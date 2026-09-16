#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import xarray as xr
import gridmarthe as gm
from gridmarthe.grid.io.gridmarthe import get_dims_from_attrs, reset_geometry


DATA_PATH = './tests/data'


def test_get_dims_from_attrs_simple():
    """Test get_dims_from_attrs with a simple grid"""
    permh_file = f'{DATA_PATH}/hallue.permh'
    ds = gm.load_marthe_grid(permh_file, varname='PERMEAB')

    dims = get_dims_from_attrs(ds)
    assert dims is not None, 'Dimensions should not be None'
    assert isinstance(dims, np.ndarray), 'Dimensions should be a numpy array'
    assert len(dims) >= 1, 'Should have at least main grid dimensions'
    assert len(dims[0]) == 3, 'Each grid should have 3 dimensions (x, y, z)'


def test_get_dims_from_attrs_nested():
    """Test get_dims_from_attrs with nested grids"""
    permh_file = f'{DATA_PATH}/Somme_V3_Surfex.permh'
    ds = gm.load_marthe_grid(permh_file, varname='PERMEAB')

    dims = get_dims_from_attrs(ds)
    assert dims is not None, 'Dimensions should not be None'
    assert isinstance(dims, np.ndarray), 'Dimensions should be a numpy array'
    # Nested grid should have multiple entries
    assert len(dims) >= 1, 'Should have at least main grid dimensions'
    assert dims.shape == (4,3)


def test_get_dims_from_attrs_multilayer():
    """Test get_dims_from_attrs with multilayer grid"""
    permh_file = f'{DATA_PATH}/craie_npc_gig.permh'
    ds = gm.load_marthe_grid(permh_file, varname='PERMEAB')

    dims = get_dims_from_attrs(ds)
    assert dims is not None, 'Dimensions should not be None'
    assert isinstance(dims, np.ndarray), 'Dimensions should be a numpy array'
    # Check that z dimension > 1 for multilayer
    assert dims[0][2] > 1, 'First grid should have multiple layers'


def test_get_dims_from_attrs_format():
    """Test that dimensions are in correct format (list of lists of ints)"""
    permh_file = f'{DATA_PATH}/hallue.permh'
    ds = gm.load_marthe_grid(permh_file, varname='PERMEAB')

    dims = get_dims_from_attrs(ds)
    dims = np.array(dims)
    assert np.issubdtype(dims.dtype, np.integer)


def test_reset_geometry_basic():
    """Test reset_geometry with a dataset that had NaN dropped"""
    permh_file = f'{DATA_PATH}/hallue.permh'

    # Load with dropna to create a subset
    ds = gm.load_marthe_grid(permh_file, varname='PERMEAB')
    ds_subset = gm.load_marthe_grid(permh_file, varname='PERMEAB', drop_nan=True)
    original_size = len(ds_subset.zone.data)

    # Reset geometry using the full permh file
    ds_reset = reset_geometry(ds_subset, path_to_permh=permh_file, variable='permeab')

    assert isinstance(ds_reset, xr.Dataset), 'Should return an xarray Dataset'
    assert 'permeab' in ds_reset.data_vars, 'Should have permeab variable'
    assert 'zone' in ds_reset.dims, 'Should have zone dimension'
    assert len(ds_subset.zone.data) == 927
    assert len(ds_reset.zone.data) == len(ds.zone.data)
    assert np.allclose(ds.zone.data, ds_reset.zone.data)
    assert np.allclose(ds.x.data, ds_reset.x.data)
    assert np.allclose(ds.y.data, ds_reset.y.data)
    assert np.allclose(ds_subset.permeab.data, ds_reset.sel(zone=ds_subset.zone.data).permeab.data)


def test_reset_geometry_fillna():
    """Test reset_geometry with fillna option"""
    permh_file = f'{DATA_PATH}/hallue.permh'

    # Load with dropna
    ds = gm.load_marthe_grid(permh_file, varname='PERMEAB')
    ds_subset = gm.load_marthe_grid(permh_file, varname='PERMEAB', drop_nan=True)

    # Reset geometry with fillna
    ds_reset = reset_geometry(ds_subset, path_to_permh=permh_file, variable='permeab', fillna=True)

    assert isinstance(ds_reset, xr.Dataset), 'Should return an xarray Dataset'
    # With fillna=True, NaN values should be filled with permh values
    assert not np.any(np.isnan(ds_reset['permeab'].data)), 'NaN values should be filled'
    assert np.allclose(ds_reset['permeab'].data, ds['permeab'].data)


if __name__ == '__main__':
    test_get_dims_from_attrs_simple()
    test_get_dims_from_attrs_nested()
    test_get_dims_from_attrs_multilayer()
    test_get_dims_from_attrs_format()
    test_reset_geometry_basic()
    test_reset_geometry_fillna()
    print("All reset_geometry and get_dims_from_attrs tests passed!")
