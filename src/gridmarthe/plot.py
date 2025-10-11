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

from copy import copy

from matplotlib import pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib import (colors, cm)

import numpy as np
import xarray as xr
import geopandas as gpd

from .utils import _get_scale

# TODO: plot_section() # outil de coupe

""" Module for visualisation of gridmarthe files
"""


def _set_map_lims(ax, xmin, ymin, xmax, ymax, perc=.05):
    x_range = xmax - xmin
    y_range = ymax - ymin
    # and add 5% margin around bounds (2.5% on each side)
    ax.set_xlim([xmin - (perc * x_range)/2, xmax + (perc * x_range)/2])
    ax.set_ylim([ymin - (perc * y_range)/2, ymax + (perc * y_range)/2])
    return None


def plot_nested_grid(ds, ax=None, varname='charge', **kwargs):
    """ Usefull function to plot nested grids, keeping heterogeneous resolution
    
    Parameters
    ----------
    ds: xr.Dataset
        the dataset MUST be a 2D array, with dims = x,y.
        In other words, you may need to sel z and time before plot, and you need to apply `assign_coord()`
    
    ax: matplotlib axe, optional.
        if provided, data are plotted on this axis, otherwise fig, ax instances will be created.
    
    varname: str, optional
        the variable to plot in dataset. Default is 'charge'.
    
    kwargs: optional.
        any keywords argument from `xr.Dataset.plot.pcolormesh()`
    
    Returns
    -------
    ax: matplotlib axis.
    """
    da = ds.copy()
    
    if 'var' in kwargs.keys():
        # legacy, previous arg name was only var, harmonize between functions/methods
        varname = kwargs.pop('var')
    
    vmin, vmax = da[varname].min(), da[varname].max()
    vmin, vmax = kwargs.pop('vmin', vmin), kwargs.pop('vmax', vmax) # replace with user defined, if defined
    if kwargs.get('norm') is not None:
        vmin, vmax = None, None  # if user set a norm, vmin and vmax are not allowed
    cbar_kwargs = kwargs.pop('cbar_kwargs', {})
    
    # split grids
    dx, dy = _get_scale(da)
    dx1, dy1 = dx.pop(0), dy.pop(0)
    grid = da.where(da['dx'] == dx1, drop=True)
    
    if ax is None:
        fig, ax = plt.subplots()
    
    # plots nested then main
    for dx2, dy2 in zip(dx, dy):
        gig = da.where(da['dx'] == dx2, drop=True)
        gig[varname].plot.pcolormesh(
            x='x', y='y',
            ax=ax, vmin=vmin, vmax=vmax,
            add_colorbar=False,
            **{k:v for k,v in kwargs.items() if k != 'add_colorbar'}
        )
    
    grid[varname].plot.pcolormesh(x='x', y='y', ax=ax, vmin=vmin, vmax=vmax, cbar_kwargs=cbar_kwargs, **kwargs)
    
    _set_map_lims(ax, da.x.min().data, da.y.min().data, da.x.max().data, da.y.max().data)
    
    if str(da.time.values)[:10] == '1850-01-01':
        # remember: no slice on time because it must be selected before calling function
        ax.set_title(varname)  # remove default title from xarray API if dummy timestep (e.g plot parameters)
    
    return ax


def plot_mesh_time_serie(*arg, zone: int, varname='charge', show=False, figsize=(12,4), **kwargs):
    """ Usefull function to plot time serie from any dataset, by extracting a specific cell timeserie
    
    Parameters
    ----------
    
    arg: xr.Dataset,
        any datasets (you can pass multiple datasets, eg. `plot_mesh_time_serie(ds1, ds2, ds3, ... zone=32)`
    
    zone: int
        zone value (dimension) to select data
    
    varname: str, optional (default is 'charge')
        Variable to plot. Must be a key of all dataset passed as *arg.
    
    show: bool, optional.
        show plot using `plt.show()`
    
    figsize: tuple[int], optional.
        figsize argument for matplotlib.
    
    kwargs: any keywords argument for `xr.Dataset.plot()` method
    
    Returns
    -------
    ax: matplotlib axis.
    
    """
    fig, ax = plt.subplots(figsize=figsize)
    for da in arg:
        da[varname].sel(zone=zone).plot(ax=ax, **kwargs)
    ax.grid(True)
    if show:
        plt.show(block=False)
    return ax


def plot_outcrop(ds_outcrop, fig=None, ax=None, cbar_width='3', labels=None, file_out=None, show=False, **kwargs):
    """ Usefull function to plot outcrop layers of a marthe (multilayer) grid
    
    There is two mode implementend yet, using xr.plot or
    gpd.plot (useful for nested grid).

    To use this function, `ds` provided need to have a `z` variable (i.e model
    used need to be multilayer) and user need to assign coords before and **keep**
    the z dimension as a variable (see Note).
    
    Note
    ----
    - if input is a `xr.Dataset` instance, `ds_outcrop` need to get coords before
    but keep `z` as a variable (use `gm.assign_coords(ds_outcrop, add_lay=False)`)
    
    Parameters
    ----------
    ds_outcrop: xr.Dataset
        output of `gm.get_surface_mask()`
    
    fig: matplotlib figure, Optional.
        if provided, data are plotted on this figure, otherwise fig, ax instances will be created
    
    ax: matplotlib axe, Optional.
        if provided, data are plotted on this axis, otherwise fig, ax instances will be created
    
    cbar_width: str, Optional.
        width of colorbar, as a percentage of the main axis. Default is '3'
    
    labels: list, Optional.
        labels for layers in colorbar

    file_out: str, Optional.
        If not None (default), file name to write plot
    
    show: bool, Optional.
        Show result (`plt.show()`), default is False.
    
    kwargs: dict, Optional.
        Any keywords argument to pass to either `xarray.Dataset.plot.pcolormesh()`
        or `geopandas.GeoDataFrame.plot()`.
    
    Returns
    -------
    fig, ax, ax_cbar if not `show`, otherwise return None
    
    Example
    -------
    xarray version:

    >>> ds_surf = gm.get_surface_layer(ds)
    >>> gm.plot_outcrop(gm.assign_coords(ds_surf, add_lay=False))

    geopandas version:

    >>> ds_surf = gm.get_surface_layer(ds)
    >>> gm.plot_outcrop(gm.to_geodataframe(ds_surf))
    """
    if isinstance(ds_outcrop, xr.Dataset):
        assert 'z' in ds_outcrop.keys(), "No `z` dimension. Outcrop plot is not possible."
        maxn = np.nanmax(ds_outcrop['z'].data)
        engine = 'xr'
    elif isinstance(ds_outcrop, gpd.geodataframe.GeoDataFrame):
        assert 'z' in ds_outcrop.columns, "No `z` dimension. Outcrop plot is not possible."
        maxn = np.nanmax(ds_outcrop['z'].to_numpy())
        engine = 'gpd'

    # custom cbar to force categories
    cmap = kwargs.pop('cmap', None)
    norm = kwargs.pop('norm', None)
    
    if cmap is None:
        cmap = cm.tab10 if maxn <= 10 else cm.tab20
        cmap = colors.ListedColormap(cmap.colors[:int(maxn)])  # subset on number of colors, if not wrong legend
    
    if norm is not None:
        bounds = norm.boundaries
    else:
        bounds = np.arange(1, maxn+2)
        if len(bounds) == 1:
            bounds = np.append(bounds, [maxn+1])
        norm = colors.BoundaryNorm(bounds, cmap.N)  # set bins to custom values
    
    sm = plt.cm.ScalarMappable(norm=norm, cmap=cmap)
    
    # Create the figure and axes, with a place for colorbar
    if fig is None or ax is None:
        fig, ax = plt.subplots(1, 1)
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="{}%".format(cbar_width), pad=0.1)
    
    if engine == 'xr':
        the_plot = plot_nested_grid(
            ds_outcrop, var='z',
            ax=ax,
            cmap=cmap,
            levels=bounds,
            add_colorbar=False,
            **kwargs
        )
    
    elif engine == 'gpd':
        
        ds_outcrop.plot(
            column='z',
            ax=ax,
            cax=cax,
            cmap=cmap,
            legend=False,
            norm=norm,
            **kwargs
        )
    
    ax_cbar = fig.colorbar(
        sm, ax=ax, cax=cax,
        orientation='vertical',
        ticks=[x+0.5 for x in bounds], # set labels in the middle of class
        label='Layers',
    )
    ax_cbar.ax.tick_params(size=0)
    
    _labels = copy(labels)
    if _labels is None:
        _labels = ['{:.0f}'.format(x) for x in bounds]
    if len(_labels) != len(bounds):
        _labels = _labels + ['none']
    ax_cbar.set_ticklabels(_labels)
    ax_cbar.ax.invert_yaxis()
    
    if file_out is not None:
        plt.savefig(file_out, dpi=300)
    if show:
        plt.show()
        plt.close()
        return None
    else:
        return fig, ax, ax_cbar
