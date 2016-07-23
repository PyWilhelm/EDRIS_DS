#!/usr/bin/env python
# -*- coding: utf-8 -*-


from flask import jsonify, request, Response
import os
import json
from edris_server import conf, app, dbm
from edris_server.UrlFormat import UrlFormat


@app.route('/upload/<path:filename>', methods=['POST'])
@app.requires_auth
def dependencies(filename):
    data = request.data
    path = os.path.join(conf.schedule_conf['dependPath'], *(filename.split('/')))
    dirpath = os.path.dirname(path)
    if os.path.exists(dirpath) == False:
        os.makedirs(dirpath)
    with open(path, 'wb') as f:
        f.write(data.decode('base64'))
    return Response(status=201)


@app.route('/tasks', methods=['PUT', 'GET', 'POST', 'DELETE'])
@app.requires_auth
def submit():
    if request.method == 'PUT':
        no_cache = bool(request.headers.get('no-cache'))
        max_age = int(request.headers.get('max-age'))  # in seconds
        priority = request.headers.get('priority', 1)
        content = request.data
        task_list = json.loads(content)
        locations = []
        tids = []
        for task in task_list:
            task_id = None
            try:
                task_id = dbm.TaskManager.insert_new_task(task, priority=priority,
                                                          no_cache=no_cache, max_age=max_age)
                locations.append(UrlFormat.create_task_location(task_id))
            except Exception:
                pass
            finally:
                tids.append(task_id)
        app.message_queue.clearup_waiting_tasks(priority)
        return jsonify(locations=locations)
    elif request.method == 'POST':
        try:
            query = json.loads(request.data)
            print query
            results = {}
            for task_loc in query:
                tid = UrlFormat.get_tid_from_location(task_loc)
                status = dbm.TaskManager.check_status_by_tid(tid)
                if status in ['FINISHED', 'FAILED']:
                    item = {'status': status, 'location': UrlFormat.create_result_location(tid)}
                else:
                    item = {'status': status}
                results[task_loc] = item
        except:
            return Response(status=404)
        return Response(json.dumps(results, indent=2))
    elif request.method == 'DELETE':
        pass


@app.route('/tasks/<tid>', methods=['GET'])
@app.requires_auth
def check_single_result(tid):
    status = dbm.TaskManager.check_status_by_tid(tid)
    if status in ['FINISHED', 'FAILED']:
        return Response(json.dumps({'status': status,
                                    'location': UrlFormat.create_result_location(tid)}))
    else:
        return Response(json.dumps({'status': status}))


@app.route('/results', methods=['POST'])
@app.requires_auth
def get_results():
    locations = json.loads(request.data)
    result_dict = {}
    for loc in locations:
        tid = UrlFormat.get_tid_from_location(loc)
        result_dict[loc] = dbm.TaskManager.get_result_bt_tid(tid)
    return Response(json.dumps(result_dict, indent=2))


@app.route('/results/<tid>', methods=['GET'])
@app.requires_auth
def get_result(tid):
    result = dbm.TaskManager.get_result_bt_tid(tid)
    if result is None:
        return Response(status=404)
    return Response(json.dumps(result, indent=2))


@app.route('/monitor')
@app.requires_auth
def monitor():
    monitor_tasks = dbm.TaskManager.get_scheduler_info()
    monitor_workers = dbm.WorkerManager.get_workers()

    result = {'task': {'pending': monitor_tasks[0], 'processing': monitor_tasks[1]},
              'workers': monitor_workers}
    return Response(json.dumps(result, indent=2))


@app.route('/put-signal', methods=['GET'])
def put_signal():
    app.message = 'kill worker'
    return jsonify(message='ok')


@app.route('/get-tasks-info')
def get_tasks_info():
    # string = json.dumps(dbm.TaskManager.get_all_tasks_info(), indent=2)
    string = '{}'
    return Response(string, 200)


@app.route('/get-workers-info')
def get_workers_info():
    string = json.dumps(dbm.TaskManager.get_all_worker_tempo(), indent=2)
    return Response(string, 200)


@app.route('/shutdown')
def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    return 'Server shutting down...'
