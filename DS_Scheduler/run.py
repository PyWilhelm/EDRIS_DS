#!/usr/bin/env python
# -*- coding: utf-8 -*-
from edris_server.Watcher import monitor_worker
import os
import edris_server
import threading
from flask import request
def load_rest():
    edris_server.app.run()

if __name__ == '__main__':
    load_rest()
    print 'shutdown'