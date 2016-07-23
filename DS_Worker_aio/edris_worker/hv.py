#!/usr/bin/env python
# -*- coding: utf-8 -*-
import hashlib


class HashValue(object):

    @staticmethod
    def new(string):
        s1 = hashlib.md5(string.encode('utf-8')).hexdigest()
        # s2 = hashlib.sha1(string).hexdigest()
        return s1
