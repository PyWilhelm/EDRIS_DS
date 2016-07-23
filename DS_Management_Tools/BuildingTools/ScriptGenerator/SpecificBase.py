#!/usr/bin/env python
# -*- coding: utf-8 -*-

import types


class SpecificBase(object):
    '''override the components type to specific name
        add more specific parameter which not generated from file names

    '''

    def __init__(self, edris_rules, specific_info=None):
        self._rules = edris_rules.generate_rule_script()
        self._specific = specific_info

    def generate_specific_script(self):
        if self._specific is None:
            return self._rules

        out = dict()
        for key in self._rules.keys():
            out[self._specific['definition'].get(key) or key] = dict()
            out[self._specific['definition'].get(key) or key][
                'child'] = self._rules[key]['child']
        out = self.__set_parameter(self._specific['parameter'], out)
        return out

    def generate_specific_script_metatask_format(self):
        if self._specific is None:
            return self._rules
        out = dict()
        for key in self._rules.keys():
            out[self._specific['definition'].get(key) or key] = dict()
            out[self._specific['definition'].get(key) or key][
                'child'] = self._rules[key]['child']
        out = self.__set_parameter(self._specific['parameter'], out)
        out2 = []
        for k in out.keys():
            child = out[k]['child']
            for kk in child.keys():
                temp = dict()
                temp['name'] = kk
                temp['link'] = "buildingInfo.%s.child" % k
                temp['build'] = True
                temp['value'] = child[kk]
                out2.append(temp)
        return out2

    def __set_parameter(self, para_dict, out):
        for key in para_dict.keys():
            if out.get(key) is None:
                out[key] = []
            if isinstance(para_dict[key], types.ListType):
                if len(out[key]) > 0:
                    for item in out[key]:
                        item.update(para_dict[key][0])
                else:
                    out[key] = para_dict[key]

            else:
                subdict = para_dict[key].get('child')
                value = para_dict[key].get('value')

                if subdict and value:
                    if out[key].get('child') is None:
                        out[key]['child'] = dict()
                    out[key]['value'] = value
                    self.__set_parameter(subdict, out[key]['child'])
                elif subdict and not value:
                    if out[key].get('child') is None:
                        out[key]['child'] = dict()
                    self.__set_parameter(subdict, out[key]['child'])
                elif value and not subdict:
                    out[key]['value'] = value
        return out
