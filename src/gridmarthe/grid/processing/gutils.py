#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
from shapely.geometry import Polygon


def _mk_cell_polygon(xleft, ylower, xright, yupper):
    return Polygon(
        (
            (xleft , ylower),
            (xright, ylower),
            (xright, yupper),
            (xleft , yupper),
            (xleft , ylower)
        )
    )


_polygonize = np.vectorize(_mk_cell_polygon)


def _build_polyg(ds):
    """ build a (rectangular) polygon shape from marthegrid dataset """

    x0 = ds.x.values - (ds.dx.values / 2.)
    y0 = ds.y.values - (ds.dy.values / 2.)
    x1 = ds.x.values + (ds.dx.values / 2.)
    y1 = ds.y.values + (ds.dy.values / 2.)

    return _polygonize(x0, y0, x1, y1)
