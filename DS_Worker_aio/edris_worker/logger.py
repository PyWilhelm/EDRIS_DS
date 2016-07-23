#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging


class logger():

    def __init__(self):
        pass

    @staticmethod
    def add_subprocess_log(task_tuple, sub_dict):
        logging.info(str(task_tuple[1]))
        logging.info(str(sub_dict))
        return {'id': task_tuple[0], 'log': sub_dict}, \
            True if len(sub_dict['simulateErr']) > 0 or len(sub_dict['resultErr']) > 0 else False
