#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest

import numpy as np
import xarray as xr

import gridmarthe as gm


def test_create_grid_nx_ny():
    # Create grid with explicit dimensions - recreate hallue grid
    grid = gm.create_grid_domain(
        x0=596.5, y0=2542, nx=53, ny=54, dx=0.5, dy=0.5, nlayer=1
    )

    assert isinstance(grid, xr.Dataset)
    assert len(grid.zone) == 54 * 53

    # Check coordinates (center of cells)
    assert grid.x[0] == 596.5 + 0.5/2
    assert grid.y[-1] == 2542 + 0.5/2  # cause y is reversed
    assert grid.z[0] == 1

    # load true grid and compare
    true_grid = gm.load_marthe_grid('tests/data/hallue.permh')
    # assert grid.equals(true_grid)
    assert np.allclose(grid.x, true_grid.x)
    assert np.allclose(grid.y, true_grid.y)
    # assert np.allclose(grid.z, true_grid.z)
    assert np.allclose(grid.dx, true_grid.dx)
    assert np.allclose(grid.dy, true_grid.dy)

    # write new grid
    status = gm.write_marthe_grid(grid, './tests/tmp_outputs/new_grid.out', varname='permeab')
    assert status == 0, 'cannot write new grid'


def test_create_grid_x1_y1():
    # Create grid with bounding box
    grid = gm.create_grid_domain(
        x0=0, y0=0, x1=1000, y1=1000, dx=100, dy=50
    )

    assert isinstance(grid, xr.Dataset)
    assert len(grid.zone) == 10 * 20

    # Check coordinates (center of cells)
    assert grid.x[0] == 0 + 100/2
    assert grid.y[-1] == 0 + 50/2
    assert grid.z[0] == 1

def test_create_grid_nx_ny_multilayer():
    grid = gm.create_grid_domain(
        x0=0.0, y0=0.0, nx=5, ny=5, dx=2.0, dy=2.0, nlayer=3
    )
    
    true_grid = gm.load_marthe_grid('tests/data/test_grid_nogig.permh')
  
    grid = grid.astype(true_grid.dtypes)  # Ensure same dtypes for comparison
    assert (grid.equals(true_grid))
    
    # add nested grid all layers
    nested_grid = gm.add_zoom(grid, x0_zoom=2.0, y0_zoom=2.0,
                              x1_zoom=6.0, y1_zoom=8.0, xfactor=2,
                              yfactor=2)
    
    true_nested_grid = gm.load_marthe_grid('tests/data/test_grid_gig.permh')
    nested_grid = nested_grid.astype(true_nested_grid.dtypes)
    assert (nested_grid.equals(true_nested_grid))

    # write new grid
    status = gm.write_marthe_grid(grid, './tests/tmp_outputs/new_grid.out', varname='permeab')
    assert status == 0, 'cannot write new grid'

def test_create_grid_from_shape():
    grid = gm.create_grid_from_shape('tests/data/test_grid_creation.shp', dx=500,dy=500, nlayer=2)
    
    # write new grid
    status = gm.write_marthe_grid(grid, './tests/tmp_outputs/new_grid.out', varname='permeab')
    assert status == 0, 'cannot write new grid'
    
    
    # add nested grid
    zooms = [
        {
            'shape': 'tests/data/test_grid_creation_zoom1.gpkg',
             'xfactor': 2,
             'yfactor': 2,
             'default_value': 1
         },
        {
            'shape': 'tests/data/test_grid_creation_zoom2.gpkg',
             'xfactor': 5,
             'yfactor': 5,
             'default_value': 1
         }        
        ]
    nested_grid = gm.add_zoom_from_shape(grid=grid, zooms=zooms) 
    status = gm.write_marthe_grid(nested_grid, './tests/tmp_outputs/new_nested_grid.out', varname='permeab')
    assert status == 0, 'cannot write new nested grid'
        

def test_missing_params():
    with pytest.raises(ValueError):
        gm.create_grid_domain(x0=0, y0=0, dx=10, dy=10) # Missing nx/ny/x1/y1


if __name__ == "__main__":
    test_create_grid_nx_ny()
    test_create_grid_x1_y1()
    test_missing_params()
    test_create_grid_nx_ny_multilayer()
    test_create_grid_from_shape()
