import hashlib
import json
import os
import urllib


from DymolaBuilder import DymolaBuilder, BaseBuilder, DummyDymolaBuilder, get_building_info
from conf import __conf__
from flask import Flask, request, send_from_directory, url_for, Response
from functools import wraps


def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return username == __conf__['buildSetting']['username'] \
        and password == __conf__['buildSetting']['password']


def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated


app = Flask('Builder')
future_queue = dict(dymola=dict(), dummy=dict())


def hash_value(obj):
    content = json.dumps(obj)
    return hashlib.sha224(content).hexdigest()

try:
    dymola_builder = DymolaBuilder(instances=5)
except Exception as err:
    dymola_builder = BaseBuilder()
    print err

dummy_dymola_builder = DummyDymolaBuilder()


def get_builder(builder_type):
    if builder_type == 'dymola':
        builder = dymola_builder
    elif builder_type == 'dummy':
        builder = dummy_dymola_builder
    else:
        raise Exception('unknown builder type: ' + builder_type)
    return builder


@app.route('/<builder_type>/models', methods=['POST'])
@requires_auth
def add_build_tasks(builder_type):
    global future_queue
    no_cache = request.headers.get('no-cache')
    data = json.loads(request.data)
    models = [data] if isinstance(data, dict) else data
    models = [get_building_info(m['name'], m['value']) for m in models]
    if future_queue.get(builder_type) is None:
        future_queue[builder_type] = dict()
    for model in models:
        key = hash_value(model)
        builder = get_builder(builder_type)
        print "putting key", key
        future_queue[builder_type][key] = builder.add_task(key, model,
                                                           no_cache=no_cache)
    moids = [hash_value(model) for model in models]
    get_url_location = lambda mid: url_for('get_models', builder_type=builder_type,
                                           mid=mid, _external=True)
    resp = [{"id": moid, "location": get_url_location(moid)} for moid in moids]
    return json.dumps(resp), 201


@app.route('/<builder_type>/models/<mid>', methods=['GET'])
@requires_auth
def get_models(builder_type, mid):
    if mid is not None:
        key = mid
        result, status_code = get_result(builder_type, key)
        return json.dumps(result), status_code


def get_result(builder_type, key):
    global future_queue
    if future_queue[builder_type].get(key) is not None:
        url = build_url(future_queue[builder_type][key])
        status_code_pending = 203
        if url == "":
            return dict(result=url, log=""), status_code_pending
        else:
            status_code_success = 200
            whole_result = future_queue[builder_type][key].get()

            return dict(result=url, log=whole_result['log']), status_code_success
    else:
        status_code_not_found = 404
        return json.dumps({}), status_code_not_found


def build_url(future):
    whole_result = future.get()
    if whole_result is None:
        return ""
    else:
        destination = whole_result['result']
        relpath = os.path.relpath(
            destination, __conf__['buildSetting']['path'])
        relurl = urllib.pathname2url(relpath)
        return url_for('downloads', filepath=relurl, _external=True)


@app.route('/downloads/<path:filepath>', methods=['GET'])
@requires_auth
def downloads(filepath):
    filename = os.path.basename(filepath)
    uploads = os.path.join(
        __conf__['buildSetting']['path'], os.path.dirname(filepath))
    return send_from_directory(directory=uploads, filename=filename)


if __name__ == "__main__":
    print "after main"
    import logging
    logging.basicConfig(level=logging.DEBUG)
    app.run(host=__conf__['buildSetting']['host'], port=__conf__['buildSetting']['port'],
            threaded=True, debug=False,
            ssl_context=(__conf__['buildSetting']['certfile'],
                         __conf__['buildSetting']['keyfile'])
            if __conf__['buildingSetting']['https'] else None)
