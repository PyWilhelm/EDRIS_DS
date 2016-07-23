'''
Created on 07.10.2014

@author: qxg2705
'''
import unittest, test, conf, sys
if __name__ == '__main__':
    if len(sys.argv) == 3:
        conf.__conf__['webSetting']['port'] = sys.argv[1]
        conf.__conf__['databaseSetting']['dbmsHost'] = sys.argv[2]
    unittest.main(test)