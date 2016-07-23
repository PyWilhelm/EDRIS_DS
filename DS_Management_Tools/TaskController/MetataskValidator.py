'''
Created on 02.09.2014

@author: qxg2705
'''
import unittest
import json
import traceback
import types
from jsonschema import validate as va


class MetataskValidator(object):

    @staticmethod
    def validate(json_file_or_dict, schema_file='db/schema/schema_one.json'):
        if isinstance(json_file_or_dict, types.DictType):
            data = json_file_or_dict
        else:
            with open(json_file_or_dict) as f:
                data = json.load(f)
        with open(schema_file) as f:
            schema = json.load(f)
        try:
            va(data, schema)
        except:
            print traceback.format_exc()
        if data['classes']['taskGenerator'].find('SimpleVariationTG') >= 0:
            try:
                MetataskValidator.__validate_simplevariation(data)
            except:
                print traceback.format_exc()

    @staticmethod
    def __validate_simplevariation(data):
        variables = data['taskGenerator']['arguments']['variable']
        for var in variables:
            length = [len(var['value']) for var in variables]
            if min(length) != max(length):
                raise Exception('Variables in Simple Variation must be at same length')


class Test(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # fname = raw_input('json file: ')
        fname = 'metatask.json'
        with open('../' + fname) as f:
            cls.data = json.load(f)
        with open('schema_one.json') as f:
            cls.schema_main = json.load(f)
        with open('schema_building.json') as f:
            cls.schema_building = json.load(f)
        with open('schema_classes.json') as f:
            cls.schema_classes = json.load(f)
        with open('schema_buildingInfo.json') as f:
            cls.schema_buildingInfo = json.load(f)
        with open('schema_constant.json') as f:
            cls.schema_constant = json.load(f)
        with open('schema_variable.json') as f:
            cls.schema_variable = json.load(f)

    def test_schema(self):
        # va(self.data, self.schema_main)
        MetataskValidator.validate('../metatask_BBVData.json', 'schema_one.json')

    '''    def test_building(self):
            va(self.data['building'], self.schema_building)

        def test_classes(self):
            va(self.data['classes'], self.schema_classes)

        def test_variable(self):
            va(self.data['taskGenerator']['arguments']['variable'], self.schema_variable)

        def test_constant(self):
            va(self.data['taskGenerator']['arguments']['constant'], self.schema_constant)

        def test_buildingInfo(self):
            va(self.data['taskGenerator']['arguments']['constant']['buildingInfo'], self.schema_buildingInfo)'''


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.test_schema']
    unittest.main()
