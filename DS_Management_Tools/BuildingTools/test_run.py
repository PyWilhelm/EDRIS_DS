#!/usr/bin/env python
# -*- coding: utf-8 -*-
from BuildingTools.ScriptGenerator.SpecificBase import SpecificBase
from BuildingTools.ScriptGenerator import edrisRules
from BuildingTools import ScriptGenerator
import yaml


with open('info.yaml') as f:
    rules = edrisRules.Rules(yaml.safe_load(f.read()))
    rules.generate_rule_script()

with open('spec.yaml') as f:
    spec = SpecificBase(rules, yaml.safe_load(f.read()))
with open('info1.yaml', 'w') as f:
    yaml.safe_dump(spec.generate_specific_script_metatask_format(), f, default_flow_style=False)
'''with open('info1.yaml') as f:
    m = ScriptGenerator.ModelSDS(yaml.safe_load(f.read()))
    print m.generate_model_script()
'''