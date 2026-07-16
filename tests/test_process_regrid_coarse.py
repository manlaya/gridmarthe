#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from inspect import stack
import numpy as np
import gridmarthe as gm


DATA = './tests/data/craie_npc_nogig.permh'


def test_regrid():
    grid = gm.load_marthe_grid(DATA, drop_nan=True)
    ds_coarse_2d = gm.rescale_grid(grid, res=1e3)
    ds_coarse = gm.rescale_grid(grid, res=1e3, stack=True)
    ds_8km = gm.rescale_grid(grid, res=8e3, stack=True)
    # ds_100m = gm.rescale_grid(grid, res=1e2, stack=True)

    # check resolution
    assert 'zone' in ds_coarse.dims
    assert 'x' in ds_coarse_2d.dims
    assert np.all(ds_coarse.dx.data == 1e3)
    assert np.all(ds_8km.dx.data == 8e3)

    # TODO check data?
    pass


if __name__ == '__main__':
    test_regrid()
