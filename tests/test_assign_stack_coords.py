#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import gridmarthe as gm
from gridmarthe.utils import _is_sorted


DATA_WITH_Z_NESTED = './tests/data/craie_npc_gig.permh'
DATA_WITH_Z = './tests/data/craie_npc_nogig.permh'
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


def test_assign_coords_with_z_nested():
    ds = gm.load_marthe_grid(DATA_WITH_Z_NESTED, VAR)
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

    # manual verif
    # np.allclose(ds2.permeab.data[:, ::-1, :].flatten(), ds.permeab.data)  # ok !
    # edit, add sortby(y, desc) in assign_coords, no more need to revert y order

    assert 'x' not in ds3.coords
    assert 'zone' in ds3.coords
    assert len(np.shape(ds3[VAR.lower()].data)) == 2
    assert len(ds3.zone.data) == ds2.x.size * ds2.y.size

    assert len(ds.zone.data) == len(ds3.zone.data)
    assert np.allclose(ds3.x.data, ds.x.data)
    assert np.allclose(ds3.y.data, ds.y.data)
    assert np.allclose(ds3.dx.data, ds.dx.data)
    assert np.allclose(ds3.dy.data, ds.dy.data)
    assert np.allclose(ds3[VAR.lower()].data, ds[VAR.lower()].data)

    assert _is_sorted(ds3.x.data[:len(ds2.x.data)])
    assert _is_sorted(ds3.y.data[::len(ds2.x.data)][::-1])

    status = gm.write_marthe_grid(ds3, './tests/res/temp_stack_coords_no_z.permh', VAR.lower(), debug=True)
    assert status == 0


def test_stack_coords_with_z():
    ds = gm.load_marthe_grid(DATA_WITH_Z, VAR)
    ds2 = gm.assign_coords(ds)
    ds3 = gm.stack_coords(ds2)

    # manual verif
    # np.allclose(ds2.permeab.data[:, :, ::-1, :].flatten(), ds.permeab.data)  # ok!

    assert 'x' not in ds3.coords
    assert 'zone' in ds3.coords
    assert len(np.shape(ds3[VAR.lower()].data)) == 2
    assert len(ds3.zone.data) == ds2.x.size * ds2.y.size * ds2.z.size

    assert len(ds.zone.data) == len(ds3.zone.data)
    assert np.allclose(ds3.x.data, ds.x.data)
    assert np.allclose(ds3.y.data, ds.y.data)
    assert np.allclose(ds3.z.data, ds.z.data)
    assert np.allclose(ds3.dx.data, ds.dx.data)
    assert np.allclose(ds3.dy.data, ds.dy.data)
    assert np.allclose(ds3[VAR.lower()].data, ds[VAR.lower()].data)

    # assert sort order
    assert _is_sorted(np.unique(ds3.x.data))
    assert _is_sorted(np.unique(ds3.y.data))
    assert _is_sorted(np.unique(ds3.z.data))
    status = gm.write_marthe_grid(ds3, './tests/res/temp_stack_coords_with_z.permh', VAR.lower())
    assert status == 0


def test_stack_coords_with_z_nested():
    ds = gm.load_marthe_grid(DATA_WITH_Z_NESTED, VAR)
    ds2 = gm.assign_coords(ds)
    ds3 = gm.stack_coords(ds2)

    assert 'x' not in ds3.coords
    assert 'zone' in ds3.coords
    assert len(np.shape(ds3[VAR.lower()].data)) == 2
    assert len(ds3.zone.data) == ds2.x.size * ds2.y.size * ds2.z.size

    # assert len(ds.zone.data) == len(ds3.zone.data)  # cannot check this for nested grids
    # FIXME: the last assert cannot be tested for nested grids, as
    # different cell sizes lead to incorrect total number of zones
    # when flattening back to 1D from cartesian coords/arrays
    # TODO: def a _reshape_for_writer function to handle nested grids properly
    # i.e from a stacked coords ds with no nans, loop over dx/dy unique values to reconstruct
    # the original grid shapes with nans where needed for every subgrid. compute dx/dy
    # from coords and shapes if not present in ds.vars


def run_all():
    test_assign_coords_with_z()
    test_assign_coords_no_z()
    test_assign_coords_force_no_z()
    test_stack_coords_no_z()
    test_stack_coords_with_z()
    print("====================================")
    print("gridmarthe assign_coords test passed")
    return


if __name__ == "__main__":
    run_all()
