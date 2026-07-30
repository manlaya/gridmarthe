#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import gridmarthe as gm


DATA_CHARGE = './tests/data/chasim_hallue.nc'
DATA_PASTP = './tests/data/hallue.pastp'
DATA_PERMEA = './tests/data/hallue.permh'


def test_to_raster_without_time():
    ds = gm.load_marthe_grid(DATA_PERMEA, drop_nan=True)
    ds = gm.assign_coords(ds, add_lay=False)

    gm.to_raster(
        ds, varname='permeab', filename_tpl='tests/tmp_outputs/permeab'
    )
    assert (
        os.path.isfile('tests/tmp_outputs/permeab.tiff'),
        'no raster found'
    )


def test_to_raster_with_time():
    ds = gm.load_marthe_grid(DATA_CHARGE, fpastp=DATA_PASTP, drop_nan=True)
    ds = gm.assign_coords(ds.isel(time=[0, 1, 2]), add_lay=False)

    # test without specifying time values explicitly
    gm.to_raster(
        ds, varname='charge', time='1995-07-31',
        filename_tpl='tests/tmp_outputs/charge'
    )
    assert (
        os.path.isfile('tests/tmp_outputs/charge_0.tiff'),
        'no raster 0 found'
    )
    assert (
        os.path.isfile('tests/tmp_outputs/charge_2.tiff'),
        'no raster 2 found'
    )

    # test specifying time values explicitly as string
    gm.to_raster(
        ds, varname='charge', time='1995-07-31',
        filename_tpl='tests/tmp_outputs/charge'
    )
    assert (
        os.path.isfile('tests/tmp_outputs/charge_1995-07-31.tiff'),
        'no raster 1995-07-31 found'
    )

    # test specifying time values explicitly as list of strings
    gm.to_raster(
        ds, varname='charge', time=['1995-08-01', '1995-09-01'],
        filename_tpl='tests/tmp_outputs/charge'
    )
    assert (
        os.path.isfile('tests/tmp_outputs/charge_1995-08-01.tiff'),
        'no raster 1995-08-01 found'
    )
    assert (
        os.path.isfile('tests/tmp_outputs/charge_1995-09-01.tiff'),
        'no raster 1995-09-01 found'
    )
