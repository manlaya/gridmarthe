
import gridmarthe as gm

if __name__ == "__main__":

    martfile = './data/craie_npc.permh'
    varname  = 'PERMEAB'
    ds = gm.load_marthe_grid(martfile, varname)

    (
        zvar, zdates,
        zxcol, zylig, zdxlu, zdylu,
        ztitle, dims, izdates
    ) = gm.extract_zvar(ds, varname.lower())

    # help(gm.lecsem.modgridmarthe.write_grid)
    gm.lecsem.modgridmarthe.write_grid(
        xvar=zvar,
        xcol=zxcol,
        ylig=zylig,
        dxlu=zdxlu,
        dylu=zdylu,
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
