
import gridmarthe as gm
from gridmarthe.gridmarthe import _extract_zvar, _parse_dims
import numpy as np


if __name__ == "__main__":
    
    import os;os.chdir('./tests')
    
    martfile = './data/craie_npc.permh'
    martfile = './data/Somme_V3_Surfex.permh'
    varname  = 'PERMEAB'
    
    
    ds = gm.load_marthe_grid(martfile, varname)

    dims = _parse_dims(ds.attrs.get('original_dimensions'))
    (
        zvar, zdates,
        zxcol, zylig, zdxlu, zdylu,
        ztitle, izdates
    ) = _extract_zvar(ds, varname.lower())
    
    np.prod(np.array(dims), axis=1).sum() == np.size(zvar)
    
    # help(gm.lecsem.modgridmarthe.write_grid)
    gm.lecsem.modgridmarthe.write_grid(
        xvar=zvar,
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

    ds2 = gm.load_marthe_grid(martfile, varname, drop_nan=True, nanval=[0.,-9999.])
    gm.write_marthe_grid(ds2, varname='permeab', file_permh=martfile)
