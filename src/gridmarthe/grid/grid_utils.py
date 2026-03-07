#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later
#
#    This file is part of gridmarthe.
#
#    gridmarthe is a python library to manage grid files for
#    MARTHE hydrogeological computer code from French Geological Survey (BRGM).
#    Copyright (C) 2024  BRGM
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

import re
from datetime import datetime
from typing import Union

import numpy as np
import pandas as pd


def _is_sorted(a):
    # https://stackoverflow.com/questions/47004506/check-if-a-numpy-array-is-sorted
    return np.all(a[:-1] <= a[1:])


def _get_scale(da):
    """ Get unique values of dx, dy marthegrid.Dataset """
    dx = np.sort(np.unique(da['dx'].values))[::-1]
    dy = np.sort(np.unique(da['dy'].values))[::-1]
    return list(dx[~np.isnan(dx)]), list(dy[~np.isnan(dy)])


def _find_nearest(array, value):
    # https://stackoverflow.com/questions/2566412/find-nearest-value-in-numpy-array
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx]


def _nearest_node(node, nodes):
    """ Get nearest value in an array of tuple, i.e closest euclidiant distance of XY in an array of XYs"""
    # https://codereview.stackexchange.com/questions/28207/finding-the-closest-point-to-a-list-of-points
    nodes = np.asarray(nodes)
    dist_2 = np.sum((nodes - node)**2, axis=1)
    return np.argmin(dist_2)


def read_dates_from_pastp(fpastp, encoding='ISO-8859-1'):
    """Read simulation timesteps from a .pastp file

    Parameters
    ----------
    fpastp : str
        Path to pastp file (Marthe Timestep)
    encoding : str, optional
        encoding of file, default ISO-8859-1

    Returns
    -------
    pd.DataFrame
        Dataframe with columns timestep, date
    """
    # reading file as raw df - not str ; faster with pandas func
    pastp = pd.read_csv(
        fpastp,
        header=None,
        encoding=encoding
    ).squeeze('columns')

    # First, get steady state time
    idx_0  = pastp.loc[pastp.str.contains(r' \*\*\* D.*but de la simulation.*', regex=True)].index.values[0]
    date_0 = re.findall(r'[0-9]+', pastp.iloc[idx_0] )

    # convert as DF
    timesteps = pd.DataFrame([{
        'timestep': 0,
        'date': datetime(int(date_0[2]), int(date_0[1]), int(date_0[0]) )
    }])

    # Then, get all ending times for transient state
    idx  = pastp.loc[pastp.str.contains(r'^ \*\*\* Le pas.*\d+: se termine.*', regex=True)]
    # extract dates from strings
    dates= pd.DataFrame(
        idx.str.findall(r'[0-9]+').to_list(),
        columns=['timestep', 'day', 'month', 'year'],
        #dtype={'timestep':int, 'day':int, 'month':int, 'year':int}
    )

    # assign dtype
    dates['timestep'] = pd.to_numeric(dates['timestep'])

    # convert data as datetime object
    dates['date'] = pd.to_datetime(dates[['day', 'month', 'year']])
    dates = dates.drop(['month','year', 'day'], axis=1)

    return pd.concat([timesteps, dates], axis=0)


def dropna(ds, varname: str, nanval: Union[list, float]):
    """ Drop values corrresponding to NaN (marthe convention, eg. code 9999.)
    for 1D (or 2D (time, zone)) array
    zone must me a coordinate dimension.

    Parameters
    ----------
    ds : xr.Dataset
        dataset of marthe variable(s)

    varname : str
        variable name in dataset to treat

    nanval : list or float
        value to consider as NaN

    Returns
    -------
    dataset where variable != nanval
    """
    if isinstance(nanval, (float, int, str)):
        nanval = [nanval]
    elif isinstance(nanval, tuple):
        nanval = list(nanval)  # convert to list to be mutated
    nanval += [1.e+20]
    mask = ds[varname.lower()].where(~ds[varname.lower()].isin(nanval)).dropna(dim='zone') # drop nanval
    ds_no_nan = ds.sel(zone=mask['zone'])
    return ds_no_nan


def subset(ds, varname: str, value: Union[list, float]):
    """ Subset dataset based on variable name and value.
    --> inverse of :py:func:`dropna`

    Parameters
    ----------
    ds : xr.Dataset
       dataset of marthe variable(s)

    varname : str
      variable name in dataset to treat

    value: list or float
      value to keep

    Returns
    -------
    dataset where variable = value
    """
    if isinstance(value, (float, int, str)):
        value = [value]
    mask = ds[varname.lower()].where(ds[varname.lower()].isin(value)).dropna(dim='zone')
    ds_filter = ds.sel(zone=mask['zone'])
    return ds_filter


def replace(ds, varname: str, value: float, replace: float):
    """ Replace a value in xr.Dataset for a variable

    Parameters
    ----------
    ds : xr.Dataset
        dataset of marthe variable(s)

    varname : str
        variable name

    value: float
        value to replace

    replace: float
        value to replace with

    Returns
    -------
    dataset with replaced value
    """
    ds[varname].data = np.where(ds[varname].data == value, replace, ds[varname].data)
    return ds


def fillna(ds, varname, value):
    """ Replace real nan (np.nan) value in dataset[varname],
    edge case of :py:func:`gridmarthe.replace`

    Parameters
    ----------
    ds : xr.Dataset
        dataset of marthe variable(s)

    varname : str
       variable name

    value: float
       value to replace NaN with
    """
    ds[varname].data = np.where(np.isnan(ds[varname].data), value, ds[varname].data)
    return ds


def assign_coords(ds, add_lay=True, coords=['x', 'y', 'z'], keep_zone=False, zone_label='zone'):
    """ Assign coordinates from variables to dimensions

    This function transform a 1D or 2D (time, zone dimensions) array to 3D or 4D
    with time, x,y [,z] as dimensions.

    Useful for plot functions/methods.

    Parameters
    ----------
    ds : xr.Dataset
        dataset of Marthe variable(s)
    add_lay : bool, optional
        Boolean to treat `z` (layer) as a dimension (True) or a variable (False)
    coords : list, optional
        list of coordinates to add as dimensions. Default is `['x', 'y', 'z']`
    keep_zone : bool, optional
        keep zone as dimension (will make multiindex). Default is False.
    zone_label : str, optional
        label of current index. Default is `zone` as read by :py:func:`gridmarthe.load_marthe_grid`

    Returns
    -------
    xr.Dataset
        Dataset with coordinates as dimension.
    """
    if len(coords) == 3:
        z_coords = ds.get(coords[2], None) # assert z is here, or bypass
    else:
        z_coords = None

    if add_lay is False:
        # in some case, even if z is included it should not be treated as coord (ex. plot outcrop)
        z_coords = None

    # attrs not kept ? force to keep them
    coords_attrs = [ds.x.attrs, ds.y.attrs]

    da = ds.assign_coords(
        #x=(zone_label, np.around(da_in[coords[0]].data, 1) ),
        x=(zone_label, ds[coords[0]].data ),
        y=(zone_label, ds[coords[1]].data ),
    )
    dims = ['y', 'x']

    if z_coords is not None:
        da = da.assign_coords(z=(zone_label, ds[coords[2]].data))
        dims.insert(0, 'z')
        coords_attrs.append(ds.z.attrs)

    da = da.set_index(zone=dims)
    if not keep_zone:
        # drop duplicates is a security for nested grids, if dropnan was not performed
        da = da.drop_duplicates(zone_label).unstack(zone_label)

    da.x.attrs = coords_attrs[0]
    da.y.attrs = coords_attrs[1]
    if z_coords is not None:
        da.z.attrs = coords_attrs[2]

    return da.sortby(dims).sortby('y', ascending=False)


def stack_coords(ds, coords=['z', 'y', 'x'], dropna=False):
    """ Transform a 3 or 4D aray into 1 or 2D array
    inverse of  :py:func:`assign_coords`

    Parameters
    ----------
    ds : xr.Dataset
        dataset of Marthe variable(s)
    coords : list, optional
        list of coordinates to stack. Default is `['z', 'y', 'x']`
        if `z` is not present in ds.coords, it will be ignored.
    dropna : bool, optional
        drop NaN values in stacked dataset. Default is False.

    Returns
    -------
    xr.Dataset
        Dataset with stacked coordinates as single dimension `zone`.

    Notes
    -----
    For nested grids, the total number of zones cannot be checked
    when flattening back to 1D from cartesian coords/arrays. It will
    lead to incorrect total number of zones as different cell sizes exist
    in the 3D grid. For such cases, it is advised to use dropna=True to remove
    empty zones. Then write back to marthe grid with :py:func:`gridmarthe.write_marthe_grid`
    using a permh file as template.

    TODO: add a sort option to ensure sorted coords in output
    based on z,y,x order AND dx, dy scale (larger scale first, then smaller)
    """
    # create zone index
    coords = [d for d in coords if d in ds.coords.keys()]  # make sure to drop coords that are not present
    dims = np.prod([len(ds[d]) for d in coords])  # create new zone dim
    # dims = np.prod(list(ds.sizes.values()))  # ok -eq
    zone = np.arange(1, dims + 1)

    # stack coords with multiindex zone grouping coords key
    # y need to be re sorted by descending order
    ds2 = ds.copy().sortby('y', ascending=False).stack(zone=coords)

    # keep only zone as dim
    ds3 = ds2.drop_vars(['zone'] + coords).assign_coords(zone=('zone', zone))

    # get back xy[z] as var
    for c in coords:
        ds3[c] = ('zone', ds2[c].data)

    # future coords as non dimensions coordinates
    # ds3 = ds3.set_coords(coords)

    if dropna:
        ds3 = ds3.dropna(dim='zone')
    return ds3


def get_default_variable(ds):
    """ Get the first non coordinate variable in xarray Dataset
    """
    _vars = [x for x in ds.keys() if x not in ['z', 'y', 'x', 'dx', 'dy', 'zone', 'time']]
    return _vars[0]
