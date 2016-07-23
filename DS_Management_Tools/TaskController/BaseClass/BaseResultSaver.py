#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json


class BaseResultSaver(object):

    def __init__(self, cid, metatask, successful, failed):
        self.successful = successful
        self.failed = failed
        self.cid = cid
        self.metatask = metatask

    def save(self):
        with open('fail-%s.json' % self.cid, 'w') as f:
            json.dump(self.failed, f, indent=2)
        with open('successful-%s.json' % self.cid, 'w') as f:
            json.dump(self.successful, f, indent=2)
