#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gridmarthe as gm
import matplotlib.pyplot as plt
import numpy as np

from pyproj import Transformer

import xarray as xr
import rioxarray as rio
# import rasterio

def transf_proj(ds, from_epsg="EPSG:27572", to_epsg="EPSG:2154"):
    """ Transform coordinates of a dataset using pyproj.
    /!\ return more unique points than initial.
    """
    transformer = Transformer.from_crs(from_epsg, to_epsg, always_xy=True)
    x_source, y_source = ds.x.data, ds.y.data
    x_target, y_target = transformer.transform(x_source, y_source)
    ds = ds.copy()
    ds['x'].data = np.round(np.astype(x_target, np.float32))
    ds['y'].data = np.round(np.astype(y_target, np.float32))
    ds.attrs['projection'] = to_epsg
    return ds

def transf_proj2(ds, from_epsg="EPSG:27572", to_epsg="EPSG:2154"):
    """ Transform coordinates of a dataset using pyproj.
    /!\ recreate a regular grid in dest epsg
    """
    x, y = np.unique(ds['x'].data), np.unique(ds['y'].data)
    nx, ny = len(x), len(y)
    x0, y0 = np.nanmin(x), np.nanmin(y)
    x1, y1 = np.nanmax(x), np.nanmax(y)
    dx, dy = ds['dx'].data, ds['dy'].data

    transformer = Transformer.from_crs(from_epsg, to_epsg, always_xy=True)
    # Transformer uniquement les bornes de la grille
    x0n, y0n = transformer.transform(x0, y0)
    x1n, y1n = transformer.transform(x1, y1)
    
    # Recreate regular grid
    x_reg = np.linspace(x0, x1, ds.x.size)
    y_reg = np.linspace(y0, y1, ds.y.size)

    ds = ds.copy()
    ds['x'].data = np.round(np.astype(x_reg, np.float32), 2)
    ds['y'].data = np.round(np.astype(y_reg, np.float32), 2)
    ds.attrs['projection'] = to_epsg

    # version meshgrid
    xx, yy = np.meshgrid(x, y)
    xx_transformed, yy_transformed = transformer.transform(xx, yy)

    # Recréer la grille avec les nouvelles coordonnées
    data_transformed = xr.DataArray(
        gm.assign_coords(ds)['permeab'].data,
        dims=["y", "x"],
        coords={"y": yy_transformed[:, 0], "x": xx_transformed[0, :]}
    )

    return ds



grid = gm.load_marthe_grid('./data/hallue.permh', xyfactor=1e3, drop_nan=True)
grid = gm.load_marthe_grid('./data/Somme_V3_Surfex.permh', xyfactor=1e3, drop_nan=True, nanval=[-9999.,0.])
grid = gm.load_marthe_grid('./data/craie_npc.permh', drop_nan=True)

# grid_2154 = transf_proj2(grid, 'EPSG:27572', 'EPSG:2154')
# len(np.unique(grid['x'].data))
# len(np.unique(grid_2154['x'].data))

g2d = gm.assign_coords(grid) #.where(grid['z']==6, drop=True)
# rio
g2d_2154 = g2d.rio.write_crs('EPSG:27572').isel(time=0).rio.reproject("EPSG:4326")
# g2d_2154.to_netcdf('toto.nc', engine='h5netcdf')


fig, ax = plt.subplots(ncols=2, figsize=(10,4))
gm.plot_nested_grid(g2d.isel(time=0), var='permeab', ax=ax[0], add_colorbar=False)
gm.plot_nested_grid(g2d_2154, var='permeab', ax=ax[1])
plt.show()

# np.unique(g2d_2154['dy'].data)