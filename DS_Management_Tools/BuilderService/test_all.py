import copy
import json
import time

from conf import __conf__
import DymolaBuilder as dbe


def test_build():
    import logging
    logging.basicConfig(level=logging.DEBUG)
    dbuilder = dbe.DymolaBuilder(instances=4)
    tasks = get_all_build_task()
    for task in tasks:
        dbuilder.add_task(task)
    time.sleep(150)
    for task in tasks:
        print task
    dbuilder.stop()
    assert 0


def load_task_json(filename):
    with open(filename) as f_handle:
        task = json.load(f_handle)
    return task


def get_all_build_task():
    filenames = ['mock_task1.json', 'mock_task2.json',
                 'mock_task3.json', 'mock_task4.json', ]
    tasks = []
    for filename in filenames:
        task = load_task_json(filename)
        building_info = copy.deepcopy(task.get('buildingInfo', {}))
        modelname = task['parameterOfFunction']['testArguments']['modelName']
        build_task = {'name': modelname, 'value': building_info}
        tasks.append(build_task)
    return tasks


def test_dymola():
    post_server(builder_type='dymola')


def test_dummy():
    post_server(builder_type='dummy')


def post_server(builder_type):
    import requests
    build_task1 = get_all_build_task()[0]
    server_url = "http://" + __conf__['buildSetting']['host'] + \
        ":" + str(__conf__['buildSetting']['port'])
    add_task_url = server_url + "/{0}/models".format(builder_type)
    print json.dumps(build_task1, indent=2)
    post_task_response = requests.post(add_task_url, data=json.dumps(build_task1))
    print post_task_response
    post_task_return_data = post_task_response.json()
    print json.dumps(post_task_return_data, indent=2)
    get_response = requests.get(url=post_task_return_data[0]['location'])
    while get_response.json()['result'] == '':
        time.sleep(0.2)
        get_response = requests.get(url=post_task_return_data[0]['location'])
    print json.dumps(get_response.json(), indent=2)
    assert (".zip" in get_response.json()['result'])

if __name__ == "__main__":

    test_dummy()
