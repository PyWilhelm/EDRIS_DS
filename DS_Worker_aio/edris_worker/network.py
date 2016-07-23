#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import json
import traceback
import aiohttp
import asyncio as aio
from edris_worker.Conf import get_configuration
from edris_worker.hv import HashValue
from aiohttp.helpers import BasicAuth
import dlog
import sys

logger = dlog.get_logger(__name__)

conf = get_configuration()


def factroy_url(string):
    if string[0] != '/':
        string = '/' + string

    # NOTE: now only supports https == false
    muster = 'https://{0}:{1}{2}' if conf.https else 'http://{0}:{1}{2}'
    if muster == 'https://{0}:{1}{2}':
        raise NotImplementedError('Only http protocol is supported!')
    return muster.format(conf.webserivce_host, str(conf.webserivce_port), string)

auth = lambda: BasicAuth(conf.username, conf.password)


@aio.coroutine
def heartbeat2server(wid=None, thread_number=1):
    try:
        if wid is None:
            response = yield from aiohttp.request('GET', factroy_url('/workers?thnr=%d' % thread_number),
                                                  auth=auth())
        else:
            response = yield from aiohttp.request('GET', factroy_url('/workers/%s?thnr=%d' % (wid, thread_number)),
                                                  auth=auth())
        if response.status == 200:
            res = yield from response.read()
            response_json = json.loads(res.decode('utf-8'))
            print(response_json)
            return response_json
        elif response.status == 401:
            print('Login failed.')
            sys.exit()
    except Exception:
        traceback.format_exc()
        return {}


@aio.coroutine
def get_new_job(wid):
    response = yield from aiohttp.request('GET', factroy_url('/workers/%s/tasks' % wid), auth=auth())
    if response.status == 200:
        res = yield from response.read()
        response_json = json.loads(res.decode('utf-8'))
        tid = response.headers.get('taskId')
        if tid is None:
            return 'server_message', 'no-message'
        return tid, response_json
    elif response.status == 404:
        return 'server_message', 'no-message'


@aio.coroutine
def check_download_file(filename, force=False):
    filename = filename.replace(os.sep, '/')
    filename = filename if filename[0] != '/' else filename[1:]
    hv = HashValue.new(filename)
    md5_file_path = os.path.join('dependency', hv + '.' + filename.split('.')[-1])
    print(filename, md5_file_path)
    headers = {'last_download': str(conf.dependencies.get(filename))} if not force else {'invalid': 'True'}
    response = yield from aiohttp.request('GET', factroy_url('/download/' + filename), headers=headers, auth=auth())
    if response.status == 204:
        return True
    elif response.status == 404:
        return False
    elif response.status == 200:
        with open(md5_file_path, 'wb') as fd:
            while True:
                chunk = yield from response.content.read(1024)
                if not chunk:
                    break
                fd.write(chunk)
        conf.dependencies[filename] = response.headers['last_download']
        return True


@aio.coroutine
def send_acknowledgement(wid, tid, result, fail_code, successful):
    # try:
    #    fail_code = json.dumps(fail_code, indent=2)
    #    fail_code = fail_code.rstrip()
    #    print(fail_code)
    # except:
    #    pass

    response = yield from aiohttp.request('POST',
                                          factroy_url('/workers/%s/tasks/%s' % (wid, tid)),
                                          headers={'successful': str(successful)},
                                          data=json.dumps({'result': result,
                                                           'log': fail_code}, indent=2),
                                          auth=auth())
    if response.status == 204:
        return True
    else:
        return False


@aio.coroutine
def fail_job(wid, tid, result, fail_code):
    yield from send_acknowledgement(wid, tid, result, fail_code, False)


@aio.coroutine
def acknowledge_job(wid, tid, result, log):
    yield from send_acknowledgement(wid, tid, result, log, True)
