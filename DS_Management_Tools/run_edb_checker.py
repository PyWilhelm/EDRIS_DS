'''
Created on 07.10.2014

@author: qxg2705
'''
import nose, sys

import AutoPoller.EdrisDBChecker as ec

module_name = sys.modules[ec.__name__].__file__
result = nose.run(argv=[sys.argv[0], module_name, '--with-xunit', ])

    
