#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gridmarthe as gm


def test_cross_section():
    permh = gm.load_marthe_grid('tests/data/craie_npc_nogig.permh', drop_nan=True)
    topo  = gm.load_marthe_grid('tests/data/craie_npc.topog', varname='H_TOPOGR')
    hsub  = gm.load_marthe_grid('tests/data/craie_npc.hsubs', varname='H_SUBSTRAT')
    gwl   = gm.load_marthe_grid('tests/data/chasim_npc.out', varname='CHARGE', drop_nan=True)  # groundwater level

    geom = gm.compute_geometry(topo, hsub, permh.zone)
    geom['charge'] = (('time', 'zone'), gwl['charge'].data)  # add gwl to new dataset with geom

    ds = gm.assign_coords(geom)

    XC = 6.116e5
    ds_xs = gm.slice_cross_section(ds, x=XC)  # here we define a cross section along y axis (x is constant)
    print(ds_xs)

    assert 'y' in ds_xs.dims, "Cross-section should have 'y' dimension"
    assert 'x' not in ds_xs.dims, "Cross-section should not have 'x' dimension"
    assert ds_xs.sizes['y'] > 1  # cross-section has multiple points
    assert ds_xs.sizes['z'] == 10  # we have 10 layers


if __name__ == "__main__":

    test_cross_section()
