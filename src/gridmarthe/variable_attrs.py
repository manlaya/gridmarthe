#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Variables and attributes definitions for gridmarthe.
"""

# http://cfconventions.org/Data/cf-standard-names/current/build/cf-standard-name-table.html
# closest value in cf-convention for groundwater level : water_table_depth
# should we make a suggestion with water_table_level ?
# https://github.com/cf-convention/discuss/issues

VARS_ATTRS = {
    'permeab': {
        'varname': 'PERMEAB',
        'units': 'm/s',
        'missing_value': 0.,
        'standard_name': '',
        'long_name': 'aquifer_hydraulic_conductivity'
    },
    'charge' : {
        'varname': 'CHARGE',
        'units': 'm',
        'missing_value': 9999.,
        'standard_name': 'water_table_level',
        'long_name':
        'groundwater head'
    },
    'saturat': {
        'varname': 'SATURAT',
        'units': '%'   ,
        'missing_value': 9999.,
        'standard_name': 'water_table_saturation',
        'long_name': 'groundwater_saturation'
    },
    'debit': {
        'varname': 'DEBIT',
        'units': 'm3/s',
        'missing_value': 0.,
        'standard_name': '',
        'long_name': 'flow'
    },
    'debit_rivi': {
        'varname': 'DEBIT_RIVI',
        'units': 'm3/s',
        'missing_value': 9999.,
        'standard_name': 'water_volume_transport_in_river_channel',
        'long_name': 'river_discharge_flow'
    },
    'qech_riv_napp': {
        'varname': 'QECH_RIV_NAPP',
        'units': 'm3/s',
        'missing_value': 9999.,
        'standard_name': '',
        'long_name': 'surface_groundwater_exchange_flow'
    },
    'emmag_libr': {
        'varname': 'EMMAG_LIBR',
        'units': '-'   ,
        'missing_value': 0.,
        'standard_name': '',
        'long_name': 'aquifer_specific_yield'
    },
    'emmag_capt': {
        'varname': 'EMMAG_CAPT',
        'units': 'm-1',
        'missing_value': 0.,
        'standard_name': '',
        'long_name': 'aquifer_confined_storage_coefficient'
    },
    'zone_geom': {
        'varname': 'ZONE_GEOM',
        'units': '-'   ,
        'missing_value': 0.,
        'standard_name': '',
        'long_name': 'geometry_zone_identifier'
    },
    'direct_val' : {
        'varname': 'DIRECT_AVAL',
        'units': '-',
        'missing_value': 0.,
        'standard_name': 'flow_direction'
    },
    'indic_rivi' : {
        'varname': 'INDIC_RIVI',
        'unit': '-',
        'missing_value': 0.,
        'standard_name': 'river_index'
    },
    'afflu_rivi' : {
        'varname': 'AFFLU_RIVI',
        'unit': '-',
        'missing_value': 0.,
        'standard_name': 'river_affluent_number'
    },
    'tronc_rivi' : {
        'varname': 'TRONC_RIVI',
        'unit': '-',
        'missing_value': 0.,
        'standard_name': 'river_reach_number'
    },
}

# add variants for variable names
VARS_ATTRS['geom_zone'] = VARS_ATTRS['zone_geom']  # english variant in MARTHE code
