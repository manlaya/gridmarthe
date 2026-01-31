#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Coordinates and variables and attributes definitions for gridmarthe.
"""

# http://cfconventions.org/Data/cf-standard-names/current/build/cf-standard-name-table.html
# closest value in cf-convention for groundwater level : water_table_depth
# should we make a suggestion with water_table_level ?
# https://github.com/cf-convention/discuss/issues

# TODO: use the config file from martpy, and deal with english names too.
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
        'standard_name': 'Flow direction'
    },
}

# add variants for variable names
VARS_ATTRS['geom_zone'] = VARS_ATTRS['zone_geom']  # english variant in MARTHE code


# For memory only, now with pyproj
COOR_ATTRS = {
    'x' : {
        'units': 'meters',
        'axis': 'X',
        'standard_name': 'projection_x_coordinate',
        'coverage_content_type' : "coordinate"
    },
    'y'  : {
        'units': 'meters',
        'axis': 'Y',
        'standard_name': 'projection_y_coordinate',
        'coverage_content_type' : "coordinate"
    },
    'lon': {
        'units': 'degrees_east',
        'standard_name': 'longitude',
    },
    'lat': {
        'units': 'degrees_north',
        'standard_name': 'latitude' ,
    },
    'z': {
        'units': 'm',
        'axis': 'Z',
        'positive': 'down',
        'standard_name': 'depth',
        'long_name': 'depth'
    },
    'layer': {
        'units': '-',
        'axis': 'Z',
        'positive': 'down',
        'standard_name': 'depth',
        'long_name': 'aquifer_layer'
    }
}
