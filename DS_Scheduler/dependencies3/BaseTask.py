#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os, types, pickle, traceback, copy
import simplejson as json
from imp import reload
reload(sys)
#sys.setdefaultencoding('utf-8')
class BaseTask(object):
    def __init__(self):
        self._dir = os.getcwd()
        if len(sys.argv) >= 3:
            self._dir = sys.argv[1]
            self._parameters = json.loads(sys.argv[2])
            self._default_result = []
        self._old = os.getcwd()
    
    def get_default_result(self):
        return copy.deepcopy(self._default_result)

    def run(self):
        try:
            os.chdir(self._dir)
            self._prepare()
            result, log = self._run()
            result = json.dumps(result, indent=2, skipkeys=True)
            log = json.dumps(log, indent=2, skipkeys=True)
                
            sys.stdout.write(result)
            sys.stderr.write(log)
            os.chdir(self._old)
        except:
            log1 = json.dumps({'run-error': traceback.format_exc()}, indent=2, skipkeys=True)
            sys.stderr.write(log1)
        
    def _prepare(self):
        pass
    
    def _flatten(self, string):
        stopchars = ['\'', '"', '\n', '\r']
        for ch in stopchars:
            string = string.replace(ch, ' ')
        return string#.decode('utf-8', 'ignore')
    
    def _run(self):
        return ''

