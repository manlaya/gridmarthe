#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import xarray as xr #needs netcdf4, rioxarray

from shapely.geometry import Polygon
import geopandas as gpd

from .utils_mgrid import get_scale

"""
Some useful functions to manage MartheGrid in python

TODO:   make it a real new operasem
        (add functions available in winmarthe or operasem,
        eg. get_layer_depths(), get_layer_thickness())
"""

# -------------------------------------------------------- #
#  Operation on Marthe Grids (semis, marthe easter eggs).  #
# -------------------------------------------------------- #

def get_new_coords(ds, res=1000):
    """ Reset xy with a range from min to max, with res as step"""
    xmin, xmax = np.min(ds.x).values, np.max(ds.x).values
    ymin, ymax = np.min(ds.y).values, np.max(ds.y).values
    
    new_x = np.arange(xmin, xmax+res, res)
    new_y = np.arange(ymin, ymax+res, res)
    
    return new_x, new_y

def coarse_nested_grid(da, varname='charge'):
    """ Coarse nested grid to res of main grid
    only realy valid if nested grid resolution is a multiple of maingrid resolution
    coords needs to be assign first
    """
    dx, dy = get_scale(da)
    dx1, dy1 = dx.pop(0), dy.pop(0)
    grid = da.where(da['dx'] == dx1, drop=True) # & da['dy'] == dy1
    for dx2, dy2 in zip(dx, dy):
        gig = da.where(da['dx'] == dx2, drop=True)
        gig = gig[varname].coarsen(x=int(dx1/dx2), y=int(dy1/dy2), boundary='trim').mean()
        grid = xr.combine_by_coords([grid, gig])
    return grid

def interp_grid(da, new_x=None, new_y=None, method='nearest', **kwargs):
    # https://docs.xarray.dev/en/stable/user-guide/interpolation.html
    # https://earth-env-data-science.github.io/lectures/xarray/xarray-part2.html
    if new_x is None or new_y is None:
        new_x = np.linspace(da['x'][0], da['x'][-1], int(da['x'].size / 2) ) # da.dims["lat"]
        new_y = np.linspace(da['y'][0], da['y'][-1], int(da['y'].size / 2) )
    return da.interp(x=new_x, y=new_y, method=method, **kwargs)

def rescale(da, res=1000, **kwargs):
    new_x, new_y = get_new_coords(da, res)
    new_da = interp_grid(da, new_x, new_y, **kwargs) # here da with assign coords
    return new_da

def get_min_layer(ds, aquif_layers=None):
    """ return min layer for every zone of a grimarthe dataset with z coords 
    allow subset on aquifer layers
    if set, aquif_layers must be a sequence (list, tuple, array)
    """
    df = ds.to_dataframe()
    df.reset_index(inplace=True)
    
    if aquif_layers is not None:
        df = df[df['z'].isin(aquif_layers)]
    
    idx_z_min = df.groupby(['x', 'y', 'time']).z.idxmin() # get index of min z ("layer") for each x,y,t groups
    first_aquif_lay = df.loc[idx_z_min].reset_index().set_index('zone')
    # time not needed here, zone are independant from time coords
    return first_aquif_lay.to_xarray()

# -------------------------------------------------------- #
#                      GIS Functions                       #
# -------------------------------------------------------- #

def subset_with_coords(da, dims=['x', 'y'], gdf=None, xmin=None, ymin=None, xmax=None, ymax=None):
    """
    subset DataArray or Dataset with gpd.GeoDataFrame or bounds
    """
    if gdf is not None:
        # edit, one line with total_bounds attribute instead of bounds
        # xmin, ymin, xmax, ymax = gdf.bounds.T.values # or .T.to_numpy(), in any case return np.array // total_bounds instead of bounds
        # xmin, ymin, xmax, ymax = xmin[0], ymin[0], xmax[0], ymax[0]
        xmin, ymin, xmax, ymax = gdf.total_bounds #gdf.bounds.T.values # or .T.to_numpy(), in any case return np.array // total_bounds instead of bounds
    else:
        assert xmin is not None, "When using manual bounds, all must be set"
        assert xmax is not None, "When using manual bounds, all must be set"
        assert ymin is not None, "When using manual bounds, all must be set"
        assert ymax is not None, "When using manual bounds, all must be set"
    
    mask_lon = ( da[dims[0]] >= xmin) & ( da[dims[0]] <= xmax) #da.xc
    mask_lat = ( da[dims[1]] >= ymin) & ( da[dims[1]] <= ymax)
    
    # imin, imax = np.where(da[var[0]].values==xmin)[0], np.where(da[var[0]].values==xmax)[0]
    # jmin, jmax = np.where(da[var[1]].values==ymin)[0], np.where(da[var[1]].values==ymax)[0]

    # sub_da = da.isel(i=slice(int(imin), int(imax)+1), j=slice(int(jmax), int(jmin)+1)) # j in reverse order / +1 on imax, jmin because upper is exclude in py slicing
    
    return da.where(mask_lon & mask_lat, drop=True)


def build_polyg(ds):
    """ build a (rectangular) polygon shape from marthegrid dataset """
    
    x0 = ds.x.values - (ds.dx.values / 2.)
    y0 = ds.y.values - (ds.dy.values / 2.)
    x1 = ds.x.values + (ds.dx.values / 2.)
    y1 = ds.y.values + (ds.dy.values / 2.)
    
    def mk_cell_polygon(xleft, yleft, xright, yright):
        return Polygon(
            (
                (xleft , yleft ),
                (xright, yleft ),
                (xright, yright),
                (xleft , yright),
                (xleft , yleft )
            )
        )
    polygonize = np.vectorize(mk_cell_polygon)
    return polygonize(x0, y0, x1, y1)



def to_geodataframe(ds, epsg='EPSG:27572', fmt='long'):
    """ Convert marthegrid.Dataset to a geodataframe 
    fmt must be long or wide, default is long
    """
    
    polygons = build_polyg(ds)
    df = ds.to_dataframe() #.to_pandas() # only for 1 dim
    if 'time' in ds.dims.keys():
        polygons = np.tile(polygons, len(np.unique(df.index.get_level_values('time')))) # ad geom for every timestep
    gdf = gpd.GeoDataFrame(
        df,
        geometry=polygons,
        crs=epsg
    )
    
    if fmt == "wide":
        # here no wide fmt if no time, so no if 'time' in ds.dims.keys():
        gdf = gdf.unstack('time')
        gdf.columns = [
            '{}_{}'.format(x, y.strftime('%Y%m%d'))\
            if x not in ['x', 'y', 'dx', 'dy', 'z', 'geometry'] else x\
            for x, y in gdf.columns
        ]
        gdf = gdf.loc[:,~gdf.columns.duplicated()].copy() # drop duplicated cols
        gdf = gdf.set_geometry('geometry') # need to make again geom after drop dupl
    
    return gdf

def write_raster_from_da(da, x_dim='x', y_dim='y', epsg=27572, fout='raster.tiff'):
    """ Write a xr.DataArray to a raster file
    need xarray with rioxarray installed
    """
    da = da.copy().rio.write_crs('epsg:{}'.format(epsg))
    da = da.rio.set_spatial_dims(x_dim=x_dim, y_dim=y_dim)
    da.rio.to_raster(fout)
    return None

