#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
from gridmarthe import functions


XFILE, VAR = './tests/data/chasim_hallue_2var.out', "CHARGE"


def test_lecsem_scan_dim():

    nu_zoomx = functions.modgridmarthe.scan_nu_zoomx(XFILE) # scan nb of nested grids (gig)
    dims, nbsteps = functions.modgridmarthe.scan_dim(XFILE, VAR, nu_zoomx)
    
    assert isinstance(dims, np.ndarray)
    assert dims.shape[0] == nu_zoomx + 1
    assert dims.shape[1] == 3  # x, y, z
    assert isinstance(nbsteps, int)
    assert nbsteps > 0
    print("test_lecsem_scan_dim passed")


def test_lecsem_scan_typevar():

    var = functions.modgridmarthe.scan_typevar(XFILE)
    var = np.char.strip(np.char.decode(var, 'utf-8'))
    var = var[var != '']

    assert isinstance(var, np.ndarray)
    assert var.size > 0
    assert all(isinstance(v, str) for v in var)
    print("test_lecsem_scan_typevar passed")


def test_lecsem_read_marthe_grid():

    (
        zvar, zdates, isteps, zxcol,
        zylig, zdxlu, zdylu, ztitle, dims
    ) = functions._read_marthe_grid(XFILE, VAR, shallow_only=False)
    
    assert isinstance(zvar, np.ndarray)
    assert np.prod(dims, axis=1).sum() == np.size(zvar)

    assert np.size(zxcol[zxcol != 1e+20]) == dims[:,0].sum()
    assert np.size(zylig[zylig != 1e+20]) == dims[:,1].sum()
    assert np.size(zdxlu[zdxlu != 1e+20]) == np.size(zxcol[zxcol != 1e+20])
    assert np.size(zdylu[zdylu != 1e+20]) == np.size(zylig[zylig != 1e+20])

    print("test_lecsem_read_marthe_grid passed")


def test_lecsem_transform_coords():
    # TODO
    pass


def main():
    test_lecsem_read_marthe_grid()
    test_lecsem_scan_dim()
    test_lecsem_scan_typevar()
    print('==================')
    print('lecsem test passed')


if __name__ == "__main__":
    main()
