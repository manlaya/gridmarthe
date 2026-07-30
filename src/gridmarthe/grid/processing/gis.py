#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later
#
#    This file is part of gridmarthe.
#
#    gridmarthe is a python library to manage grid files for
#    MARTHE hydrogeological computer code from French Geological Survey (BRGM).
#    Copyright (C) 2024-2025  BRGM
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
""" GIS utility for marthe grids
"""


from typing_extensions import deprecated
import re
import numpy as np

from pyproj import Transformer, CRS
import geopandas as gpd
import xarray as xr

from ..grid_utils import assign_coords, stack_coords
from .gutils import _polygonize


def _build_polyg(ds):
    """ build a (rectangular) polygon shape from marthegrid dataset """

    x0 = ds.x.values - (ds.dx.values / 2.)
    y0 = ds.y.values - (ds.dy.values / 2.)
    x1 = ds.x.values + (ds.dx.values / 2.)
    y1 = ds.y.values + (ds.dy.values / 2.)

    return _polygonize(x0, y0, x1, y1)


def to_geodataframe(ds, epsg='EPSG:27572', fmt='long'):
    """ Convert marthegrid.Dataset to a geodataframe

    Parameters
    ----------
    ds : xarray.Dataset
        The dataset to convert.
    epsg : str, optional
        The EPSG code for the coordinate reference system, by default 'EPSG:27572'.
    fmt : str, optional
        The format of the output GeoDataFrame, either 'long' or 'wide', by default 'long'.

    Returns
    -------
    geopandas.GeoDataFrame
        The converted GeoDataFrame.
    """

    polygons = _build_polyg(ds) # .isel(time=0) # x,y does not vary in time
    df = ds.to_dataframe() #.to_pandas() # only for 1 dim

    if 'time' in ds.dims:
        # ad geom for every timestep
        polygons = np.tile(
            polygons.flatten(),
            len(np.unique(df.index.get_level_values('time')))
        )

    gdf = gpd.GeoDataFrame(
        df,
        geometry=polygons,
        crs=epsg
    )

    if fmt == "wide" and 'time' in ds.dims:
        # here no wide fmt if no time, so no if 'time' in ds.dims:
        gdf = gdf.unstack('time')
        gdf.columns = [
            '{}_{}'.format(x, y.strftime('%Y%m%d'))\
            if x not in ['x', 'y', 'dx', 'dy', 'z', 'geometry'] else x\
            for x, y in gdf.columns
        ]
        gdf = gdf.loc[:,~gdf.columns.duplicated()].copy()  # drop duplicated cols
        gdf = gdf.set_geometry('geometry')  # need to make again geom after drop dupl

    return gdf


def _check_rioxarray():
    try:
        import rioxarray
    except ModuleNotFoundError as e:
        raise ModuleNotFoundError(
            'rioxarray is not Found in python env.' + \
            'Please install it or reinstall gridmarthe with optional dependancies: pip install gridmarthe[opt]'
        ) from e
    return


def clip_dataset(ds, gdf, crs=27572, engine='gdf'):
    """ Clip a xarray Dataset with a gpd.GeoDataFrame

    Needs rioxarray. If not installed, raise ModuleNotFoundError
    please install it or reinstall gridmarthe with optional dependancies: pip install gridmarthe[opt]

    See: https://corteva.github.io/rioxarray/html/examples/clip_geom.html
    Todo: shapely version

    Parameters
    ----------
    ds : xarray.Dataset
        The dataset to clip.
    gdf : geopandas.GeoDataFrame
        The GeoDataFrame containing the geometry to clip with.
    crs : int, optional
        The coordinate reference system to use for the clipping, by default 27572.
    engine : str, optional
        The engine to use for clipping, by default 'gdf'.

    Returns
    -------
    xarray.DataArray or xarray.Dataset
        The clipped dataset.
    """
    _check_rioxarray()
    shp = gdf.to_crs(crs)
    da  = assign_coords(ds.rio.write_crs("EPSG:{}".format(crs)))
    clipped_da = da.rio.clip(shp.geometry.values, shp.crs, drop=True)
    return clipped_da


@deprecated("Use `sel_by_coords` instead")
def subset_with_coords(da, dims=['x', 'y'], gdf=None, xmin=None, ymin=None, xmax=None, ymax=None):
    """ subset DataArray or Dataset on rectangular shape, with gpd.GeoDataFrame or bounds

    Parameters
    ----------
    da : xarray.DataArray or xarray.Dataset
        The data to subset.
    dims : list of str, optional
        The dimensions to use for subsetting, by default ['x', 'y'].
    gdf : geopandas.GeoDataFrame, optional
        A GeoDataFrame containing the geometry to use for subsetting, by default None.
    xmin, ymin, xmax, ymax : float, optional
        The manual bounds to use for subsetting, by default None.

    Returns
    -------
    xarray.DataArray or xarray.Dataset
        The subsetted data.
    """
    if gdf is not None:
        # edit, one line with total_bounds attribute instead of bounds
        # xmin, ymin, xmax, ymax = gdf.bounds.T.values
        # xmin, ymin, xmax, ymax = xmin[0], ymin[0], xmax[0], ymax[0]
        xmin, ymin, xmax, ymax = gdf.total_bounds #gdf.bounds.T.values
        # or .T.to_numpy(), in any case return np.array // total_bounds instead of bounds
    else:
        assert xmin is not None, "When using manual bounds, all must be set"
        assert xmax is not None, "When using manual bounds, all must be set"
        assert ymin is not None, "When using manual bounds, all must be set"
        assert ymax is not None, "When using manual bounds, all must be set"

    mask_lon = ( da[dims[0]] >= xmin) & ( da[dims[0]] <= xmax) #da.xc
    mask_lat = ( da[dims[1]] >= ymin) & ( da[dims[1]] <= ymax)

    # imin, imax = np.where(da[var[0]].values==xmin)[0], np.where(da[var[0]].values==xmax)[0]
    # jmin, jmax = np.where(da[var[1]].values==ymin)[0], np.where(da[var[1]].values==ymax)[0]
    # sub_da = da.isel(i=slice(int(imin), int(imax)+1), j=slice(int(jmax), int(jmin)+1))
    # # j in reverse order / +1 on imax, jmin because upper is exclude in py slicing

    return da.where(mask_lon & mask_lat, drop=True)


def _transf_proj_regrid(ds, from_epsg="EPSG:27572", to_epsg="EPSG:2154", decimals=None):
    """ Recreate a transformed grid based on dx, dy and x0, y0
    """
    transformer = Transformer.from_crs(from_epsg, to_epsg, always_xy=True)
    crs = CRS(to_epsg)

    ds_2d = assign_coords(ds) if 'x' not in ds.dims else ds.copy()
    grid_2d = ds_2d.copy(deep=True)  # deep to avoid side effect with dx
    if 'z' in ds_2d.dims:
        # as x, y are the same in along z dimension in marthe grids:
        grid_2d = grid_2d.isel(z=0)

    nx, ny = len(grid_2d.x), len(grid_2d.y)
    x0, y0 = np.nanmin(grid_2d.x), np.nanmin(grid_2d.y)
    x1, y1 = np.nanmax(grid_2d.x), np.nanmax(grid_2d.y)
    dx, dy = grid_2d.dx.data[0,:], grid_2d.dy.data[:,0]
    # dx, dy = grid_2d.dx.data, grid_2d.dy.data
    dx[0], dy[0] = 0, 0
    dxc, dyc = np.cumsum(dx), np.cumsum(dy)

    new_xy0 = transformer.transform(x0, y0)
    if isinstance(decimals, int):
        new_xy0 = np.round(new_xy0, decimals)
    # dx, dy = ds['dx'].data, ds['dy'].data
    # new_x = np.linspace(new_xy0[0], new_xy0[0] + nx * dx, nx)
    new_x = new_xy0[0] + dxc
    new_y = new_xy0[1] + dyc

    ds_reproj = ds_2d.copy()  # back with z dim if present
    ds_reproj['x'] = new_x
    ds_reproj['y'] = new_y[::-1]  # y is reversed order

    # reset to reduced grid
    ds_reproj = stack_coords(ds_reproj)
    if np.size(ds_reproj.zone.data) != np.size(ds.zone.data):
        ds_reproj = ds_reproj.dropna(dim='zone')

    # update attrs
    cf_attrs = crs.coordinate_system.to_cf()
    ds_reproj.attrs['crs'] = crs.to_cf()
    ds_reproj.x.attrs = cf_attrs[0]
    ds_reproj.y.attrs = cf_attrs[1]

    return ds_reproj


def reproj_grid(ds, from_epsg="EPSG:27572", to_epsg="EPSG:2154", engine='regrid', decimals=None):
    """  Transform the projection of a dataset using pyproj

    Warnings
    --------
    - (!) NaN should not have been removed before (full x,y,dx,dy are needed)
    - This is only valid for regular grids.
    - If used with 'rioxarray' mode, it should be only used for visualization purposes.
      For rewriting a Marthe grid with another projection, further tests are required.
    - This function is still EXPERIMENTAL and should be used with caution.

    Parameters
    ----------
    ds : xarray.Dataset
       Dataset to transform
    from_epsg : str
        EPSG code of input data
    to_epsg : str
        targeted EPSG code
    engine : str, optional
        Engine to use, either 'rioxarray' or 'regrid' (default)
    decimals : int, optional
        Number of decimals to round the coordinates to (default is None, not used).
        E.g use `decimals=0` to round at meters scale for EPSG 27572, 2154 (Lambert
        projections).

    Returns
    -------
    xarray.Dataset
        Dataset with new coordinates in the targeted projection
    """
    if engine.lower() in ['rioxarray', 'rasterio']:
        _check_rioxarray()
        grid_2d = assign_coords(ds) if 'x' not in ds.dims else ds.copy()
        ds_transf = grid_2d.rio.write_crs(from_epsg).rio.reproject(to_epsg)
        ds_transf = stack_coords(ds_transf)
    else:
        ds_transf = _transf_proj_regrid(ds, from_epsg, to_epsg, decimals)
    return ds_transf


def _single_grid_to_raster(da, x_dim, y_dim, epsg, fout):
    da = da.copy().rio.write_crs('epsg:{}'.format(epsg))
    da = da.rio.set_spatial_dims(x_dim=x_dim, y_dim=y_dim)
    da.rio.to_raster(fout)
    return None


def to_raster(
    ds,
    varname=None,
    x_dim='x',
    y_dim='y',
    time=None,
    epsg=27572,
    filename_tpl='raster'
):
    """ Write a xr.DataArray to a raster file

    Notes
    -----
    - Warning, only functionnal for regular grids
    - Requires rasterio/rioxarray packages
    - TODO: add support for irregular grids, using PostMARTHE QGIS plugin code.

    Parameters
    ----------
    ds : xarray.Dataset, xarray.DataArray
        The dataset/dataArray to write to a raster file
    x_dim : str, optional
        The name of the x dimension, by default 'x'.
    y_dim : str, optional
        The name of the y dimension, by default 'y'.
    time : str, list, optional
        time or list of time from `da.time`
    epsg : int, optional
        The EPSG code for the coordinate reference system, by default 27572.
    filename_tpl : str, optional
        The output file template for the raster file, by default 'raster'.
        Final name will be '{filename_tpl}_{time}.tiff'

    Returns
    -------
    None
        The function writes the raster file and returns None.
    """

    _check_rioxarray()

    if isinstance(ds, xr.Dataset):
        assert varname is not None, \
            'You need to provide a variable name to export when using a Dataset'
        da = ds[varname].copy()
    elif isinstance(ds, xr.DataArray):
        da = ds.copy()
    else:
        raise ValueError('ds is neither a xr.Dataset nor xr.DataArray')

    if 'time' not in da.dims:
        _single_grid_to_raster(
            da,
            x_dim, y_dim, epsg,
            f"{filename_tpl}.tiff"
        )
    else:
        if time is None:
            # if not defined, get all available times
            time = da.time
        elif isinstance(time, str):
            # make sure to get an iterable for slicing
            time = [time]

        for i, t in enumerate(time):
            _single_grid_to_raster(
                da.sel(time=t),
                x_dim, y_dim, epsg,
                # check for valid filename of time as string
                f"{filename_tpl}_{t}.tiff"
                # https://stackoverflow.com/a/47455094
                if re.match(r'^[^<>:;,?"*|/\\]+$', f"{filename_tpl}_{t}.tiff")
                # otherwise use integer index instead
                else f"{filename_tpl}_{i}.tiff"
            )

    return None
