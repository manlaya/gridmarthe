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
