#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import gridmarthe as gm


def test_search_zone_ij():
    ftest = 'tests/data/hallue.permh'
    ds = gm.load_marthe_grid(ftest, add_col_row=True)
    i, j = 23, 32
    idx = gm.search_zone(ds, i=i, j=j)
    assert len(idx.zone) == 1
    assert idx.col == 23
    assert idx.row == 32
    assert idx.x == 607.75
    assert idx.y == 2.55325e+03
    assert idx.permeab == 3.46e-3


def test_search_zone_xy():
    ftest = 'tests/data/hallue.permh'
    ds = gm.load_marthe_grid(ftest, add_col_row=True)
    xm, ym = 607.75, 2.55325e3
    idx = gm.search_zone(ds, x=xm, y=ym)
    assert len(idx.zone) == 1
    assert idx.col == 23
    assert idx.row == 32
    assert idx.x == 607.75
    assert idx.y == 2.55325e+03
    assert idx.permeab == 3.46e-3


def test_search_zone_xy_nearest():
    ftest = 'tests/data/hallue.permh'
    ds = gm.load_marthe_grid(ftest, add_col_row=True)
    xm, ym = 607.85, 2.553e3
    idx = gm.search_zone(ds, x=xm, y=ym)
    assert len(idx.zone) == 1
    assert idx.col == 23
    assert idx.row == 32
    assert idx.x == 607.75
    assert idx.y == 2.55325e+03
    assert idx.permeab == 3.46e-3


def test_search_zone_xyz():
    ftest = 'tests/data/albien.hsubs'
    xm, ym = 533, 2527
    ds = gm.load_marthe_grid(ftest)
    idx = gm.search_zone(ds, x=xm, y=ym, z=6)
    assert len(idx.zone) == 1
    assert idx.z == 6
    assert idx.zone == 170567


def test_search_zone_xy_multiple_layer():
    ftest = 'tests/data/albien.hsubs'
    xm, ym = 533, 2527
    ds = gm.load_marthe_grid(ftest)
    idx = gm.search_zone(ds, x=xm, y=ym)
    assert len(idx.zone) == 6


if __name__ == '__main__':
    test_search_zone_ij()
    test_search_zone_xy()
    test_search_zone_xy_nearest()
    test_search_zone_xyz()
    test_search_zone_xy_multiple_layer()
    print('All tests passed!')
