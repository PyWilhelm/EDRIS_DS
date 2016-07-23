#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
import os
import logging
import subprocess
import httplib
import time
import json


from conf import __conf__

gfl = lambda path: {'data': []} if path == '' \
    else {'data': [[f] for f in os.listdir(os.path.join(__conf__['edrisBasePath'], path)) if f.find('.mat') >= 0]}


class Test(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        reset_conf()
        start_mongodb()
        time.sleep(10)
        start_scheduler()
        start_worker()

    @classmethod
    def tearDownClass(cls):
        shutdown_worker()
        shutdown_scheduler()
        with open('globalinfo.json', 'w') as f:
            json.dump({'pid': []}, f)
        shutdown_mongodb()

    def setUp(self):
        from TaskController.BaseClass.Controller import Controller
        self.controller = Controller()

    def tearDown(self):
        self.controller.stop(all_stop=True)

    def test_system_SPS_simulation(self):
        import TaskController.SPS
        print '-----------------\ntest_system_SPS_simulation'
        modelname = 'EdrisLibComponents.SystemBases.SystemsBases.BasesSPS.TB_separated_SPS_base'
        n_max = '1000'
        n_eck = '500'
        setNcAgingFactor = '0.7'
        setRiAgingFactor = '1.3'
        battery = r'EDRIS_database\ComponentData\02_ElectricEnergyStorageSystem\02_ComponentData\50_Gen5\01_PHEV1_85mm_UHE\01_Gen5_20140717_PHEV1_85mm_UHE_88s3p'
        emachine = r'EDRIS_database\ComponentData\04_EM\02_ComponentData\example'
        userinput = {'modelName': modelname,
                     'n_max': n_max, 'n_eck': n_eck,
                     'setNcAgingFactor': setNcAgingFactor,
                     'setRiAgingFactor': setRiAgingFactor,
                     'build': {'Battery_01': gfl(battery), 'ElectricMachine_01': gfl(emachine)}}
        result_future = TaskController.SPS.start_controller('__test__', userinput, controller=self.controller,
                                                            block=False, method='System', sample=True)
        result_filename = result_future.get()
        print result_filename
        print self.controller.check_progress()

    def test_charging_simulation(self):
        import TaskController.Charging
        print '-----------------\ntest_charging_simulation'
        battery = r'EDRIS_database\ComponentData\02_ElectricEnergyStorageSystem\02_ComponentData\50_Gen5\01_PHEV1_85mm_UHE\01_Gen5_20140717_PHEV1_85mm_UHE_88s3p'
        dcdc = r''
        charger1 = r'EDRIS_database\ComponentData\06_Charger\02_ComponentData\BMW_LE125\10_parameterSets'
        charger2 = r''
        userinput = {'build': {}}
        userinput['build'] = {'Battery_01': gfl(battery), 'DCDCConverter_01': gfl(dcdc),
                              'Charger_01': gfl(charger1), 'Charger_02': gfl(charger2)}
        result_future = TaskController.Charging.start_controller(
            None, userinput, controller=self.controller, block=False, sample=True)
        result_filename = result_future.get()
        print result_filename
        print self.controller.check_progress()

    def test_BBVAP_simulation(self):
        import TaskController.BBVAP
        print '-----------------\ntest_BBVAP_simulation'
        componentname = r'EDRIS_database\ComponentData\02_ElectricEnergyStorageSystem\02_ComponentData\50_Gen5\01_PHEV1_85mm_UHE\01_Gen5_20140717_PHEV1_85mm_UHE_88s3p'
        setNcAgingFactor = '0.7'
        setRiAgingFactor = '1.3'
        userinput = {'Battery': gfl(componentname),
                     'setNcAgingFactor': setNcAgingFactor, 'setRiAgingFactor': setRiAgingFactor, 'componentname': componentname}
        result = TaskController.BBVAP.start_controller('__test__', userinput, controller=self.controller)
        print result
        print self.controller.check_progress()

    def test_battery_SPS_plot(self):
        import TaskController.SPS
        print '-----------------\ntest_battery_SPS_plot'
        componentname = r'EDRIS_database\ComponentData\02_ElectricEnergyStorageSystem\02_ComponentData\50_Gen5\01_PHEV1_85mm_UHE\01_Gen5_20140717_PHEV1_85mm_UHE_88s3p'
        setRci = u'0.1:0.3:1'
        setTemp = u'0:10:30'
        StopTime = u'200'
        userinput = {'componentname': componentname,
                     'setRci': setRci,
                     'setTemp': setTemp,
                     'StopTime': StopTime,
                     'build': {'Battery': gfl(componentname)}}
        result_future = TaskController.SPS.start_controller(
            '__test__', userinput, block=False, controller=self.controller, method='BatteryPlot')
        result_filename = result_future.get()
        print result_filename
        print self.controller.check_progress()

    def test_system_SPS_Plot(self):
        import TaskController.SPS
        print '-----------------\ntest_system_SPS_Plot'
        setRci = '0.1:0.1:1'
        setTemp = '0:5:30'
        StopTime = '200'
        setSpeed = '5000'
        SOH = '0'
        battery = r'EDRIS_database\ComponentData\02_ElectricEnergyStorageSystem\02_ComponentData\50_Gen5\01_PHEV1_85mm_UHE\01_Gen5_20140717_PHEV1_85mm_UHE_88s3p'
        emachine = r'EDRIS_database\ComponentData\04_EM\02_ComponentData\example'
        setNcAgingFactor = '0.7'
        setRiAgingFactor = '1.3'
        userinput = {'BatteryComponentName': battery,
                     'ElectricMachineComponentName': emachine,
                     'setRci': setRci,
                     'setTemp': setTemp,
                     'StopTime': StopTime,
                     'setSpeed': setSpeed,
                     'SOH': SOH,
                     'setNcAgingFactor': setNcAgingFactor,
                     'setRiAgingFactor': setRiAgingFactor,
                     'build': {'Battery_01': gfl(battery), 'ElectricMachine_01': gfl(emachine)}}
        result_future = TaskController.SPS.start_controller(
            '__test__', userinput, controller=self.controller, block=False, method='SystemPlot')
        result_filename = result_future.get()
        print result_filename
        print self.controller.check_progress()


def reset_conf():
    __conf__['edrisComponentsPath'] = '..'
    __conf__['libraryPath'] = {"EdrisLibComponents": "EdrisLibComponents",
                               "EdrisLibData": "EdrisLibData",
                               "EdrisLibSystems": "EdrisLibSystems",
                               "SimDevTools": "SimDevTools"}
    port = __conf__['databaseSetting']['dbmsHost'].split(':')[-1].replace('/', '')
    __conf__['databaseSetting']['dbmsHost'] = __conf__['databaseSetting']['dbmsHost'].replace(port, str(int(port) + 1))
    __conf__['webSetting']['port'] += 1


def start_mongodb():
    if os.path.exists('..\\test_db') == False:
        os.makedirs('..\\test_db')
    lck_file = os.path.join('..\\test_db', 'mongod.lock')
    print os.path.abspath(lck_file)
    if os.path.exists(lck_file):
        os.remove(lck_file)
    port = __conf__['databaseSetting']['dbmsHost'].split(':')[-1].replace('/', '')
    subprocess.Popen([__conf__['databaseSetting']['dbmsPath'], '--dbpath', '..\\test_db', '--port', port], shell=True)


def shutdown_mongodb():
    port = __conf__['databaseSetting']['dbmsHost'].split(':')[-1].replace('/', '')
    pid = get_pid_from_port(port)
    rv = os.system('taskkill /F /PID %s' % (pid))
    time.sleep(10)


def start_scheduler():
    path = os.path.dirname(__file__)
    subprocess.Popen([os.path.join(path, 'script', 'run_scheduler_jenkins.cmd')], shell=True)


def shutdown_scheduler():
    try:
        conn = httplib.HTTPConnection(__conf__['webSetting']['host'], __conf__['webSetting']['port'])
        conn.request('GET', '/shutdown')
        data = conn.getresponse().read()
        print data
        conn.close()
    except:
        pid = get_pid_from_port(__conf__['webSetting']['port'] + 1)
        rv = os.system('taskkill /F /PID %s' % (pid))
    finally:
        time.sleep(10)


def start_worker():
    path = os.path.dirname(__file__)
    p = subprocess.Popen([os.path.join(path, 'script', 'run_worker_jenkins.cmd')], shell=True)
    return p.pid


def shutdown_worker():
    print 'shut_down_worker'
    conn = httplib.HTTPConnection(__conf__['webSetting']['host'], __conf__['webSetting']['port'])
    conn.request('GET', '/put-signal')
    data = conn.getresponse().read()
    print data
    conn.close()
    time.sleep(10)


def get_pid_from_port(port):
    print 'port', port
    a = subprocess.Popen(['netstat', '-ao'], shell=True, stdout=subprocess.PIPE)
    lines = a.stdout.readlines()
    print len(lines)
    for line in lines:
        words = line.split()
        if len(words) == 5:
            if words[1].find(':' + str(port)) > 0 and words[-1] != '0':
                return words[-1]
    return '0'
