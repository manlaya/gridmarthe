
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np

import gridmarthe as gm
from gridmarthe.functions import (
    _extract_zvar_from_ds,
    _parse_dims_from_xr_attrs,
    # modgridmarthe
)


def test_extract_var():
    martfile = './tests/data/Somme_V3_Surfex.permh'  # nested
    varname  = 'PERMEAB'

    ds = gm.load_marthe_grid(martfile, varname)
    dims = _parse_dims_from_xr_attrs(ds.attrs.get('original_dimensions'))
    (
        zvar, zdates,
        zxcol, zylig, zdxlu, zdylu,
        ztitle, izdates
    ) = _extract_zvar_from_ds(ds, varname.lower())
    
    assert np.prod(np.array(dims), axis=1).sum() == np.size(zvar), \
    'Expected dimensions and actual dimension of array do not match'
    
    # help(gm.lecsem.modgridmarthe.write_grid)
    # modgridmarthe.write_grid(
    #     zvar=zvar,
    #     xcol=zxcol,
    #     ylig=zylig,
    #     dxlu=zdxlu.round(2),
    #     dylu=zdylu.round(2),
    #     typ_don=varname.upper(),
    #     titsem='ztitle',
    #     n_dims=dims,
    #     nval=len(zvar[0]),
    #     ngrid=len(dims),
    #     nsteps=len(zdates),
    #     dates=izdates,
    #     debug=True,
    #     xfile='tests/res/test.out'
    # )


def _single_test_write_marthe_grid(martfile, varname, fout):

    # test normal (time still a dimension/axis)
    ds1 = gm.load_marthe_grid(martfile, varname, drop_nan=True, nan_value=[0., -9999.])
    status = gm.write_marthe_grid(ds1, fout, varname='permeab', file_permh=martfile)
    assert status == 0, "write_marthe_grid test, with permh file and dropna, failed"

    # test sel time
    ds2 = gm.load_marthe_grid(martfile, varname)
    status = gm.write_marthe_grid(ds2.isel(time=0), fout, varname='permeab')
    assert status == 0, "write_marthe_grid test with sel(time) failed"

    # also test reading the written file
    ds3 = gm.load_marthe_grid(fout, varname, drop_nan=True, nan_value=[0., -9999.])
    assert 'permeab' in ds3.data_vars, "re-read written file failed"
    assert ds3.permeab.shape == ds1.permeab.shape, "re-read written file shape mismatch"
    assert np.allclose(ds3.permeab.values, ds1.permeab.values, equal_nan=True), \
        "write_marthe_grid re-read written file values mismatch"
    
    print("==================================================")
    print(f"write_marthe_grid test passed for file {martfile}")


def test_write_marthe_grid():
    martfile = './tests/data/hallue.permh'  # simple, single layer
    varname  = 'PERMEAB'
    fout = './tests/res/grid.out'
    _single_test_write_marthe_grid(martfile, varname, fout)


def test_write_marthe_grid_nested():
    martfile = './tests/data/Somme_V3_Surfex.permh'  # nested
    varname  = 'PERMEAB'
    fout = './tests/res/grid.out'
    _single_test_write_marthe_grid(martfile, varname, fout)


def test_write_marthe_grid_multilayer():
    martfile = './tests/data/craie_npc_gig.permh'  # multilayer and nested
    varname  = 'PERMEAB'
    fout = './tests/res/grid.out'
    _single_test_write_marthe_grid(martfile, varname, fout)


if __name__ == "__main__":
    
    test_write_marthe_grid()