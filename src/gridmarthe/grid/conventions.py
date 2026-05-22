#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Coordinates and variables and attributes definitions for gridmarthe.
"""

import sys

if sys.version_info >= (3, 11):
    from datetime import datetime, UTC
else:
    from datetime import datetime

import pyproj
import numpy as np
import pandas as pd


# http://cfconventions.org/Data/cf-standard-names/current/build/cf-standard-name-table.html
# closest value in cf-convention for groundwater level : water_table_depth
# should we make a suggestion with water_table_level ?
# https://github.com/cf-convention/discuss/issues

# TODO: use the config file from martpy, and deal with english names too.
VARS_ATTRS = {
    'permeab': {
        'varname': 'PERMEAB',
        'units': 'm/s',
        'mart_missing_value': 0.,
        'standard_name': '',
        'long_name': 'aquifer_hydraulic_conductivity'
    },
    'charge' : {
        'varname': 'CHARGE',
        'units': 'm',
        'mart_missing_value': 9999.,
        'standard_name': 'water_table_level',
        'long_name': 'groundwater head'
    },
    'saturat': {
        'varname': 'SATURAT',
        'units': '%',
        'mart_missing_value': 9999.,
        'standard_name': 'water_table_saturation',
        'long_name': 'groundwater_saturation'
    },
    'debit': {
        'varname': 'DEBIT',
        'units': 'm3/s',
        'mart_missing_value': 0.,
        'standard_name': '',
        'long_name': 'flow'
    },
    'debit_rivi': {
        'varname': 'DEBIT_RIVI',
        'units': 'm3/s',
        'mart_missing_value': 9999.,
        'standard_name': 'water_volume_transport_in_river_channel',
        'long_name': 'river_discharge_flow'
    },
    'qech_riv_napp': {
        'varname': 'QECH_RIV_NAPP',
        'units': 'm3/s',
        'mart_missing_value': 9999.,
        'standard_name': '',
        'long_name': 'surface_groundwater_exchange_flow'
    },
    'emmag_libr': {
        'varname': 'EMMAG_LIBR',
        'units': '-',
        'mart_missing_value': 0.,
        'standard_name': '',
        'long_name': 'aquifer_specific_yield'
    },
    'emmag_capt': {
        'varname': 'EMMAG_CAPT',
        'units': 'm-1',
        'mart_missing_value': 0.,
        'standard_name': '',
        'long_name': 'aquifer_confined_storage_coefficient'
    },
    'zone_geom': {
        'varname': 'ZONE_GEOM',
        'units': '-',
        'mart_missing_value': 0.,
        'standard_name': '',
        'long_name': 'geometry_zone_identifier'
    },
    'direct_val' : {
        'varname': 'DIRECT_AVAL',
        'units': '-',
        'mart_missing_value': 0.,
        'standard_name': 'Flow direction'
    },
    'indic_rivi' : {
        'varname': 'INDIC_RIVI',
        'unit': '-',
        'mart_missing_value': 0.,
        'standard_name': 'river_index'
    },
    'afflu_rivi' : {
        'varname': 'AFFLU_RIVI',
        'unit': '-',
        'mart_missing_value': 0.,
        'standard_name': 'river_affluent_number'
    },
    'tronc_rivi' : {
        'varname': 'TRONC_RIVI',
        'unit': '-',
        'mart_missing_value': 0.,
        'standard_name': 'river_reach_number'
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


def _assign_xy_attrs(epsg=27572):
    crs = pyproj.CRS(epsg)
    cf_attrs = crs.coordinate_system.to_cf()
    xy_attrs = {
        'x' : cf_attrs[0],
        'y' : cf_attrs[1],
    }
    return xy_attrs


def _assign_z_attrs(full_3d=False):
    z_attrs =  {
        'units': '-' if not full_3d else 'm',
        'axis': 'Z',
        'positive': 'down',
        'standard_name': 'depth',
        'long_name': 'aquifer_layer' if not full_3d else 'depth'
    }
    return z_attrs


def _parse_global_attrs(
    title=None,
    dims=None,
    xyfactor=1.,
    dates=None,
    is_nested=False,
    dxlus=None,
    dylus=None,
    xcols=None,
    yligs=None,
    epsg=27572,
):
    """ Parse attributes for xarray.Dataset
    nb: attrs must be string, int, float
    # TODO: check https://cfconventions.org/Data/cf-conventions/cf-conventions-1.7/build/apa.html
    # Memo:
    #   - for gridmapping https://cfconventions.org/Data/cf-conventions/cf-conventions-1.7/build/ch05s06.html
    #   - for reduced-horizontal-grid https://cfconventions.org/Data/cf-conventions/cf-conventions-1.7/build/ch08s02.html
    #   - for timeseries https://cfconventions.org/Data/cf-conventions/cf-conventions-1.7/build/ch09s05.html
    """
    crs = pyproj.CRS(epsg)

    prologue = {
        'conventions'         :'CF-1.10',  # check https://cfconventions.org/
        'title'               : title if title is not None else '',
        'marthe_grid_version' : 9.0,
        'original_dimensions' : 'x,y,z [grids]: ' + '; '.join(
            [ ' '.join(map(str, x)) for x in dims]
        ),
    }
    grid_attrs = {
        'crs': str(crs.to_cf()),
        'lon_resolution': ', '.join(map(str, np.unique(dxlus))),
        'lat_resolution': ', '.join(map(str, np.unique(dylus))),
        'resolution_units': crs.coordinate_system.to_cf()[0].get('units', ''),
        'scale_factor'  : xyfactor,
        'nested_grid'   : str(is_nested),
        'extend'        : "xymin : {} {}; xymax: {} {}".format(
            np.min(xcols), np.min(yligs), np.max(xcols), np.max(yligs)
        ),
    }
    dates_attrs = {}
    if isinstance(dates, pd.DatetimeIndex):
        dates_attrs = {
            'period'    : '{}-{}'.format(
                pd.to_datetime(dates.min()).year, pd.to_datetime(dates.max()).year
            ), # force pd.date_time, case of pastp => numpydatetime64 / # np.datetime_as_string(i, unit='M')
            'frequency' : '{} day(s)'.format(str(dates.to_series().diff().mean().days)),
        }

    if sys.version_info >= (3, 11):
        _date_now = datetime.now(UTC).strftime('%Y-%m-%dT%H:%M:%SZ UTC')
    else:
        _date_now = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ UTC')

    epilogue = {
        'creation_date' : 'Created on {}'.format(_date_now),
        # comment or source ? https://cfconventions.org/Data/cf-conventions/cf-conventions-1.7/build/ch02s06.html
        'comment'       : 'Hydrogeological model created with MARTHE code '\
                          '(Thiery, D. 2020. Guidelines for MARTHE v7.8 computer code '\
                          'for hydro-systems modelling. report BRGM/RP-69660-FR).'
    }

    return {**prologue, **grid_attrs, **dates_attrs, **epilogue}
