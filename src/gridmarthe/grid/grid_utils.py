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


def _is_sorted(a, asc=True):
    # https://stackoverflow.com/questions/47004506/check-if-a-numpy-array-is-sorted
    return np.all(a[:-1] <= a[1:]) if asc else np.all(a[:-1] >= a[1:])


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
    """ Get nearest value in an array of tuple, i.e closest euclidiant distance
    of XY in an array of XYs

    Returns:
        index of the nearest node
        distance to the nearest node
    """
    # https://codereview.stackexchange.com/questions/28207/finding-the-closest-point-to-a-list-of-points
    nodes = np.asarray(nodes)
    dist_2 = np.sum((nodes - node)**2, axis=1)
    idx_nearest = np.argmin(dist_2)
    return idx_nearest, np.sqrt(idx_nearest)


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
        Dataframe with columns step, time
    """
    # reading file as raw df - not str ; faster with pandas func
    pastp = pd.read_csv(
        fpastp,
        header=None,
        encoding=encoding
    ).squeeze('columns')

    if isinstance(pastp, pd.DataFrame):
        # pastp needs to be a pd.Series
        pastp = pastp.iloc[:, 0]

    # First, get steady state time
    idx_0  = pastp.loc[pastp.str.contains(r' \*\*\* D.*but de la simulation.*', regex=True)].index.values[0]

    _match = re.search(
        r':\s*(?P<time>\d+\.?\d+|\d{2}/\d{2}/\d{4}( \d{2}:\d{2})?)\s*;',
        pastp.iloc[idx_0]
    )
    if _match:
        date_0 = _match.group(1)
    else:
        raise ValueError("No date to parse in pastp file.")

    _is_date = False
    if re.match(r'(\d{2}/\d{2}/\d{4})( \d{2}:\d{2})?', date_0):
        _is_date = True

    if _is_date:
        dt = datetime.strptime(date_0, '%d/%m/%Y')
    else:
        dt = float(date_0) if re.match(r'\d+\.\d+', date_0) else int(date_0)

    # convert as DF
    _steadystep = pd.DataFrame([{
        'step': 0,
        'time': dt
    }])

    # Then, get all ending times for transient state
    idx  = pastp.loc[pastp.str.contains(r'^ \*\*\* Le pas.*\d+: se termine.*', regex=True)]
    # extract times from strings
    times = pd.DataFrame(idx.str.findall(r'[0-9]+').to_list())

    # assign dtype
    # convert data as datetime object
    if _is_date:
        times.columns = ['step', 'day', 'month', 'year']
        times['time'] = pd.to_datetime(times[['day', 'month', 'year']])
        times = times.drop(['month','year', 'day'], axis=1)
    else:
        times.columns = ['step', 'time']
        times['time'] = pd.to_numeric(times['time'])

    times['step'] = pd.to_numeric(times['step'])

    return pd.concat([_steadystep, times], axis=0)


def dropna(ds, varname: str, nanval: Union[list, float]):
    """ Drop values corrresponding to NaN (marthe convention, eg. code 9999.)
    for 1D (or 2D (time, zone)) array zone must be a coordinate dimension.

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


def assign_coords(ds, add_lay=True, coords=('x', 'y', 'z'), keep_zone=False, zone_label='zone'):
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
        x=(zone_label, ds[coords[0]].data),
        y=(zone_label, ds[coords[1]].data),
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


def stack_coords(ds, coords=('z', 'y', 'x'), dropna=False):
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
    coords = [d for d in coords if d in ds.coords]  # make sure to drop coords that are not present
    dims = np.prod([np.size(ds[d]) for d in coords])  # create new zone dim
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
    _vars = [x for x in ds if x not in ['z', 'y', 'x', 'dx', 'dy', 'zone', 'time']]
    return _vars[0]


def _get_nearest_xy(ds, x, y):
    """ Get the nearest (x, y) point in a 1D flattened xarray Dataset

    Returns
    -------
    nearest_xy: array of two floats
        The nearest (x, y) point in the dataset
    nearest_idx: int
        Index of the nearest point in the dataset
    """
    nearest, dist = _nearest_node(
        np.array([(x, y)]),
        np.array(list(zip(ds['x'].data, ds['y'].data)))
    )
    xy_arr = np.array([ds['x'].data, ds['y'].data]).T
    _nearest_xy = xy_arr[nearest]
    return _nearest_xy, nearest


def sel_xy(dataset, x=None, y=None, z=None, method=None, tolerance=1e3, return_mask=False):
    """ Filter a 1D flattened xarray Dataset by spatial (x, y) and/or z ranges.

    When grid are stored as 1D vector for spatial dimension, `xarray.Dataset.sel`
    method cannont be used on `x` and `y` coordinates. This function is a workaround
    to select a point in the grid when coordinates ('x', 'y') are variables.

    Parameters
    ----------
    dataset : xarray.Dataset
        The input dataset with 1D 'zone' dimension and variables 'x', 'y', 'z'.
    x : float or tuple, optional
        x-coordinate: float for point selection, (xmin, xmax) for range.
    y : float or tuple, optional
        y-coordinate: float for point selection, (ymin, ymax) for range.
    z : int or tuple, optional
        z-level: int for exact, (zmin, zmax) for range.
    method : str, optional
        For point selection (x,y), use 'nearest' to find closest point.
        Requires `tolerance` (max distance).
    tolerance : float, optional
        Max distance when using method='nearest' (in same units as x/y).
        Default is 1e3 (meters).
    return_mask: bool, optional
        Option to return mask array

    Returns
    -------
    xarray.Dataset
        Filtered dataset with matching indices, still 1D.

    Example
    -------
    Select by spatial box
    >>> subset = sel_xy(dataset, x=(4.5e5, 5.0e5), y=(2.5e6, 2.6e6))
    Select by z level
    >>> subset = sel_xy(dataset, z=(1, 3))
    Select by point (nearest)
    >>> subset = sel_xy(dataset, x=4.35e5, y=2.58e6, method='nearest', tolerance=1e3)
    Combine x, y, z
    >>> subset = sel_xy(dataset, x=(4.5e5, 5.0e5), y=(2.5e6, 2.6e6), z=2)
    """
    mask = np.ones(len(dataset.zone), dtype=bool)

    # Handle X and Y point selection with method='nearest'
    # if (x is not None and isinstance(x, (int, float))) or (y is not None and isinstance(y, (int, float))):

    if method == 'nearest':
        if tolerance is None:
            raise ValueError("tolerance is required when method='nearest'")

        assert x is not None or y is not None, "At least one of x or y must be provided"

        x_vals = dataset['x'].values if x is not None else None
        y_vals = dataset['y'].values if y is not None else None

        # Compute distances
        dist_sq = 0.0
        if x is not None:
            dist_sq += (x_vals - x)**2
        if y is not None:
            dist_sq += (y_vals - y)**2

        # Find the closest point
        idx_min = np.argmin(dist_sq)
        dist_min = np.sqrt(dist_sq[idx_min])

        # Only keep it if within tolerance
        if dist_min <= tolerance:
            new_mask = np.zeros_like(mask)
            new_mask[idx_min] = True
            mask &= new_mask
        else:
            mask[:] = False  # No point within tolerance
    else:
        # Look for exact match
        if isinstance(x, (int, (float, np.floating))):
            mask &= np.isclose(dataset['x'].values, x)
        if isinstance(y, (int, (float, np.floating))):
            mask &= np.isclose(dataset['y'].values, y)

        # Range or no selection
        if isinstance(x, (tuple, list)) and len(x) == 2:
            xmin, xmax = x
            mask &= (dataset['x'].values >= xmin) & (dataset['x'].values <= xmax)
        if isinstance(y, (tuple, list)) and len(y) == 2:
            ymin, ymax = y
            mask &= (dataset['y'].values >= ymin) & (dataset['y'].values <= ymax)

    # Handle Z selection
    if z is not None:
        z_vals = dataset['z'].values
        if isinstance(z, (int, np.integer)):
            mask &= (z_vals == z)
        elif isinstance(z, (tuple, list)) and len(z) == 2:
            zmin, zmax = z
            mask &= (z_vals >= zmin) & (z_vals <= zmax)
        else:
            raise ValueError("z must be an int or a 2-tuple (min, max)")

    # Apply mask
    filtered_dataset = dataset.isel(zone=mask)
    if not return_mask:
       return filtered_dataset
    else:
        return filtered_dataset, mask
