#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np

from shapely.geometry import Polygon
from pyproj import Transformer
import geopandas as gpd

from ..utils import assign_coords


def transf_proj(ds, from_epsg="EPSG:27572", to_epsg="EPSG:2154"):
    """ Transform coordinates of a dataset using pyproj.
    """
    transformer = Transformer.from_crs(from_epsg, to_epsg, always_xy=True)
    x_source, y_source = ds.x.data, ds.y.data
    x_target, y_target = transformer.transform(x_source, y_source)
    ds = ds.copy()
    ds['x'].data, ds['y'].data = np.astype(x_target, np.float32), np.astype(y_target, np.float32)
    ds.attrs['projection'] = to_epsg
    return ds


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
    
    polygons = _build_polyg(ds) # .isel(time=0) # x,y does not vary in time
    df = ds.to_dataframe() #.to_pandas() # only for 1 dim
    
    if 'time' in ds.dims.keys():
        polygons = np.tile(polygons.flatten(), len(np.unique(df.index.get_level_values('time')))) # ad geom for every timestep
    
    gdf = gpd.GeoDataFrame(
        df,
        geometry=polygons,
        crs=epsg
    )
    
    if fmt == "wide" and 'time' in ds.dims.keys():
        # here no wide fmt if no time, so no if 'time' in ds.dims.keys():
        gdf = gdf.unstack('time')
        gdf.columns = [
            '{}_{}'.format(x, y.strftime('%Y%m%d'))\
            if x not in ['x', 'y', 'dx', 'dy', 'z', 'geometry'] else x\
            for x, y in gdf.columns
        ]
        gdf = gdf.loc[:,~gdf.columns.duplicated()].copy()  # drop duplicated cols
        gdf = gdf.set_geometry('geometry')  # need to make again geom after drop dupl
    
    return gdf


def clip_dataset(ds, gdf, crs=27572, engine='gdf'):
    """ Clip a xarray Dataset with a gpd.GeoDataFrame
    Needs rioxarray
    See: https://corteva.github.io/rioxarray/html/examples/clip_geom.html
    Todo: shapely version
    """
    shp = gdf.to_crs(crs)
    da  = assign_coords(ds.rio.write_crs("EPSG:{}".format(crs)))
    clipped_da = da.rio.clip(shp.geometry.values, shp.crs, drop=True)
    return clipped_da


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



def write_raster_from_da(da, x_dim='x', y_dim='y', epsg=27572, fout='raster.tiff'):
    """ Write a xr.DataArray to a raster file
    need xarray with rioxarray installed
    """
    da = da.copy().rio.write_crs('epsg:{}'.format(epsg))
    da = da.rio.set_spatial_dims(x_dim=x_dim, y_dim=y_dim)
    da.rio.to_raster(fout)
    return None

