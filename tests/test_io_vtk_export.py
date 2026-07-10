#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import numpy as np
import vtkwriters as vtkw

import gridmarthe as gm
from gridmarthe.grid.io.vtk_writer import (
    _get_vertices_connectivity,
    convert_grid_to_vtk
)


def test_vtk_export():
    model_name = 'hallue_multilayer'
    hsubs = gm.load_marthe_grid('./tests/data/{}.hsubs'.format(model_name), xyfactor=1e3)
    topo  = gm.load_marthe_grid('./tests/data/{}.topog'.format(model_name), xyfactor=1e3)
    permh = gm.load_marthe_grid('./tests/data/{}.permh'.format(model_name), xyfactor=1e3, varname='PERMEAB', drop_nan=True)
    # geom = gm.compute_geometry(topo, hsubs, mask)  # ok
    geom = gm.compute_geometry(topo, hsubs).sel(zone=permh.zone.values)

    vertices, cellnodes, celltype = _get_vertices_connectivity(geom)
    assert np.shape(vertices) == (8*len(geom.x), 3), 'Wrong number of vertices'
    assert np.shape(cellnodes) == (len(geom.x), 8), 'Wrong number of cellnodes'
    assert celltype == 'voxel', 'Wrong celltype'

    convert_grid_to_vtk(geom, 'z', output_tpl='tests/tmp_outputs/vtk_hallue')
    print('vtk writer test passed!')
    return


if __name__ == '__main__':

    test_vtk_export()
