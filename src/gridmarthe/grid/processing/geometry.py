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

""" Module to manage geometry attributes of Marthe grids/domain
"""

import numpy as np
import xarray as xr

from .gis import to_geodataframe
from ..grid_utils import _get_nearest_xy, subset, sel_by_coords


def _get_mask_zone(ds, varname: str='permeab', nanval: list=[-9999., 0.]):
    """ Get mask array of active domain, from permh file (hydraulic conductivity)

    Returns
    -------
    array:
        array of valid zone id
    """
    return ds.where(~ds[varname].isin(nanval), drop=True)['zone'].data


def get_active_mask(
    ds, varname: str='permeab',
    nanval: list=[-9999., 0.],
    as_array=False,
    only_mask=False,
    shp_file=None,
    epsg=27572
):
    """ Get the mask of active domain from hydraulic conductivity variable

    This function (i) get the active mask as a 0/1 array and optionally
    (ii) filter the dataset on valid values and dissolve results to get a mask shape

    Input ds should be the permh dataset (read from permh file, ie Horizontal hydraulic
    conductivity, **without** the dropnan option).

    Parameters
    ----------

    ds : xarray.Dataset

    varname : str, optional
        default is 'permeab'

    nanval : float or list, optional
        default are 'permeab' nan values : 0, -9999.

    as_array : bool, optional.
        Option to get result as a xr.Dataset and not geodataframe.
        Default is False.

    only_mask : bool, optional
        filter `ds` on active mask. Default is False, returns a dataset
        with 'ibound' variable set to 1 (active domain) or 0.

    shp_file : str, optional.
        if set (and not `as_array`), used to stored result in a file.

    epsg : int, optional
        if shp_file, use epsg to set projection.

    Returns
    -------
    xr.Dataset
        Dataset with ibound field, or gpd.GeoDataFrame of active domain if `as_array`
        is set to False.
    """

    mask = _get_mask_zone(ds, varname, nanval)
    ds_masked = ds.copy()
    ds_masked['ibound'] = ('zone', np.where(np.isin(ds.zone.data, mask), 1, 0))
    if not as_array:
        ds_masked = ds_masked.sel(zone=mask)
        gdf  = to_geodataframe(ds_masked, epsg=epsg)
        gdf  = gdf.dissolve()
        if shp_file is not None:
            gdf.to_file(shp_file)
        return gdf
    return ds_masked if not only_mask else ds_masked.sel(zone=mask)


def _get_true_topo(topo, key='h_topogr'):
    # in Marthe, topography is stored in the first layer,
    # for the whole domain, avoiding duplicates data.
    # Here, this function tile topography to all layers
    # to allow vectorized operations.
    ds = topo.copy()
    if 'z' not in list(topo.dims) + list(topo.keys()):
        return ds  # single layer model, topo already covers the whole domain
    zdim = len(np.unique(topo.z.data))
    true_topo = subset(topo, 1, 'z')[key].data  # true topo is only 1st layer
    true_topo = np.tile(true_topo, zdim)  # set topo for all layers
    ds[key] = (tuple(topo.dims), true_topo)
    return ds


def _get_upper_alt(topo, hsubs, hsubs_name='h_substrat', topo_name='h_topogr'):
    """ Compute upper altitude of cells by layer
    Topo should contains the same values in all layers, see :py_func:`_get_true_topo`

    TODO: make valid version with time (if topo change with times)

    Returns
    -------
    dataset with only ([time],zone), (h_topogr, h_substr, h_upper)
    """
    ds = xr.combine_by_coords([topo, hsubs], combine_attrs='override', compat='override')
    _dims = list(ds.dims)  # ('time','zone') in most cases, only 'zone' if no time
    if 'time' in _dims:
        ds.isel(time=0)  # only for first time, topo is mainly constant in time in Marthe
    df = ds.to_dataframe().reset_index()
    _sort_by = ['x', 'y', 'z'] if 'z' in df.columns else ['x', 'y']  # no z for single layer model
    df = df.sort_values(by=_sort_by).copy()  # assure data are sort in this way
    # set nans for topo and hsubs
    # this is constant in Marthe / should not be changed by user
    for x in [hsubs_name, topo_name]:
        df[x] = df[x].replace(9999., np.nan)  # avoid doing this on full df, zone might be impacted

    # Compute z top of layers
    df[topo_name] = df.groupby(['x', 'y'])[topo_name].transform('first')  # topo is always first of group
    df['tmp']     = df.groupby(['x', 'y'])[hsubs_name].ffill()  # ffill z down for each group
    df['h_upper'] = df.groupby(['x', 'y'])['tmp'].shift(1)  # then shift to initiate z top
    # For the first layer (or if h_upper is NaN but h_substrat is valid), then h_topogr is z upper (first layer)
    mask = (df['h_upper'].isna()) & (df[hsubs_name].notna())
    df.loc[mask, 'h_upper'] = df.loc[mask, topo_name]

    # # switch back to xarray backend
    ds = df.set_index(_dims)[[topo_name, hsubs_name, 'h_upper']].to_xarray()
    return ds


def _get_thickness(h_upper, hsubs):
    """ Compute layer thickness from upper altitudes
    and substratums.

    See, :py_func:`_get_upper_alt`
    """
    return h_upper - hsubs


def _get_depth(topo, h_upper):
    return topo - h_upper


def compute_geometry(topo, hsubs, mask=None, topo_varname='h_topogr', subs_varname='h_substrat'):
    """ Compute geometry attributes of Marthe domain

    Parameters
    ----------
    topo : xarray.Dataset
        Topgraphy of the domain (stored in the first layer, in Marthe Conventions).
    hsubs : xarray.Dataset
        altitude of all the lower boundary in the domain
    mask : numpy.array, optional
        list of indices (`zone`) to keep, if None (default) not used.
        It is recommended to use this mask to avoid computing on invalid cells.
        For example, values may be defined in masked cells of the model domain,
        which will lead to incorrect results. Using the active domain as mask
        is a good practice (See example).
    topo_varname : str, optional
        name of the variable containing the topography in the corresponding dataset,
        allow custom name for marthe backward compatibility
    subs_varname : str, optional
        name of the variable containing the substratum in the corresponding dataset,
        allow custom name for marthe backward compatibility

    Returns
    -------
    xarray.Dataset
        A new dataset with layer, depth, thickness, upper/lower altitude.

    Notes
    -----
    - If mask is not provided, the input datasets should be sliced on valid
      cells before calling this function for accurate results;
    - The time dimension is dropped during process

    Examples
    --------
    >>> import gridmarthe as gm
    >>> permh = gm.load_marthe_grid('data/craie_npc.permh', drop_nan=True)
    >>> topo  = gm.load_marthe_grid('data/craie_npc.topog', varname='H_TOPOGR')
    >>> hsub  = gm.load_marthe_grid('data/craie_npc.hsubs', varname='H_SUBSTRAT')
    >>> geom = gm.compute_geometry(topo, hsub, mask=permh.zone.data)
    """

    # compute elements of geometry
    xtopo = _get_true_topo(topo, key=topo_varname)  # map topo values to all layers
    xhsubs = hsubs.copy()

    if mask is not None:
        xtopo  = xtopo.sel(zone=mask)
        xhsubs = xhsubs.sel(zone=mask)

    tmp   = _get_upper_alt(xtopo, xhsubs, subs_varname, topo_varname)
    thick = _get_thickness(tmp['h_upper'].data, tmp[subs_varname].data)
    depth = _get_depth(tmp[topo_varname].data, tmp['h_upper'].data)

    # put values in xr.Dataset
    ds = xtopo.copy()
    dims = tuple(xtopo.dims)  # ('time', 'zone') in most cases, only 'zone' if no time
    ds['z_lower']    = (dims, tmp[subs_varname].data)
    ds['z_upper']    = (dims, tmp['h_upper'].data)
    ds['thickness']  = (dims, thick)
    ds['depth']      = (dims, depth)
    if 'time' in ds:
        ds = ds.squeeze('time').drop_vars('time')
    return ds


def get_surface_layer(ds, aquif_layers=None):
    """ Compute surface mask of marthe domain

    This function return min layer for every zone of a grimarthe dataset with z coords
    A subset on specific (aquifers) layers can be performed with `aquif_layers`.
    if set, aquif_layers must be a sequence (list, tuple, array) of layer (list of int).

    This should be used to get a surface mask, ie get zone to filter a dataset.

    Examples
    --------
    >>>    mask = get_surface_layer(ds, [6,8,9])
    >>>    ds_surf = ds.sel(zone=mask.zone.data)

    Parameters
    ----------
    ds : xarray.Dataset
    aquif_layers : sequence (list, tuple, array) of int
        representing layers to subset ds. Only active domain must
        be passed to function (ie drop nan first)

    Returns
    -------
    surface_mask: xarray.Dataset
    """
    ds = ds.copy()
    _dims = tuple(ds.dims)
    coords = ['x', 'y']
    if 'time' in _dims:
        # time not needed here, zone are independant from time coords
        # ds = ds.drop_dims('time')
        coords.append('time')
    df = ds.to_dataframe()
    df = df.reset_index()

    if aquif_layers is not None:
        df = df[df['z'].isin(aquif_layers)]

    idx_z_min = df.groupby(coords).z.idxmin() # get index of min z ("layer") for each x,y,t groups
    first_aquif_lay = df.loc[idx_z_min].reset_index().set_index('zone').drop('index', axis=1)
    return first_aquif_lay.to_xarray()


def search_zone(ds, i=None, j=None, x=None, y=None, z=None):
    """ Search zone number in marthe grid, based on xy or ij (col, lig)

    This function can be used to search zone number from coordinates or indices.
    You must provide either (i,j) or (x,y).

    Notes
    -----

    - if ds is multilayered, you need to provide the layer you want (z arg., int type)
    - ds should contains dx and dy
    - ds should not have assigned coords (x and y are variables, zone is the
    dimension coordinates (with time))


    Parameters
    ----------
    ds : xarray.Dataset
        dataset with zone, x, y, dx, dy variables.
    i : int, optional
        column index to search zone.
    j : int, optional
        row index to search zone.
    x : float, optional
        x coordinate to search zone.
    y : float, optional
        y coordinate to search zone.
    z : int, optional
        layer index to search zone. If not provided, all layers are considered.

    Returns
    -------
    zone : xarray.Dataset
        dataset with zone variable, containing the zone number(s) corresponding
        to the provided coordinates. If no zone is found, an empty dataset is
        returned. If multiple zones are found, all of them are returned.
    """
    ds_search = ds.copy()

    if z is not None:
        ds_search = ds_search.where(ds_search.z == z, drop=True)

    if x is not None:
        assert y is not None, 'if x is provided, y cannot be None'

        nearest_xy, nearest_idx = _get_nearest_xy(ds_search, x, y)

        # check if xy is in a cell == dx and dy are not greater than grid resolution
        nearest_zone = ds_search.isel(zone=nearest_idx)
        dx = np.abs(nearest_zone.x.data - x)
        dy = np.abs(nearest_zone.y.data - y)

        # get mask of cell(s) (if several layers) matching xy
        if dx <= nearest_zone.dx.data and dy <= nearest_zone.dy.data:
            _, mask = sel_by_coords(ds_search, nearest_xy[0], nearest_xy[1], return_mask=True)
            mask = xr.DataArray(mask, {"zone": ds_search.zone.data})  # as dataarray to use .where()
        else:
            mask = ds_search['zone'].isnull()

    if i is not None:
        assert j is not None, 'if i is provided, j cannot be None'
        mask = (ds_search['col'] == i) & (ds_search['row'] == j)

    # zone = ds.where(mask, drop=True)['zone'].data
    zone = ds_search.where(mask, drop=True)
    return zone
