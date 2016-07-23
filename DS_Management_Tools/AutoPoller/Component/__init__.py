#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json, unittest

from AutoPoller.Component.ComponentWatcher import ComponentWatcher


def main():
    '''generate FMU files of the components which are newly added in database. 
        input:    data in database and filesystem (.fmu files exist?)
        output:   .fmu files stored in component folders
                  or Exception if failed/invalid
    
        todo:     svn commit
        
        two method to call this function
        1. call by frontend.
        2. call by jenkins (Periodic)
        if component is invalid, raise Exception.
        _FMUBuilder.py 
            only use constant ComponentType-ModelName Mapping. can be rewritten into a conf (.json) file
            ComponentType determined by the number of base folder. e.g. 02: Battery
        
            
    '''
    logging_dict = ComponentWatcher().build_fmu()
    if len(logging_dict.keys()) > 0:
        raise Exception(json.dumps(logging_dict, indent=2))    
    
class Test(unittest.TestCase):
    def test_main(self):
        main()
