import random
import sys
import os
import pytest
import d3ploy.solver as solver
import d3ploy.timeseries_inst as ti


def test_parse_commodities():
    """ Tests if parse_commodities parses the input correctly """
    commodities = ['POWER_reactor_3000_1000-t',
                   'POWER_reactor2_1000_3',
                   'POWER_reactor3_600_10*t_pu_300',
                   'fuel_source_300',
                   'pu_separations_5000_0_spentuox_5000']
    commodity_dict = ti.TimeSeriesInst.parse_commodities(
        ti.TimeSeriesInst, commodities)
    answer = {'POWER': {'reactor': {'cap': 3000.0,
                                    'pref': '1000-t',
                                    'second_commod': '0',
                                    'constraint': 0},
                        'reactor2': {'cap': 1000.0,
                                     'pref': '3',
                                     'second_commod': '0',
                                     'constraint': 0},
                        'reactor3': {'cap': 600.0,
                                     'pref': '10*t',
                                     'second_commod': 'pu',
                                     'constraint': 300.0}},
              'fuel': {'source': {'cap': 300.0,
                                  'pref': '0',
                                  'second_commod': '0',
                                  'constraint': 0}},
              'pu': {'separations': {'cap': 5000.0,
                                     'pref': '0',
                                     'second_commod': 'spentuox',
                                     'constraint': 5000.0}}}
    assert commodity_dict['POWER'] == answer['POWER']
    assert commodity_dict['fuel'] == answer['fuel']
    assert commodity_dict['pu'] == answer['pu']


def test_min_deploy_solver():
    """ Tests if the minimize_number_of_deployment function works correctly
        by deploying the smallest number of facilities while meeting diff"""
    for i in range(100):
        diff = -1.0 * random.uniform(0.01, 30.0)
        commod = {}
        for i in range(4):
            commod.update({str(i): {'cap': random.uniform(0.1, 9.9),
                                    'pref': '0',
                                    'second_commod': '0',
                                    'constraint': 0}})
        deploy_dict = solver.deploy_solver(commodity_supply={},
                                           commodity_dict={'commod': commod},
                                           commod='commod',
                                           diff=diff,
                                           time=1)
        # actually deploy and see if it's good
        cap_list = [v['cap'] for k, v in commod.items()]
        final_diff = diff
        for key, val in deploy_dict.items():
            final_diff += val * commod[key]['cap']
        if final_diff > min(cap_list):
            raise ValueError(
                'The difference after deployment exceeds ' +
                'the capacity of the smallest deployable prototype')
        # if it didn't raise valueerror, we are good
        assert(True)


def test_pref_solver_const():
    """ Tests if the preference_deploy function works correctly
        for constant preference values
        by deploying only the most preferred prototype to meet diff """
    for i in range(100):
        diff = -1.0 * random.uniform(0.01, 30.0)
        commod = {}
        for i in range(3):
            commod.update({str(i): {'cap': random.uniform(0.1, 9.9),
                                    'pref': str(random.uniform(0.1, 9.9)),
                                    'second_commod': '0',
                                    'constraint': 0}})
        deploy_dict = solver.deploy_solver(commodity_supply={},
                                           commodity_dict={'commod': commod},
                                           commod='commod',
                                           diff=diff,
                                           time=1)
        # check if only one prototype is deployed
        assert (len(deploy_dict.keys()) == 1)

        # get highest preference value prototype
        highest_pref = max([v['pref'] for k, v in commod.items()])
        most_preferred_proto = [
            k for k, v in commod.items() if v['pref'] == highest_pref][0]
        # check if the deployed proto is the most preferred prototype
        for proto, deploy_num in deploy_dict.items():
            assert (proto == most_preferred_proto)
            # check if deployed capacity is the right value
            deployed_cap = deploy_num * commod[proto]['cap']
            if deployed_cap < diff:
                raise ValueError('Underdeploys')
            elif (deployed_cap + diff) > commod[proto]['cap']:
                raise ValueError('Overdeploys')
    assert(True)


def test_pref_solver_eq():
    """ Tests if the preference_deploy function works correctly
        when the preference values are given as an equation """
    diff = -10
    commod = {'1': {'cap': 2,
                    'pref': '1*t',
                    'second_commod': '0',
                    'constraint': 0},
              '2': {'cap': 4,
                    'pref': '10 - (1*t)',
                    'second_commod': '0',
                    'constraint': 0}
              }
    for t in range(10):
        print(t)
        deploy_dict = solver.deploy_solver(commodity_supply={},
                                           commodity_dict={'commod': commod},
                                           commod='commod',
                                           diff=diff,
                                           time=t)
        if t < 5:
            assert(deploy_dict['2'] == 3)
        if t == 5:
            assert(deploy_dict['2'] == 2)
            assert(deploy_dict['1'] == 1)
        if t > 5:
            assert(deploy_dict['1'] == 5)
    assert(True)
