import pymongo 
print pymongo.version
from AutoPoller.System import YamlWatcher 
from AutoPoller.BaseChecker import check_components

print check_components()

w = YamlWatcher(False, r'E:\BeSTD\03_Tools-Modelle-Methoden\AutomatisiertesTesting\09_ExchangeDirectory\testsDirectory\Projekten\FAAR\gen3_int')
w.run()

