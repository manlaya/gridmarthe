#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import gridmarthe as gm


DATA_WITH_Z = './tests/data/craie_npc_gig.permh'
DATA_NO_Z = './tests/data/hallue.permh'
VAR = "PERMEAB"


def test_assign_coords_with_z():
    ds = gm.load_marthe_grid(DATA_WITH_Z, VAR)
    ds2 = gm.assign_coords(ds)
    assert 'x' in ds2.coords
    assert 'y' in ds2.coords
    assert 'z' in ds2.coords
    assert VAR.lower() in ds.data_vars
    assert len(np.shape(ds2[VAR.lower()].data)) == 4


def test_assign_coords_no_z():
    ds = gm.load_marthe_grid(DATA_NO_Z, VAR)
    ds2 = gm.assign_coords(ds)
    assert 'x' in ds2.coords
    assert 'y' in ds2.coords
    assert 'z' not in ds2.coords
    assert VAR.lower() in ds.data_vars
    assert len(np.shape(ds2[VAR.lower()].data)) == 3


def test_assign_coords_force_no_z():
    ds = gm.load_marthe_grid(DATA_WITH_Z, VAR)
    ds2 = gm.assign_coords(ds, add_lay=False)
    assert 'x' in ds2.coords
    assert 'y' in ds2.coords
    assert 'z' not in ds2.coords
    assert VAR.lower() in ds.data_vars
    assert len(np.shape(ds2[VAR.lower()].data)) == 3


def test_stack_coords_no_z():
    ds = gm.load_marthe_grid(DATA_NO_Z, VAR)
    ds2 = gm.assign_coords(ds)
    ds3 = gm.stack_coords(ds2)
    assert 'x' not in ds3.coords
    assert 'zone' in ds3.coords


def run_all():
    test_assign_coords_with_z()
    test_assign_coords_no_z()
    test_assign_coords_force_no_z()
    test_stack_coords_no_z()
    print("====================================")
    print("gridmarthe assign_coords test passed")
    return


if __name__ == "__main__":
    run_all()
