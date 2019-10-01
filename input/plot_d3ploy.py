"""
This file produces the plots for one scenario.
The plots are produced for only one calculation method.
This is not useful to compare different calculation methods
but to see the outputs of only one simulation.
"""

import json
import re
import subprocess
import os
import sqlite3 as lite
import copy
import glob
import sys
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import d3ploy.tester as tester
import d3ploy.plotter as plotter
import collections

direc = os.listdir('./')

# Delete previously generated files
# hit_list = glob.glob('*.png') + glob.glob('*.csv')
# for file in hit_list:
#     os.remove(file)

ENV = dict(os.environ)
ENV['PYTHONPATH'] = ".:" + ENV.get('PYTHONPATH', '')

# initialize metric dict
output_file = "cyclus.sqlite"

demand_eq = '50 - 0.1 * t'

# Initialize dicts
metric_dict = {}
all_dict = {}
agent_entry_dict = {}

# get agent deployment
commod_dict = {'fuel': ['source'],
               'POWER': ['reactor1', 'reactor2'],
               'spent': ['Sink']}

for commod, facility in commod_dict.items():
    agent_entry_dict[commod] = tester.get_agent_dict(output_file, facility)

all_dict['POWER'] = tester.supply_demand_dict_driving(
    output_file, demand_eq, 'POWER')

plotter.plot_demand_supply_agent(all_dict['POWER'], agent_entry_dict['POWER'],
                                 'POWER', '0-power',
                                 True, True, False, 1)

front_commods = ['fuel']
back_commods = ['spent']

for commod in front_commods:
    all_dict[commod] = tester.supply_demand_dict_nondriving(output_file,
                                                            commod, True)
    name = '0-' + commod
    plotter.plot_demand_supply_agent(all_dict[commod],
                                     agent_entry_dict[commod], commod, 'test1',
                                     True, True, False, 1)

for commod in back_commods:
    all_dict[commod] = tester.supply_demand_dict_nondriving(output_file,
                                                            commod, False)

    name = '0-' + commod
    plotter.plot_demand_supply_agent(all_dict[commod],
                                     agent_entry_dict[commod],
                                     commod, 'test2', False, True, False, 1)