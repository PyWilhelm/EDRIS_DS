#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import sys
import os


__conf_file__ = 'conf.json'


class Conf(object):

    def __init__(self):
        local_config = 'conf_local.json'
        default_config = 'conf.json'
        if os.path.exists(local_config):
            __conf_file__ = local_config
        else:
            __conf_file__ = default_config
        with open(__conf_file__, 'r') as f:
            self.__json = json.load(f)
            for key in self.__json:
                # FIXME: change to dict
                setattr(Conf, key, self.__json[key])
        self.dependencies = {}
        # Jenkins mode
        if len(sys.argv) > 1:
            if sys.argv[1] == 'jenkins':
                self.webserivce_port += 1
                # self.webserivce_host = socket.gethostbyaddr('localhost')[0]
                if os.path.exists('jenkins') == False:
                    os.makedirs('jenkins')
                os.chdir('jenkins')
                print('Jenkins Mode')
configuration = Conf()


def get_configuration():
    return configuration
