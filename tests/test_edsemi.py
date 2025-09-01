
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import gridmarthe as gm
# from gridmarthe.lecsem import _extract_zvar_from_ds, _parse_dims_from_xr_attrs, modgridmarthe


def test_write_marthe_grid():
    
    # martfile = './tests/data/craie_npc.permh'   # multilayer
    # martfile = './tests/data/hallue.permh'      # simple, single layer
    martfile = './tests/data/Somme_V3_Surfex.permh'  # nested
    varname  = 'PERMEAB'
    fout = './tests/res/grid.out'
    
    # ds = gm.load_marthe_grid(martfile, varname)
    # dims = _parse_dims_from_xr_attrs(ds.attrs.get('original_dimensions'))
    # (
    #     zvar, zdates,
    #     zxcol, zylig, zdxlu, zdylu,
    #     ztitle, izdates
    # ) = _extract_zvar_from_ds(ds, varname.lower())
    
    # np.prod(np.array(dims), axis=1).sum() == np.size(zvar)
    
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
    #     xfile='test.out'
    # )

    # t = np.arange(1, 2862)
    # t2 = np.arange(1, 2862, dtype=np.int32)
    # t.dtype
    # t2.dtype
    # np.allclose(t, t2)

    ds2 = gm.load_marthe_grid(martfile, varname, drop_nan=True, nanval=[0.,-9999.])
    status = gm.write_marthe_grid(ds2, fout, varname='permeab', file_permh=martfile)
    assert status == 0, "write_marthe_grid test failed"

    # also test reading the written file
    ds3 = gm.load_marthe_grid(fout, varname, drop_nan=True, nanval=[0.,-9999.])
    assert 'permeab' in ds3.data_vars, "re-read written file failed"
    assert ds3.permeab.shape == ds2.permeab.shape, "re-read written file shape mismatch"
    assert np.allclose(ds3.permeab.values, ds2.permeab.values, equal_nan=True), "re-read written file values mismatch"
    print("write_marthe_grid test passed")

