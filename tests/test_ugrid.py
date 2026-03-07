#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gridmarthe as gm
from gridmarthe.grid.grid_utils import get_default_variable


def test_ugrid_no_z():
    ds = gm.load_marthe_grid('./tests/data/hallue.permh', drop_nan=True)
    varname = get_default_variable(ds)
    uds = create_ugrid(ds, varname)
    pass


def test_ugrid_no_z_nested():
    ds = gm.load_marthe_grid('./tests/data/hallue.permh', drop_nan=True)
    varname = get_default_variable(ds)
    ds = ds.where(ds.z == 6, drop=True).drop_vars('z')
    uds = create_ugrid(ds, varname)
    pass


def test_ugrid_with_z_nested():
    ds = gm.load_marthe_grid('./tests/data/craie_npc_gig.permh', drop_nan=True)
    varname = get_default_variable(ds)
    uds = create_ugrid(ds, varname)
    pass


def test_ugrid_with_time():
    pass


if __name__ == "__main__":

    import os
    os.makedirs('tests/nc_ugrid', exist_ok=True)

    ds = gm.load_marthe_grid('./tests/data/craie_npc_gig.permh', drop_nan=True)
    # ds = gm.load_marthe_grid('./tests/data/hallue.permh', drop_nan=True)
    varname = get_default_variable(ds)
    ds = ds.where(ds.z == 6, drop=True).drop_vars('z')
    uds = create_ugrid(ds, varname)

    # issue with h5netcdf engine
    # see https://github.com/lutraconsulting/MDAL/issues/520
    uds.isel(time=0).to_netcdf('tests/nc_ugrid/tests-netcdf4.nc', engine='netcdf4')
    uds.isel(time=0).to_netcdf('tests/nc_ugrid/tests-h5netcdf.nc', engine='h5netcdf')
    print(uds)

    uds.isel(time=0).to_netcdf('tests/nc_ugrid/tests-with-z.nc', engine='netcdf4')
    # bathy = xr.open_dataset('tests/nc_ugrid/mesh_bathy.nc')
    # bathy['element'].values
