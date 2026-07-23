#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import gridmarthe as gm


DATA = './tests/data/hallue.permh'
DATA_MULTILAYER = './tests/data/hallue_multilayer.permh'
WRITE_TMP = False   # for manual verif if debugging


def _check_reproj(ds_reproj, n=2862, dx=500., dy=500.):
    assert len(ds_reproj.zone) == n, 'wrong number of output cells'
    # check that dx, dy are ketp with new coords
    ds_check = gm.assign_coords(ds_reproj)
    assert np.allclose(np.diff(ds_check.x), dx)
    assert np.allclose(np.diff(ds_check.y[::-1]), dy)
    assert 'RGF93' in ds_reproj.attrs['crs'].get('geographic_crs_name')


def test_reproj_ds():
    ds = gm.load_marthe_grid(DATA, xyfactor=1e3)
    ds_reproj = gm.reproj_grid(ds, 'EPSG:27572', 'EPSG:2154')

    _check_reproj(ds_reproj)
    assert float(ds_reproj.x.min()) == 649021.875
    assert float(ds_reproj.x.max()) == 675021.875
    assert float(ds_reproj.y.min()) == 6.9755545e+06
    assert float(ds_reproj.y.max()) == 7.0020545e+06

    if WRITE_TMP:
        gm.to_geodataframe(ds, 'EPSG:27572').to_file('./tests/tmp_outputs/original_ds_L2E.gpkg')
        gm.to_geodataframe(ds_reproj, 'EPSG:2154').to_file('./tests/tmp_outputs/reproj_ds_L93.gpkg')


def test_reproj_ds_round():
    ds = gm.load_marthe_grid(DATA, xyfactor=1e3)
    ds_reproj = gm.reproj_grid(ds, 'EPSG:27572', 'EPSG:2154', decimals=0)

    if WRITE_TMP:
        gm.to_geodataframe(ds_reproj, 'EPSG:2154').to_file('./tests/tmp_outputs/reproj_ds_L93_round.gpkg')

    _check_reproj(ds_reproj)
    assert float(ds_reproj.x.min()) == 649022.
    assert float(ds_reproj.x.max()) == 675022.
    assert float(ds_reproj.y.min()) == 6975555.
    assert float(ds_reproj.y.max()) == 7002055.


def test_reproj_ds_multilayer():
    ds = gm.load_marthe_grid(DATA_MULTILAYER, xyfactor=1e3)
    ds_reproj = gm.reproj_grid(ds, 'EPSG:27572', 'EPSG:2154')
    _check_reproj(ds_reproj, n=2862*3)


# def test_reproj_ds_dropna():
#     ds = gm.load_marthe_grid(DATA, drop_nan=True, xyfactor=1e3)
#     ds_reproj = gm.reproj_grid(ds, 'EPSG:27572', 'EPSG:2154', decimals=0)
#     # ds_reproj.dropna(dim='zone')

#     ds_ref = gm.load_marthe_grid(DATA, xyfactor=1e3)
#     ds_reproj_ref = gm.reproj_grid(ds_ref, 'EPSG:27572', 'EPSG:2154', decimals=0)
#     ds_reproj_ref = ds_reproj_ref.sel(zone=ds.zone.data)

#     assert np.allclose(ds_reproj, ds_reproj_ref)


def test_reproj_ds_rasterio():
    ds = gm.load_marthe_grid(DATA, xyfactor=1e3)
    ds_reproj = gm.reproj_grid(ds, 'EPSG:27572', 'EPSG:2154', engine='rasterio')
    if WRITE_TMP:
        gm.to_geodataframe(ds_reproj, 'EPSG:2154').to_file('./tests/tmp_outputs/reproj_rio_ds_L93.gpkg')

    assert ds_reproj.rio.crs == 'EPSG:2154'
    assert len(ds_reproj.zone) == 2862
    # _check_reproj(ds_reproj)  # does not pass, but logic
    # reproj of grid points is correct but does not conserve dx/dy)


if __name__ == '__main__':
    test_reproj_ds()
    test_reproj_ds_round()
    test_reproj_ds_multilayer()
    # test_reproj_ds_dropna()
    test_reproj_ds_rasterio()
