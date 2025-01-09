#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from .gridmarthe import *
from .operasem import *
from .plot import plot_nested_grid, plot_outcrop

from typing import Union

from .__version__ import __version__


@xr.register_dataset_accessor('mart')
class MartheGrid(object):
    """ A Marthe grid attributes/methods accessor for xarray.Dataset objects
    
    Example
    --------
    >>> ds = gm.load_marthe_grid(**kwargs)
    >>> ds.mart.dropna('permeab', 0.)
    
    """
    def __init__(self, xr_obj: Union[xr.Dataset, None] = None):
        self.obj = xr_obj
    
    def assign_coords(self, add_lay=True):
        return assign_coords(self.obj, add_lay)
    
    def stack_coords(self, coords=['z', 'y', 'x']):
        return stack_coords(self.obj, coords)
    
    def to_geodataframe(self, epsg='EPSG:27572', fmt='long'):
        # from .mgrid_utils import to_geodataframe
        return to_geodataframe(self.obj, epsg, fmt)
    
    def to_recarray(self):
        """ return a np.recarray from pymarthe compatibility """
        # TODO, add pymarthe requested informations (i, j, etc.) => grid should be read with `add_grid_id`, and `keep_col` options.
        df = self.obj.to_dataframe()
        return df.to_records()
    
    def to_raster(self, x_dim='x', y_dim='y', time=None, epsg=27572, fout_template='raster'):
        """ Write raster file for a specific timestep (or all) from dataset 
        Warning, only functionnal for regular grids
        """
        if time is None:
            time = self.obj.times # if not defined, get all available times
        if isinstance(time, str): # make sure to get a iterable for slicing
            time = [time]
        
        for t in time:
            write_raster_from_da(self.obj.sel(time=slice(t)), x_dim, y_dim, epsg, "{}_{}.tiff".format(fout_template, t))
        
        return None
    
    def get_outcrop(self, subset_layers=None):
        return get_min_layer(self.obj, subset_layers)
    
    def subset_coords(self, dims=['x', 'y'], gdf=None, xmin=None, ymin=None, xmax=None, ymax=None):
        return subset_with_coords(self.obj, dims, gdf, xmin, ymin, xmax, ymax)
    
    def dropna(self, varname='charge', nanval=9999.):
        ds = self.obj.copy()
        masque = ds[varname].where(ds[varname] != nanval).dropna(dim='zone') # drop nanval
        return ds.sel(zone=masque['zone'])
    
    # def write(self, fmt='mart'):
        # if fmt.lower() in ['mart', 'marthe']
            # write_marthe_grid()
        # else:
            # self.obj.to_netcdf()
