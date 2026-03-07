#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import xarray as xr

import pytest

import gridmarthe as gm


DATA_PATH = './tests/data/chasim_hallue_2var.out'
DATA_WITH_TIME = './tests/data/chasim_hallue.out'
FPASTP = './tests/data/hallue.pastp'
VAR = "CHARGE"


def test_load_valid_grid_returns_xarray():
    ds = gm.load_marthe_grid(DATA_PATH, VAR)
    assert isinstance(ds, xr.Dataset)
    assert VAR.lower() in ds.data_vars
    assert len(ds.zone) == 2862


def test_load_with_varname_none_picks_first():
    ds = gm.load_marthe_grid(DATA_PATH, varname=None)
    assert isinstance(ds, xr.Dataset)
    # assert len(ds.data_vars) > 0
    assert VAR.lower() in ds.data_vars  # here we know the first var is CHARGE


def test_load_with_varname_all_returns_multiple():
    ds = gm.load_marthe_grid(DATA_PATH, varname='all')
    assert isinstance(ds, xr.Dataset)
    data_vars = [ x for x in list(ds.data_vars) if x not in ['x', 'y', 'z', 'dx', 'dy']]
    assert len(data_vars) >= 1


def test_load_with_drop_nan_removes_nan():
    ds = gm.load_marthe_grid(DATA_PATH, VAR, drop_nan=True)
    arr = ds[VAR.lower()].values
    assert not np.any(np.isnan(arr))
    assert not np.any(arr == 9999.)  # here 9999. is the default nanval


def test_load_with_custom_nanval():
    DATA_PATH = './tests/data/craie_npc_gig.permh'
    ds = gm.load_marthe_grid(DATA_PATH, VAR, drop_nan=True, nan_value=0.)
    arr = ds[VAR.lower()].values
    assert not np.any(arr == 0.)


def test_load_with_adds_col_row():
    ds = gm.load_marthe_grid(DATA_PATH, VAR, add_col_row=True)
    assert 'col' in ds.data_vars
    assert 'row' in ds.data_vars


def test_load_with_add_id_grid_adds_id_grid():
    ds = gm.load_marthe_grid(DATA_PATH, VAR, add_id_grid=True)
    assert 'id_grid' in ds.data_vars


def test_load_nonexistent_file_raises():
    with pytest.raises(FileNotFoundError):
        gm.load_marthe_grid('not_a_file.permh', VAR)


def test_load_invalid_varname_raises():
    with pytest.raises(ValueError):
        gm.load_marthe_grid(DATA_PATH, varname='INVALIDVAR')


def test_load_grid_attrs_present():
    ds = gm.load_marthe_grid(DATA_PATH, VAR)
    assert 'title' in ds.attrs
    assert 'marthe_grid_version' in ds.attrs
    assert 'original_dimensions' in ds.attrs


def test_drop_time_dimension_for_parameter_grid():
    ds = gm.load_marthe_grid(DATA_PATH, VAR, drop_time=True)
    assert 'time' not in ds.dims


def test_load_grid_with_time_dimension():
    ds = gm.load_marthe_grid(DATA_WITH_TIME, VAR, FPASTP, drop_nan=True)
    assert 'time' in ds.dims
    assert ds.sizes['time'] == 205
    assert isinstance(ds.time.values[0], np.datetime64)
    assert ds.zone.size == 927


def test_load_grid_wrong_metadata():
    ds = gm.load_marthe_grid('./tests/data/test_multilay_nest_no_metadata.permh')
    varn = 'permh'
    assert 'time' in ds.dims
    assert ds.sizes['time'] == 1
    assert varn in ds.keys()
    assert ds[varn].size == 2533420
    assert np.max(ds['z'].values) == 10


def run_all():
    test_load_valid_grid_returns_xarray()
    test_load_grid_attrs_present()
    test_load_with_add_id_grid_adds_id_grid()
    test_load_with_adds_col_row()
    test_load_with_custom_nanval()
    test_load_with_drop_nan_removes_nan()
    test_load_with_varname_none_picks_first()
    test_load_with_varname_all_returns_multiple()
    test_load_nonexistent_file_raises()
    test_load_invalid_varname_raises()
    print("=============================")
    print("gridmarthe reader test passed")
    return


if __name__ == "__main__":
    run_all()
