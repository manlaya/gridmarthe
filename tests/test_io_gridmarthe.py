#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
import numpy as np
import xarray as xr

import pytest

import gridmarthe as gm


DATA_PATH = './tests/data/chasim_hallue_2var.out'
DATA_WITH_TIME = './tests/data/chasim_hallue.out'
FPASTP = './tests/data/hallue.pastp'
VAR = "CHARGE"

try:
    import pytest_benchmark  # noqa: F401
    BENCHMARK_AVAILABLE = True
except ImportError:
    BENCHMARK_AVAILABLE = False


def test_load_valid_grid_returns_xarray():
    ds = gm.load_marthe_grid(DATA_PATH, VAR)
    assert isinstance(ds, xr.Dataset)
    assert VAR.lower() in ds.data_vars
    assert len(ds.zone) == 2862


def test_load_with_varname_none_picks_first():
    ds = gm.load_marthe_grid(DATA_PATH, varname=None)
    assert isinstance(ds, xr.Dataset)
    # assert len(ds.data_vars) > 0
    assert VAR.lower() in ds.data_vars  # here we know the first var is CHARGE


def test_load_with_varname_all_returns_multiple():
    ds = gm.load_marthe_grid(DATA_PATH, varname='all')
    assert isinstance(ds, xr.Dataset)
    data_vars = [ x for x in list(ds.data_vars) if x not in ['x', 'y', 'z', 'dx', 'dy']]
    assert len(data_vars) >= 1


def test_load_with_drop_nan_removes_nan():
    # default version, with 9999.
    ds = gm.load_marthe_grid(DATA_PATH, VAR, drop_nan=True)
    arr = ds[VAR.lower()].values
    assert not np.any(np.isnan(arr))
    assert not np.any(arr == 9999.)  # here 9999. is the default nanval

    # other variables, with 0. with automatic detection
    ds = gm.load_marthe_grid('tests/data/hallue.permh', drop_nan=True)
    arr = ds['permeab'].values
    assert not np.any(np.isnan(arr))
    assert not np.any(arr == 0.)  # here 9999. is the default nanval
    assert len(ds.zone.data) == 927

    # same but nested
    ds = gm.load_marthe_grid('tests/data/Somme_V3_Surfex.permh', drop_nan=True, xyfactor=1e3)
    arr = ds['permeab'].values
    assert not np.any(np.isnan(arr))
    assert not np.any(arr == 0.)  # here 9999. is the default nanval
    assert len(ds.zone.data) == 66924

    # same but multilayer
    ds = gm.load_marthe_grid('tests/data/craie_npc_nogig.permh', drop_nan=True)
    arr = ds['permeab'].values
    assert not np.any(np.isnan(arr))
    assert not np.any(arr == 0.)
    assert len(ds.zone.data) == 216742

    # same but multilayer AND nested grid
    ds = gm.load_marthe_grid('tests/data/craie_npc_gig.permh', drop_nan=True)
    arr = ds['permeab'].values
    assert not np.any(np.isnan(arr))
    assert not np.any(arr == 0.)
    assert len(ds.zone.data) == 101209


def test_load_with_custom_nanval():
    ds = gm.load_marthe_grid('tests/data/chasim_hallue_fake_8888.out', VAR, drop_nan=True, nan_value=8888.)
    arr = ds[VAR.lower()].values
    assert not np.any(arr == 0.)
    assert np.any(arr == 9999.)  # here 9999. should still be present


def test_load_with_adds_col_row():
    ds = gm.load_marthe_grid(DATA_PATH, VAR, add_col_row=True)
    assert 'col' in ds.data_vars
    assert 'row' in ds.data_vars


def test_load_with_add_id_grid_adds_id_grid():
    ds = gm.load_marthe_grid(DATA_PATH, VAR, add_id_grid=True)
    assert 'id_grid' in ds.data_vars


def test_load_with_add_id_grid_drop_nest_bound():
    ds = gm.load_marthe_grid('./tests/data/craie_npc_gig.permh', 'PERMEAB', add_id_grid=True)
    assert 'id_grid' in ds.data_vars

    zones = ds.where(ds['id_grid']==1)['zone'].values

    mask = gm.mask_nest_bound(ds)
    safe_zone = ~ds["zone"].isin(mask)
    ds = ds.sel(zone=safe_zone)
    
    assert len(zones) != len(ds['zone'].values)


def test_load_nonexistent_file_raises():
    with pytest.raises(FileNotFoundError):
        gm.load_marthe_grid('not_a_file.permh', VAR)


def test_load_invalid_varname_raises():
    with pytest.raises(ValueError):
        gm.load_marthe_grid(DATA_PATH, varname='INVALIDVAR')


def test_load_grid_attrs_present():
    ds = gm.load_marthe_grid(DATA_PATH, VAR)
    assert 'title' in ds.attrs
    assert 'marthe_grid_version' in ds.attrs
    assert 'original_dimensions' in ds.attrs


def test_drop_time_dimension_for_parameter_grid():
    ds = gm.load_marthe_grid(DATA_PATH, VAR, drop_time=True)
    assert 'time' not in ds.dims
    assert VAR.lower() in ds.data_vars


def test_load_grid_with_time_dimension():
    ds = gm.load_marthe_grid(DATA_WITH_TIME, VAR, FPASTP, drop_nan=True)
    assert 'time' in ds.dims
    assert ds.sizes['time'] == 205
    assert isinstance(ds.time.values[0], np.datetime64)
    assert ds.zone.size == 927


@pytest.mark.filterwarnings("ignore:No variable name found.")
def test_load_grid_wrong_metadata():
    ds = gm.load_marthe_grid('./tests/data/test_multilay_nest_no_metadata.permh')
    varn = 'permh'
    assert 'time' in ds.dims
    assert ds.sizes['time'] == 1
    assert varn in ds.keys()
    assert ds[varn].size == 2533420
    assert np.max(ds['z'].values) == 10


def test_shallow_only():
    ds = gm.load_marthe_grid(DATA_PATH) # single layer
    ds_shallow = gm.load_marthe_grid(DATA_PATH, shallow_only=True) # single layer
    assert np.size(ds_shallow.zone) == 2862
    assert np.all(ds.zone == ds_shallow.zone)

    ds_shallow = gm.load_marthe_grid('./tests/data/hallue_multilayer.permh', shallow_only=True)  # 3lay
    assert np.size(ds_shallow.zone) == 2862
    assert np.all(ds.zone == ds_shallow.zone)

    ds = gm.load_marthe_grid('./tests/data/Somme_V3_Surfex.permh')  # nest
    ds_shallow = gm.load_marthe_grid('./tests/data/Somme_V3_Surfex.permh', shallow_only=True)  # nest
    assert np.size(ds_shallow.zone) == 250537  # all 3 nested and masked val should be there
    assert np.all(ds.x == ds_shallow.x)
    assert np.all(ds.y == ds_shallow.y)
    assert np.all(ds.dx == ds_shallow.dx)
    assert np.all(ds.dy == ds_shallow.dy)
    # gm.dropna(ds)
    # gm.dropna(ds_shallow)

    ds = gm.load_marthe_grid('./tests/data/craie_npc_gig.permh')  # nets+nlay
    ds1 = ds.where(ds['z'] ==1, drop=True)
    ds_shallow = gm.load_marthe_grid('./tests/data/craie_npc_gig.permh', shallow_only=True)  # nets+nlay
    assert np.size(ds_shallow.zone) == np.size(ds1.zone)


def test_load_gm_with_path_object():
    from pathlib import Path
    ds = gm.load_marthe_grid(Path(DATA_PATH), drop_nan=True)
    assert isinstance(ds, xr.Dataset)
    assert ds.zone.size == 927


def test_read_grid_times_int_fmt():
    # test reading times with integer format in pastp file
    # complementary to test_io_read_time.test_read_times_int_fmt()
    # unit test vs integration test
    head = gm.load_marthe_grid(
        './tests/data/chasim_albien.out',
        fpastp='./tests/data/albien.pastp',
        xyfactor=1e3
    )
    assert np.allclose(head.time.data, np.array([1840, 1935, 1970, 1995, 2005, 2012]))


def test_get_dims_from_ds_with_nan():
    ds = gm.load_marthe_grid('./tests/data/craie_npc_gig.permh', 'PERMEAB', add_id_grid=True)
    dims = gm.get_dims_from_attrs(ds)

    assert gm.get_dims_from_ds(ds) == dims


def test_get_dims_from_ds_with_non_nested_grid():
    ds = gm.load_marthe_grid(DATA_PATH, VAR, add_id_grid=True)
    dims = gm.get_dims_from_attrs(ds)

    assert gm.get_dims_from_ds(ds) == dims


def test_get_dims_from_ds_without_nan():
    ds = gm.load_marthe_grid('./tests/data/craie_npc_gig.permh', 'PERMEAB', add_id_grid=True, drop_nan=True)
    dims = gm.get_dims_from_attrs(ds)

    assert gm.get_dims_from_ds(ds) != dims

    ds2 = gm.load_marthe_grid('./tests/data/craie_npc_gig.permh', 'PERMEAB', add_id_grid=True)
    ds2 = ds2.where(ds['permeab'] != 0, drop=True)

    assert gm.get_dims_from_ds(ds) == gm.get_dims_from_ds(ds2)


@pytest.mark.skipif(not BENCHMARK_AVAILABLE, reason="pytest-benchmark not found")
@pytest.mark.benchmark
def test_perf_read_grid(benchmark):
    benchmark(gm.load_marthe_grid, DATA_WITH_TIME, drop_nan=True)


def test_path_134():
    # up to version 0.4.0, max paths lenght in Fortran was 132
    # this test checks that for version > 0.4.0, the file is read even with
    # a path length of more than 132
    import shutil
    from pathlib import Path
    d = Path('./tests/tmp_outputs', 'y' * 140)
    d.mkdir(exist_ok=True)
    f = Path(d, 'g.out')                     # len(p) == 153
    shutil.copy('./tests/data/chasim_hallue_2var.out', f)
    ds = gm.load_marthe_grid(f, 'CHARGE')
    f.unlink()
    d.rmdir()


if __name__ == "__main__":
    pytest.main([__file__, '-v', '--no-cov'])
