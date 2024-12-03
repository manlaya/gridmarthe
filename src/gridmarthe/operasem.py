#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import xarray as xr #needs netcdf4, rioxarray

from shapely.geometry import Polygon
import geopandas as gpd

from .utils import _get_scale, _nearest_node

"""
Some useful functions to manage MartheGrid in python
"""
# TODO:   add functions available in winmarthe or operasem.
#         eg. get_layer_depths(), get_layer_thickness(),
#         get_runoff_direction(), remove_layer(), remove_nested(), etc.

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

def coarse_nested_grid(da, varname='charge', dx=None, dy=None):
    """ Coarse nested grid to res of main grid
    only realy valid if nested grid resolution is a multiple of maingrid resolution
    coords needs to be assign first
    """
    if dx is None or dy is None:
        dx, dy = _get_scale(da)
    dx1, dy1 = dx.pop(0), dy.pop(0)
    grid = da.where(da['dx'] == dx1, drop=True) # & da['dy'] == dy1
    for dx2, dy2 in zip(dx, dy):
        gig = da.where(da['dx'] == dx2, drop=True)
        gig = gig[varname].coarsen(x=int(dx1/dx2), y=int(dy1/dy2), boundary='trim').mean()
        grid = xr.combine_by_coords([grid, gig])
    return grid

def interp_grid(da, new_x=None, new_y=None, method='nearest', **kwargs):
    """ Interpolate on a new grid using `xarray.Dataset.interp`

    Parameters
    ----------
    da: xr.Dataset
        the input dataset to interpolate on new coordinates.
    new_x: array-like
        the new x-axis coordinate to use
    new_y: array-like
        the new y-axis coordinate to use
    method: str, Optionnal (default='nearest')
        `xr.Dataset.interp` method to use. Default is 'nearest'
    **kwargs: dict, Optionnal.
        Any keywords argument to pass to `xr.Dataset.interp`.
    
    Returns
    -------
        interpolated xr.Dataset
    """
    # https://docs.xarray.dev/en/stable/user-guide/interpolation.html
    # https://earth-env-data-science.github.io/lectures/xarray/xarray-part2.html
    if new_x is None or new_y is None:
        new_x = np.linspace(da['x'][0], da['x'][-1], int(da['x'].size / 2) ) # da.dims["lat"]
        new_y = np.linspace(da['y'][0], da['y'][-1], int(da['y'].size / 2) )
    return da.interp(x=new_x, y=new_y, method=method, **kwargs)

def rescale(da, res=1000, **kwargs):
    """ Wrapper function that uses `get_new_coords()` and `interp_grid()` together
    
    See also
    --------
    `get_new_coords`
    `interp_grid`
    """
    new_x, new_y = get_new_coords(da, res)
    new_da = interp_grid(da, new_x, new_y, **kwargs) # here da with assign coords
    return new_da

def get_min_layer(ds, aquif_layers=None):
    """ Compute surface mask of marthe domain
    
    This function return min layer for every zone of a grimarthe dataset with z coords
    A subset on specific (aquifers) layers can be performed with `aquif_layers`.
    if set, aquif_layers must be a sequence (list, tuple, array) of layer (list of int).
    
    This should be used to get a surface mask, ie get zone to filter a dataset.
    
    Examples
    --------
    >>>    mask = get_min_layer(ds, [6,8,9])
    >>>    ds_surf = ds.sel(zone=mask.zone.data)
        
    Parameters
    ----------
        ds: xr.Dataset
        aquif_layers: sequence (list, tuple, array) of int
            representing layers to subset ds
    Returns
    -------
        surface_mask: xr.Dataset
    """
    df = ds.to_dataframe()
    df = df.reset_index()
    
    if aquif_layers is not None:
        df = df[df['z'].isin(aquif_layers)]
    
    idx_z_min = df.groupby(['x', 'y', 'time']).z.idxmin() # get index of min z ("layer") for each x,y,t groups
    first_aquif_lay = df.loc[idx_z_min].reset_index().set_index('zone').drop('index', axis=1)
    # time not needed here, zone are independant from time coords
    return first_aquif_lay.to_xarray()


def get_mask(ds, varname: str='permeab', nanval: list=[-9999., 0.], fileout: str='mask.shp'):
    """ Filter dataset on non-nan values, and dissolve results to get a mask shape 
    input ds should be the permh dataset (read from permh file, ie Horizontal hydraulic conductivity)
    """
    mask = ds.where(~ds[varname].isin(nanval), drop=True)
    mask = ds.sel(zone=mask['zone'])
    gdf  = to_geodataframe(mask)
    gdf  = gdf.dissolve()
    gdf.to_file(fileout)
    return gdf


def search_zone(ds, i=None, j=None, x=None, y=None, z=None):
    """ search zone number in marthe grid,
    based on xy or ij (col, lig)
    
    if ds is multilayered, you need to provide the layer you want (int)
    ds should contains dx and dy
    ds should not have assigned coords (x and y are variables, zone is the dimension coordinates (with time))
    """
    ds_search = ds.copy()
    
    if z is not None:
        ds_search = ds_search.where(ds_search.z == z, drop=True)

    if x is not None:
        assert y is not None, 'if x is provided, y cannot be None'
        ## mask = ds.sel(x=x, y=y, method='nearest') # possible uniquement si x,y sont des coordonnées/dim
        nearest = _nearest_node(np.array([(x, y)]), np.array(list(zip(ds_search['x'].data, ds_search['y'].data))))
        nearest_zone = ds_search.isel(zone=nearest)
        
        # check if xy is in a cell == dx and dy are not greater than grid resolution
        dx = np.abs(nearest_zone.x.data - x)
        dy = np.abs(nearest_zone.y.data - y)
        mask = ds_search['zone'] == nearest_zone.zone if (dx <= nearest_zone.dx.data) & (dy <= nearest_zone.dy.data) else ds_search['zone'].isnull()

    if i is not None:
        assert j is not None, 'if i is provided, j cannot be None'
        mask = (ds_search['col'] == i) & (ds_search['lig'] == j)

    # zone = ds.where(mask, drop=True)['zone'].data
    zone = ds_search.where(mask, drop=True)
    return zone

# -------------------------------------------------------- #
#                      GIS Functions                       #
# -------------------------------------------------------- #

def subset_with_coords(da, dims=['x', 'y'], gdf=None, xmin=None, ymin=None, xmax=None, ymax=None):
    """
    subset DataArray or Dataset with gpd.GeoDataFrame or bounds
    TODO: real shp clip
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


def _mk_cell_polygon(xleft, ylower, xright, yupper):
    return Polygon(
        (
            (xleft , ylower),
            (xright, ylower),
            (xright, yupper),
            (xleft , yupper),
            (xleft , ylower)
        )
    )

_polygonize = np.vectorize(_mk_cell_polygon)


def _build_polyg(ds):
    """ build a (rectangular) polygon shape from marthegrid dataset """
    
    x0 = ds.x.values - (ds.dx.values / 2.)
    y0 = ds.y.values - (ds.dy.values / 2.)
    x1 = ds.x.values + (ds.dx.values / 2.)
    y1 = ds.y.values + (ds.dy.values / 2.)
    
    return _polygonize(x0, y0, x1, y1)


def to_geodataframe(ds, epsg='EPSG:27572', fmt='long'):
    """ Convert marthegrid.Dataset to a geodataframe 
    fmt must be long or wide, default is long
    """
    
    polygons = _build_polyg(ds.isel(time=0))
    df = ds.to_dataframe() #.to_pandas() # only for 1 dim
    
    if 'time' in ds.dims.keys():
        polygons = np.tile(polygons.flatten(), len(np.unique(df.index.get_level_values('time')))) # ad geom for every timestep
    
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

