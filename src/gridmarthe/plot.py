from matplotlib import pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib import (colors, cm)

import numpy as np
import xarray as xr
import geopandas as gpd

from .utils_mgrid import get_scale

# TODO: plot_section() # outil de coupe

def plot_nested_grid(da, ax=None, var='charge', **kwargs):
    """ da MUST be a 2D array, with dims = x,y. In other words, you may need to sel z and time before plot"""
    
    vmin, vmax = da[var].min(), da[var].max()
    vmin, vmax = kwargs.pop('vmin', vmin), kwargs.pop('vmax', vmax) # replace with user defined, if defined
    cbar_kwargs = kwargs.pop('cbar_kwargs', {})
    
    # split grids
    dx, dy = get_scale(da)
    dx1, dy1 = dx.pop(0), dy.pop(0)
    grid = da.where(da['dx'] == dx1, drop=True)
    
    if ax is None:
        fig, ax = plt.subplots()
    
    # plots nested then main
    for dx2, dy2 in zip(dx, dy):
        gig = da.where(da['dx'] == dx2, drop=True)
        gig[var].plot.pcolormesh(x='x', y='y', ax=ax, vmin=vmin, vmax=vmax, add_colorbar=False, **kwargs)
    grid[var].plot.pcolormesh(x='x', y='y', ax=ax, vmin=vmin, vmax=vmax, cbar_kwargs=cbar_kwargs, **kwargs)
    
    return ax

def plot_outcrop(ds_outcrop, fout=None, engine='xr'):
    
    """ plot outcrop layers
    two mode : xr.plot or gpd.plot (useful for nested grid)
    TODO xr version for nested with `plot_nested_grid()`, see func below in src

    if engine == 'xr' => ds_outcrop need to get coords before (use `gm.assign_coords(ds_outcrop, add_lay=False)`)
    if engine == 'gpd => ds_outcrop need to be a gpd.GeoDataframe (use `gm.to_geodataframe(ds_outcrop)`)

    """
    if isinstance(ds_outcrop, xr.Dataset):
        assert 'z' in ds_outcrop.keys(), "No `z` dimension. Outcrop plot is not possible."
        maxn = np.max(ds_outcrop['z'].data)
    elif isinstance(ds_outcrop, gpd.GeoDataframe):
        assert 'z' in ds_outcrop.columns, "No `z` dimension. Outcrop plot is not possible."
        maxn = np.max(ds_outcrop['z'].to_numpy())

    # custom cbar to force categories
    cmap = cm.tab10 if maxn <= 10 else cm.tab20
    cmap = colors.ListedColormap(cmap.colors[:maxn]) # subset on number of colors, if not wrong legend
    bounds = np.arange(1, maxn+1)
    norm = colors.BoundaryNorm(bounds, cmap.N,)  # set bins to custom values
    cbar = plt.cm.ScalarMappable(norm=norm, cmap=cmap)
    
    fig, ax = plt.subplots(1, 1)
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.1)
    
    if engine == 'xr':
        the_plot = ds_outcrop['z'].plot.pcolormesh(
            x='x', y='y',
            ax=ax,
            cmap=cmap,
            levels=bounds,
            add_colorbar=False,
        )
    elif engine == 'gpd':
        
        ds_outcrop.plot(
            column='z',
            ax=ax,
            cax=cax,
            cmap=cmap,
            legend=False,
            norm=norm,
        )
    
    ax_cbar = fig.colorbar(
        cbar, ax=ax, cax=cax,
        orientation='vertical',
        ticks=[x+0.5 for x in bounds], # set labels in the middle of class
        label='Layers',
    )
    ax_cbar.ax.tick_params(size=0)
    ax_cbar.set_ticklabels(bounds)
    
    if fout is not None:
        plt.savefig(fout, dpi=300)
    plt.show()
    plt.close()
    return None
