#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import geopandas as gpd
import gridmarthe as gm


MODEL_NAME = 'hallue'
DATA = './tests/data/{}.permh'.format(MODEL_NAME)


def test_get_active_mask_array():
    permh = gm.load_marthe_grid(DATA, varname='PERMEAB')
    mask = gm.get_active_mask(permh, as_array=True, only_mask=True)
    assert np.all(mask['ibound'].data == 1), 'only_mask failed'
    assert np.size(mask.zone.data) == 927


def test_get_active_mask_array_ibound():
    permh = gm.load_marthe_grid(DATA, varname='PERMEAB')
    mask = gm.get_active_mask(permh, as_array=True)
    ma = mask['ibound'].data
    assert not np.all(ma == 1), 'ibound mask failed'
    assert np.size(ma) == 2862
    assert np.size(ma[ma==1]) == 927


def test_get_active_mask_shape():
    permh = gm.load_marthe_grid(DATA, varname='PERMEAB')
    mask = gm.get_active_mask(permh)
    assert isinstance(mask, gpd.GeoDataFrame)
