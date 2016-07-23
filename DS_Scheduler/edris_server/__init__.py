#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask, request, Response
from flask.ext.compress import Compress
import os
import threading
import subprocess
import logging
import time
import traceback
import gzip
import StringIO
from conf import conf
from functools import wraps
from edris_server import clearup, Watcher
from edris_server.mq import message_queue
from edris_server.Watcher import monitor_worker
from multiprocessing import Process, Lock, Array


class MyFlask(Flask):

    def __init__(self, import_name, message_queue=None, **options):
        logging.basicConfig(level=logging.ERROR)
        clearup.clearup()
        self.message_queue = message_queue
        self.message = None
        Flask.__init__(self, import_name, **options)

    def check_auth(self, username, password):
        """This function is called to check if a username /
        password combination is valid.
        """
        return username == conf.security_conf['username'] \
            and password == conf.security_conf['password']

    def authenticate(self):
        """Sends a 401 response that enables basic auth"""
        return Response(
            'Could not verify your access level for that URL.\n'
            'You have to login with proper credentials', 401,
            {'WWW-Authenticate': 'Basic realm="Login Required"'})

    def requires_auth(self, f):
        @wraps(f)
        def decorated(*args, **kwargs):
            auth = request.authorization
            if not auth or not self.check_auth(auth.username, auth.password):
                return self.authenticate()
            return f(*args, **kwargs)
        return decorated

    def run(self):
        logging.info('server run')
        self.message_queue.start()
        thread3 = threading.Thread(target=monitor_worker)
        thread3.daemon = True
        thread3.start()
        Flask.run(self,
                  host=conf.server_conf['host'],
                  port=conf.server_conf['port'],
                  threaded=True,
                  debug=True,
                  ssl_context=(conf.server_conf['certfile'],
                               conf.server_conf['keyfile']) if conf.server_conf['https'] else None
                  )

compress = Compress()
app = MyFlask(__name__, message_queue)
compress.init_app(app)
app.config.setdefault('COMPRESS_MIN_SIZE', 100)
# app.config.setdefault('COMPRESS_LEVEL', 9)


@app.before_request
def before_request():
    '''decompress content if Content-Encoding is gzip
    '''
    if request.headers.get('Content-Encoding') == 'gzip':
        buf = StringIO.StringIO(request.data)
        f = gzip.GzipFile(fileobj=buf)
        request.data = f.read()


import views_controller
import views_worker
