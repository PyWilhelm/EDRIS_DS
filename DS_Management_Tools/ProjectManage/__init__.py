#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os
import socket
import threading
import time
from flask import Flask, session, redirect, request
from conf import __conf__
from flask_bootstrap import Bootstrap
from flask_appconfig import AppConfig
from flask_wtf import Form, RecaptchaField
from flask_login import LoginManager, UserMixin, login_required, login_url
import hashlib
import uuid


class User(UserMixin):
    '''User class used to create a user instance and to validate <user, password> pair

        Class Attributes:
            @var  users_db (list): initialized from "users.json" file. 
                             Each item is in format {'username': 'admin', 'password': 'pwd'}

        @param username (string)
        @param password (string)

    '''
    with open('configuration/users.json') as f:
        users_db = json.load(f)

    def __init__(self, username, password):
        self.id = username
        self.password = password

    def get_auth_token(self):
        '''get hase value of id (username)
        '''
        return hashlib.md5(self.id).hexdigest()

    @classmethod
    def get(cls, userid):
        '''
            @param userid: userid to validate
            @return: tuple (userid, password), if userid exists in database; else None

        '''
        for item in cls.users_db:
            if item['username'] == userid:
                return (item['username'], item['password'])
        return None

    @classmethod
    def get_by_hash(cls, hashvalue):
        '''
            @param hashvalue: hashvalue to validate
            @return: tuple (userid, password) if hashvalue belongs to a userid; else None
        '''
        for item in cls.users_db:
            if hashlib.md5(item['username']).hexdigest() == hashvalue:
                return (item['username'], item['password'])
        return None


class MyFlask(Flask):

    def __init__(self, import_name, **options):
        self.conf = dict()
        self.conf = __conf__
        self.results = dict()
        Flask.__init__(self, import_name, **options)

    def run(self):
        print 'server run'
        t = threading.Thread(target=self.clear_app_results)
        t.daemon = True
        t.start()
        Flask.run(self, host=__conf__['projectManageSetting']['host'],
                  port=__conf__['projectManageSetting']['port'],
                  threaded=True, debug=False,
                  ssl_context=(__conf__['projectManageSetting']['certfile'],
                               __conf__['projectManageSetting']['keyfile']))

    def clear_app_results(self):
        '''
            clear the results in cache, if the task of result was finished before 8 hours
        '''
        time_slot = 60 * 60 * 8  # 8 hours

        while True:
            del_keys = []
            for key in self.results.keys():
                if self.results[key].get('finish') == True:
                    ft = self.results[key].get('finish_time', 0)
                    print time.time(), ft
                    if time.time() - ft > time_slot:
                        del_keys.append(key)
            print del_keys
            for key in del_keys:
                del self.results[key]

            time.sleep(60)

    def get_results_from_ip(self, ip):
        hostname = socket.gethostbyaddr(ip)[0]
        return self.get_results_from_host(hostname)

    def get_results_from_host(self, hostname):
        rv = {}
        for key in self.results.keys():
            if self.results[key].get('data') == None:
                continue
            if self.results[key]['data']['clientHost'] == hostname:
                data = self.results[key]['data']
                rv[key] = data['taskName'] + ' @ ' + data['clientHost']
        return rv

    def get_all_results(self):
        rv = {}
        for key in self.results.keys():
            if self.results[key].get('data') == None:
                continue
            data = self.results[key]['data']
            rv[key] = data['taskName'] + ' @ ' + data['clientHost']
        return rv

    def get_result_from_tid(self, tid):
        return self.results.get(tid, {})


app = MyFlask(__name__)
app.config['SECRET_KEY'] = 'EDRIS'
app.config['REMEMBER_COOKIE_NAME'] = 'EDRIS_PM_KEY'
Bootstrap(app)
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.request_loader
def load_user(request):
    '''callback method required by request_loader of login_manager,
        @return: User instance initialized by given username and password, if validation is successful; else None
    '''
    username = request.form.get('login')
    password = request.form.get('password')  # naive token
    user_entry = User.get(username)
    if (user_entry is not None):
        user = User(user_entry[0], user_entry[1])
        if (user.password == password):
            session['remember'] = 'set'
            session['user_id'] = user.get_auth_token()
            return user
    return None


@login_manager.unauthorized_handler
def unauthorize_loader():
    '''callback method required by unautorized_handler of login_manager
       this method is executed, if authentication is failed or never login
        @return: redirect login page
    '''
    print('unauth')
    return redirect(login_url('login', request.url))


@login_manager.user_loader
def user_loader(user_id):
    '''callback method required by user_loader in login_manager
        @return: a User instance by given hashvalue, if hashvalue is validated successfully, else None
    '''
    if user_id is None:
        return None
    print(user_id)
    u = User.get_by_hash(user_id)
    print(u)
    if u is None:
        return None
    return User(u[0], u[1])
