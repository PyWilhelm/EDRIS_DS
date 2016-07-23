#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import jsonify, request, Response, send_file
import os
import json
import logging
import shutil
import socket
import time
from edris_server import conf, app, dbm


@app.route('/workers', methods=['GET'])
@app.requires_auth
def worker():
    thread_number = request.args.get('thnr')
    clientname = socket.gethostbyaddr(request.remote_addr)[0]
    wid = dbm.WorkerManager.get_new_worker_id(thread_number, clientname)
    return jsonify(wid=wid, message=None)


@app.route('/workers/<wid>', methods=['GET'])
@app.requires_auth
def messages(wid):
    def get_current_msg(wid):
        if app.message:
            msg = app.message
            app.message = None
            return jsonify(wid=wid, message=msg)
        return jsonify(wid=wid, message=None)
    thread_number = request.args.get('thnr')
    clientname = socket.gethostbyaddr(request.remote_addr)[0]
    wid = dbm.WorkerManager.worker_update(wid, thread_number, clientname)
    return get_current_msg(wid)


# worker API
@app.route('/workers/<wid>/tasks', methods=['GET'])
@app.requires_auth
def get_task(wid):
    try:
        task = app.message_queue.get_task(wid)
    except:
        return Response(status=404)
    result = task['message']
    headers = {'taskId': task.get(u'tid')}
    return Response(json.dumps(result, indent=2),
                    headers=headers,
                    mimetype='application/json')

# worker API


@app.route('/workers/<wid>/tasks/<tid>', methods=['POST'])
@app.requires_auth
def post_acknowledgement(wid, tid):
    successful = request.headers.get('successful')
    content = json.loads(request.data)
    log = content['log']
    result_body = content['result']
    if successful == 'True':
        app.message_queue.acknowledge(wid, tid, result_body, log)
    elif successful == 'False':
        logging.error(tid + '\n' + str(log))
        app.message_queue.fail_by_tid(wid, tid, result_body, log)
    return Response(status=204)


@app.route('/download/<path:name>', methods=['GET'])
@app.requires_auth
def get_file(name):
    def get_file_info(name):
        name = name.split('/')
        path = os.path.join(conf.schedule_conf['dependPath'], *name)
        if os.path.exists(path) == False:
            return -1
        return os.path.getmtime(path)
    last_download = float(request.headers.get('last_download', 0))
    invalid = bool(request.headers.get('invalid', False))
    last_modified = get_file_info(name)
    if last_modified == -1:
        logging.error('Dependency ERROR: ' + name + ' is not existed!')
        return Response(status=404)
    if (not invalid) and last_download is not None and last_modified <= last_download:
        return Response(status=204)
    name = name.split('/')
    path = os.path.join(conf.schedule_conf['dependPath'], *name)
    response = send_file(path, mimetype='application/octet-stream', attachment_filename=os.path.basename(path))
    response.headers['last_download'] = str(time.time())
    return response


@app.route('/', methods=['GET'])
@app.route('/worker.zip', methods=['GET'])
def get_worker_zip():
    create_zip_file()
    path = os.path.join(conf.schedule_conf['dependPath'], 'EDRIS_Worker.zip')
    return send_file(path, mimetype='application/octet-stream', as_attachment=True,
                     attachment_filename='EDRIS_Worker.zip')


def create_zip_file():
    shutil.make_archive(os.path.join(conf.schedule_conf['dependPath'], 'EDRIS_Worker'),
                        format='zip', root_dir='../EDRIS_Worker', base_dir='../EDRIS_Worker')


@app.route('/test')
def test_func():
    return 'testaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
