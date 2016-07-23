#!/usr/bin/env python
# -*- coding: utf-8 -*-
import types
from BuildingTools.ScriptGenerator.edrisRules import Rules
from BuildingTools.ScriptGenerator.SpecificBase import SpecificBase
parenthesis = lambda x: '(' + x[0:-1] + '),'


class ModelSDS(object):
    '''generate script string from data structure from SpecificBase or edrisRules
    '''

    def __init__(self, building_info=None, info_data=None, spec_data=None):
        if info_data is not None:
            rules = Rules(info_data)
            spec = SpecificBase(rules, spec_data)
            self.__in = spec.generate_specific_script()
        else:
            self.__in = building_info

    def generate_model_script(self):
        script = self.__get_subscript(self.__in)
        script = self.__normalize(script)
        return script

    def __normalize(self, script):
        _ = [sub for sub in script.split(',') if sub != '']
        out = ''
        for index, sub in enumerate(_):
            if sub == ')':
                _[index - 1] += sub
                _[index] = ''
        _ = [sub for sub in _ if sub != '']
        for sub in _:
            out += sub + ', '
        return '(' + out[0:-2] + ')'

    def __get_subscript(self, d):
        out = ''
        print d
        for key in d.keys():

            subdict = d[key].get('child')
            value = d[key].get('value')
            if isinstance(value, types.BooleanType):
                value = 'true' if value else 'false'
            if (value is not None) and (subdict is None):
                if d[key].get('method') == 'redeclare':
                    out += '%s %s ' % (d[key]['method'], d[key]['type'])
                out += '%s=%s,' % (key, value)
            elif (subdict is not None) and (value is None):
                if d[key].get('method') == 'redeclare':
                    out += '%s %s ' % (d[key]['method'], d[key]['type'])
                out += '%s%s,' % (key, parenthesis(self.__get_subscript(subdict)))
            elif (subdict is not None) and (value is not None):
                if d[key].get('method') == 'redeclare':
                    out += '%s %s ' % (d[key]['method'], d[key]['type'])
                out += '%s=%s%s,' % (key, value, parenthesis(self.__get_subscript(subdict)))
            elif (subdict is None) and (value is None):
                if d[key].get('method') == 'redeclare':
                    out += '%s %s %s,' % (d[key]['method'], d[key]['type'], key)

        return out

    def __variable(self, item):
        return True if item.get('value') and not item.get('method') else False

    def __redeclare(self, item):
        return True if item.get('method') == 'redeclare' else False
