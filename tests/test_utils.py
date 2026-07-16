#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import xarray as xr
import pytest

import gridmarthe as gm


def test_get_fist_var():
    ds = xr.open_dataset('tests/data/chasim_hallue.nc')
    var = gm.get_default_variable(ds)
    assert var == 'charge', 'Error while parsing first var'


def test_fillna():
    ds = gm.load_marthe_grid('tests/data/hallue.permh', drop_nan=True)
    ds = gm.stack_coords(gm.assign_coords(ds))  # create nans
    nan_idx = np.argwhere(np.isnan(np.squeeze(ds['permeab'].data))).ravel()
    nonan = np.ones(ds.permeab.data.shape[1], dtype=bool)
    nonan[nan_idx] = False
    ds = gm.fillna(ds, value=0)
    assert np.all(ds['permeab'].data[0, nan_idx] == 0), 'Error while filling nans'
    assert np.all(ds['permeab'].data[0, nonan] != 0.), 'Too much value filled'


def test_dropna():
    ds = gm.load_marthe_grid('tests/data/hallue.permh')
    ds = gm.dropna(ds, 0.)
    arr = ds['permeab'].data
    assert np.size(ds.zone.data) == 927, 'too much value dropped'
    assert not np.any(np.isnan(arr)), 'real np nan present'
    assert np.count_nonzero(arr) == 927, 'zero values still present after dropna'


def test_subset():
    ds = gm.load_marthe_grid('tests/data/hallue.permh')
    ds = gm.subset(ds, 0.)
    assert np.all(ds['permeab'].data == 0.)
    assert np.size(ds.zone.data) == (2862 - 927)


def test_replace():
    msk = gm.load_marthe_grid('tests/data/hallue.permh', drop_nan=True)
    ds = gm.load_marthe_grid('tests/data/hallue.permh')
    ds = gm.replace(ds, 0., 9999.)
    nan_idx = np.ones(ds['permeab'].shape[1], dtype=bool)
    nan_idx[msk.zone.data - 1] = False
    assert not np.any(ds['permeab'].data == 0.)
    assert np.all(ds['permeab'].data[0, nan_idx] == 9999.)
    assert np.allclose(msk['permeab'].data, ds.sel(zone=msk['zone'].data)['permeab'].data)


def test_deprecated_arg():
    with pytest.warns(DeprecationWarning):
        ds = gm.load_marthe_grid('tests/data/chasim_hallue_2var.out', nanval=9999.)


if __name__ == '__main__':
    test_get_fist_var()
    test_deprecated_arg()
