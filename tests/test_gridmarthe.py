#!/usr/bin/env python
# -*- coding: utf-8 -*-


import numpy as np
import xarray as xr
import pytest

import gridmarthe as gm


DATA_PATH = './tests/data/chasim_hallue_2var.out'
VAR = "CHARGE"


def test_load_valid_grid_returns_xarray():
    ds = gm.load_marthe_grid(DATA_PATH, VAR)
    assert isinstance(ds, xr.Dataset)
    assert VAR.lower() in ds.data_vars


def test_load_with_varname_none_picks_first():
    ds = gm.load_marthe_grid(DATA_PATH, varname=None)
    assert isinstance(ds, xr.Dataset)
    # assert len(ds.data_vars) > 0
    assert VAR.lower() in ds.data_vars  # here we know the first var is CHARGE


def test_load_with_varname_all_returns_multiple():
    ds = gm.load_marthe_grid(DATA_PATH, varname='all')
    assert isinstance(ds, xr.Dataset)
    data_vars = [ x for x in list(ds.data_vars) if not x in ['x', 'y', 'z', 'dx', 'dy']]
    assert len(data_vars) >= 1


def test_load_with_drop_nan_removes_nan():
    ds = gm.load_marthe_grid(DATA_PATH, VAR, drop_nan=True)
    arr = ds[VAR.lower()].values
    assert not np.any(np.isnan(arr))
    assert not np.any(arr == 9999.)  # here 9999. is the default nanval


def test_load_with_custom_nanval():
    ds = gm.load_marthe_grid(DATA_PATH, VAR, drop_nan=True, nanval=0.)
    arr = ds[VAR.lower()].values
    assert not np.any(arr == 0.)


def test_load_with_keepligcol_adds_col_lig():
    ds = gm.load_marthe_grid(DATA_PATH, VAR, keepligcol=True)
    assert 'col' in ds.data_vars
    assert 'lig' in ds.data_vars


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


# MY TESTS
# inputs = './tests/data/craie_npc.permh', "PERMEAB" # ajouter tests/data ici pour conda-forge ?
# 
# toto = gm.load_marthe_grid(*inputs, drop_nan=True)
# # toto = gm.load_marthe_grid(*inputs, drop_nan=True, nanval=0.)
# # toto = gm.load_marthe_grid(inputs[0], varname=None)
# # toto = gm.load_marthe_grid(inputs[0], varname='all')
# # toto = gm.load_marthe_grid(*inputs, keepligcol=True)
# # toto = gm.load_marthe_grid(*inputs, add_id_grid=True)
# 
# test = toto.set_coords(['time', 'zone', 'x', 'y', 'z', 'dx', 'dy'])
# print(toto.attrs)
# test.mart.assign_coords()
# 
# # for pymarthe compat'
# # to recarray
# df = toto.to_dataframe()
# df.to_records()
# 
# toto2 = toto.mart.assign_coords()
# toto3 = toto.mart.to_recarray()
# 