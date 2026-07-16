#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import gridmarthe as gm


DATA = './tests/data/craie_npc_nogig.permh'


def test_regrid():
    grid = gm.load_marthe_grid(DATA, drop_nan=True)
    ds_coarse = gm.rescale_grid(grid, res=1e3)  # kwars can be passed to interp method
    ds_8km = gm.rescale_grid(grid, res=8e3)
    ds_100m = gm.rescale_grid(grid, res=1e2)

    # check resolution
    assert np.all(ds_coarse.dx.data == 1e3)
    assert np.all(ds_8km.dx.data == 8e3)
    assert np.all(ds_100m.dx.data == 1e2)

    # TODO check data
    pass
