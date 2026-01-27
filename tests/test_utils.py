#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import xarray as xr
import gridmarthe as gm
import pytest


def test_get_fist_var():
    ds = xr.open_dataset('tests/data/chasim_hallue.nc')
    var = gm.get_default_variable(ds)
    assert var == 'charge', 'Error while parsing first var'


def test_deprecated_arg():
    with pytest.warns(DeprecationWarning):
        ds = gm.load_marthe_grid('tests/data/chasim_hallue_2var.out', nanval=9999.)


if __name__ == '__main__':
    test_get_fist_var()
    test_deprecated_arg()
