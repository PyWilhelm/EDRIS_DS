import asyncio as aio
import aiohttp
import time
import traceback
import json
import os
import hashlib
import shutil
import subprocess
import sys
import functools
from edris_worker import network
from functools import partial
from aiohttp.websocket import Message
from edris_worker.hv import HashValue
from cgi import log
from edris_worker.Conf import get_configuration
conf = get_configuration()


wid = None
loop = None

total = 0
number = -4
MAX_PARALLEL_TASKS = int(get_configuration().thread)


@aio.coroutine
def enter_heartbeat(semaphore):
    _ = aio.Task(heartbeat_loop(semaphore))


@aio.coroutine
def heartbeat_loop(semaphore):
    global wid
    while True:
        response_json = yield from network.heartbeat2server(wid,
                                                            MAX_PARALLEL_TASKS)
        wid = response_json.get('wid')
        yield from aio.sleep(5.0)


@aio.coroutine
def enter_execute_job(semaphore, thread_safe_lock):
    while wid is None:
        yield from aio.sleep(0.1)
    _ = aio.Task(execute_job_loop(semaphore, thread_safe_lock))


@aio.coroutine
def execute_job_loop(semaphore, thread_safe_lock):
    global wid

    def release(task=None):
        semaphore.release()

    while True:
        yield from semaphore
        try:
            tid, message = yield from network.get_new_job(wid)
        except Exception as e:
            print('[execute_job_loop]', e)
            tid = 'no_connection'
        print(tid)
        if tid == 'server_message' or tid == 'no_connection':
            yield from aio.sleep(2)
            release()
        else:
            task = aio.Task(run_execute_chain(semaphore, tid, message, thread_safe_lock))
            task.add_done_callback(release)


@aio.coroutine
def run_execute_chain(semaphore, tid, job, thread_safe_lock):
    global wid, number, total
    try:
        md5_path = yield from get_dependency(job, thread_safe_lock)
        result, log = yield from execute_script(job, job['meta_function'], md5_path)
        result = result[0:result.rfind('}') + 1]
        print('result', result)
        print('log:', log)
        try:
            yield from network.acknowledge_job(wid, tid, result, log)
        except:
            yield from network.fail_job(wid, tid, result, log)
    except Exception as e:
        print('[run_execute_chain]', traceback.format_exc())
        try:
            yield from network.fail_job(wid, tid, '',
                                        {'id': tid, 'log': {'message': traceback.format_exc(),
                                                            'type': 'Error outside Execution'}})
        except Exception as e:
            print(e)
    return


@aio.coroutine
def get_dependency(job, thread_safe_lock):
    @aio.coroutine
    def download_and_copy(source_path, filename):
        yield from thread_safe_lock
        res = yield from network.check_download_file(filename, not os.path.exists(source_path))
        if not res:
            print('Download file Error!', filename)
            raise Exception('Download file Error! ' + filename)
        yield from safe_copy(source_path,
                             os.path.join(direction_path, os.path.basename(filename)))
        thread_safe_lock.release()
    try:
        direction_path = os.path.join('working', HashValue.new(str(job)) + str(int(time.time())))
        yield from make_dir(direction_path)
        dependency_files = [job['meta_function']] + job['dependency']
        for filename in dependency_files:
            hv = HashValue.new(filename.replace(os.sep, '/'))
            source_path = os.path.join('dependency',
                                       hv + '.' + filename.split('.')[-1])
            print(filename, source_path)
            yield from download_and_copy(source_path, filename)
        return direction_path
    except Exception as e:
        traceback.print_exc()
        yield from remove_dir(direction_path)
        raise e


@aio.coroutine
def remove_dir(direction_path):
    shutil.rmtree(direction_path)


@aio.coroutine
def make_dir(direction_path):
    os.makedirs(direction_path)


@aio.coroutine
def safe_copy(source, destination):
    shutil.copyfile(source, destination)
    sum_source = yield from md5sum(source)
    while (sum_source != (yield from md5sum(destination))):
        yield from aio.sleep(0.02)
    return True


@aio.coroutine
def md5sum(filename):
    while True:
        try:
            with open(filename, mode='rb') as f:
                d = hashlib.md5()
                [d.update(buf) for buf in iter(partial(f.read, 128), b'')]
            return d.hexdigest()
        except:
            yield from aio.sleep(0.02)


@aio.coroutine
def execute_script(job, job_name, md5_path):
    class DateProtocol(aio.SubprocessProtocol):

        def __init__(self, exit_future):
            self.exit_future = exit_future
            self.output = bytearray()
            self.error = bytearray()

        def pipe_data_received(self, fd, data):
            if fd == 1:
                self.output.extend(data)
            elif fd == 2:
                self.error.extend(data)

        def process_exited(self):
            self.exit_future.set_result(True)
    try:
        abs_path = os.path.abspath(md5_path)
        print(abs_path, os.listdir(md5_path))
        script_abs_path = os.path.join(abs_path, os.path.basename(job_name))
        exit_future = aio.Future(loop=loop)
        if script_abs_path.find('.py') >= 0:
            create = loop.subprocess_exec(
                lambda: DateProtocol(exit_future), sys.executable,
                script_abs_path, abs_path,
                json.dumps(job['parameterOfFunction']),
                stdin=None, cwd=abs_path)
        if script_abs_path.find('.exe') >= 0:
            create = loop.subprocess_exec(
                lambda: DateProtocol(exit_future), script_abs_path,
                os.path.abspath('lib'), abs_path,
                json.dumps(job['parameterOfFunction']),
                stdin=None)
        transport, protocol = yield from create
        yield from exit_future
        transport.close()
        data_stdout = bytes(protocol.output).decode('ascii').rstrip()
        data_stderr = bytes(protocol.error).decode('ascii').rstrip()
    except Exception as e:
        raise e
    finally:
        yield from remove_dir(abs_path)
    return data_stdout, data_stderr


def initial_fs():
    if not os.path.exists('dependency'):
        os.mkdir('dependency')
    [os.remove(os.path.join('dependency', path))
     for path in os.listdir('dependency')]
    if not os.path.exists('working'):
        os.mkdir('working')
    ls = os.listdir('working')
    for subdir in ls:
        shutil.rmtree(os.path.join('working', subdir))


def main():
    global loop
    initial_fs()
    loop = aio.ProactorEventLoop()
    aio.set_event_loop(loop)
    # print (aio.get_event_loop_policy())
    # loop = aio.get_event_loop()
    semaphore = aio.Semaphore(MAX_PARALLEL_TASKS, loop=loop)
    thread_safe_lock = aio.Semaphore(1, loop=loop)
    aio.async(enter_execute_job(semaphore, thread_safe_lock))
    aio.async(enter_heartbeat(semaphore))
    loop.run_forever()
