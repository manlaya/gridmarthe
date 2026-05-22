#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tempfile

import numpy as np
import xarray as xr

import gridmarthe as gm


FILE_IN = './tests/data/hallue_multilayer.permh'
FILE_OUT = './tests/tmp_outputs/test_write_nc_missing_val.nc'


def test_fix_write_nc_missing_val():
    # known bug : cp from src gridmarthe 2024:
     # FIXME better, prevent bug at write :
    # https://github.com/pydata/xarray/issues/7722
    # https://stackoverflow.com/questions/65019301/variable-has-conflicting-fillvalue-and-missing-value-cannot-encode-data-when
    # del ds[varname.lower()].encoding['missing_value']

    # issue gridmarthe#16
    # temp =  # create a temp file
    temp = tempfile.NamedTemporaryFile(suffix='.nc', dir='./tests/tmp_outputs')
    ds = gm.load_marthe_grid(FILE_IN)
    ds.to_netcdf(FILE_OUT)
    ds = xr.open_dataset(FILE_OUT)
    ds.to_netcdf(temp.name)  # previously ko
    ds2 = xr.open_dataset(FILE_OUT)
    assert ds2['permeab'].encoding.get('missing_value') is None
    assert ds2['permeab'].attrs.get('mart_missing_value') == 0.
    assert np.isnan(ds2['permeab'].encoding.get('_FillValue'))
