#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import gridmarthe as gm
from gridmarthe.grid.grid_utils import get_default_variable


def _check_coords_attrs(ds, uds):
    assert 'node_x' in uds.coords, 'node coordinates not found'
    assert 'node_y' in uds.coords, 'node coordinates not found'
    assert 'face_x' in uds.coords, 'face coordinates not found'
    assert 'face_y' in uds.coords, 'face coordinates not found'
    assert 'mesh_topology' in uds.keys(), 'mesh topology not found'
    assert 'face_node_connectivity' in uds.variables, 'face connectivity not found'
    assert 'nodes_per_face' in uds.variables, 'node per face not found'
    assert len(uds.n_faces) == len(ds.zone), 'number of faces does not match'
    assert len(uds.n_max_face_nodes) == 4, "max number of face is wrong"


def test_ugrid_no_z():
    ds = gm.load_marthe_grid('./tests/data/hallue.permh', drop_nan=True)
    varname = get_default_variable(ds)
    uds = gm.create_ugrid(ds, varname)
    _check_coords_attrs(ds, uds)
    assert len(uds.n_nodes) == 1035


def test_ugrid_no_z_nested(write_to_disk=False):
    ds = gm.load_marthe_grid('./tests/data/Somme_V3_Surfex.permh', xyfactor=1e3, drop_nan=True)
    varname = get_default_variable(ds)
    uds = gm.create_ugrid(ds, varname)
    _check_coords_attrs(ds, uds)
    assert len(uds.n_nodes) == 69041
    if write_to_disk:
        uds.to_netcdf('tests/nc_ugrid/test-2d-unstruct.nc', engine='netcdf4')


def test_ugrid_with_z_nested():
    ds = gm.load_marthe_grid('./tests/data/craie_npc_gig.permh', drop_nan=True)
    varname = get_default_variable(ds)
    ds = ds.where(ds.z == 6, drop=True).drop_vars('z')
    uds = gm.create_ugrid(ds, varname)
    _check_coords_attrs(ds, uds)


def test_ugrid_with_time(write_to_disk=False):
    ds = gm.load_marthe_grid('./tests/data/chasim_hallue.out', xyfactor=1e3, drop_nan=True, fpastp='./tests/data/hallue.pastp')
    varname = get_default_variable(ds)
    uds = gm.create_ugrid(ds, varname)
    _check_coords_attrs(ds, uds)
    assert len(uds.time) == 205
    assert np.issubdtype(uds.time.data.dtype, np.datetime64)
    if write_to_disk:
        uds.to_netcdf('tests/nc_ugrid/test-2d-struct-with-time.nc', engine='netcdf4')


if __name__ == "__main__":

    import os
    os.makedirs('tests/nc_ugrid', exist_ok=True)

    test_ugrid_with_time(write_to_disk=True)
    test_ugrid_no_z_nested(write_to_disk=True)

    # Additional manual tests, for debug
    # ----------------------------------
    ds = gm.load_marthe_grid('./tests/data/craie_npc_gig.permh', drop_nan=True)
    # ds = gm.load_marthe_grid('./tests/data/hallue.permh', drop_nan=True)
    varname = get_default_variable(ds)
    ds_z6 = ds.where(ds.z == 6, drop=True).drop_vars('z')
    uds = gm.create_ugrid(ds_z6, varname)

    # issue with h5netcdf engine
    # see https://github.com/lutraconsulting/MDAL/issues/520
    uds.isel(time=0).to_netcdf('tests/nc_ugrid/tests-netcdf4.nc', engine='netcdf4')
    uds.isel(time=0).to_netcdf('tests/nc_ugrid/tests-h5netcdf.nc', engine='h5netcdf')
    print(uds)

    uds_3d = gm.create_ugrid(ds, varname)
    uds_3d.isel(time=0).to_netcdf('tests/nc_ugrid/tests-with-z.nc', engine='netcdf4')

    uds.to_netcdf('tests/nc_ugrid/test-2d-with-time.nc', engine='netcdf4')
    uds_3d.to_netcdf('tests/nc_ugrid/test-3d-with-time.nc', engine='netcdf4')

    # check other dataset:
    # bathy = xr.open_dataset('tests/nc_ugrid/mesh_bathy.nc')
    # bathy['element'].values
