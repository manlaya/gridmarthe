
import gridmarthe as gm
from gridmarthe.lecsem import _extract_zvar_from_ds, _parse_dims_from_xr_attrs, modgridmarthe
import numpy as np


if __name__ == "__main__":
    
    import os;os.chdir('./tests')
    
    martfile = './data/craie_npc.permh'   # multilayer
    martfile = './data/Somme_V3_Surfex.permh'  # nested
    martfile = './data/hallue.permh'  # simple, single layer
    varname  = 'PERMEAB'
    
    
    ds = gm.load_marthe_grid(martfile, varname)

    dims = _parse_dims_from_xr_attrs(ds.attrs.get('original_dimensions'))
    (
        zvar, zdates,
        zxcol, zylig, zdxlu, zdylu,
        ztitle, izdates
    ) = _extract_zvar_from_ds(ds, varname.lower())
    
    np.prod(np.array(dims), axis=1).sum() == np.size(zvar)
    
    # help(gm.lecsem.modgridmarthe.write_grid)
    modgridmarthe.write_grid(
        zvar=zvar,
        xcol=zxcol,
        ylig=zylig,
        dxlu=zdxlu.round(2),
        dylu=zdylu.round(2),
        typ_don=varname.upper(),
        titsem='ztitle',
        n_dims=dims,
        nval=len(zvar[0]),
        ngrid=len(dims),
        nsteps=len(zdates),
        dates=izdates,
        debug=True,
        xfile='test.out'
    )

    # t = np.arange(1, 2862)
    # t2 = np.arange(1, 2862, dtype=np.int32)
    # t.dtype
    # t2.dtype
    # np.allclose(t, t2)

    ds2 = gm.load_marthe_grid(martfile, varname, drop_nan=True, nanval=[0.,-9999.])
    gm.write_marthe_grid(ds2, varname='permeab', file_permh=martfile)
