#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import lecsem as gm
import pandas as pd
import numpy as np
import xarray as xr

""" LECSEM
# Fortran modules created/compiled by JPV
# funcs to read chasim from JPV 
# Adaptation to multilayer and nested grids, AM
# memo : file.out read as seq => all layer then nested grid and all layers too. And so on for every timestep.
# coords with no value read as 1.00000e+20
# zvar read as a single 1D array
"""

# TODO tester avec plusieurs variables
# ==> vérifier la lecture de la variable choisie

def read_chasim_charges(xfile, varname='CHARGE'):
    nu_zoomx = gm.modgridmarthe.scan_nu_zoomx(xfile) # scan nb of nested grids (gig)
    dims, nbsteps = gm.modgridmarthe.scan_dim(xfile, varname, nu_zoomx)
    nbtot = np.product(dims, axis=1).sum()
    res = list(gm.modgridmarthe.read_grid( xfile, varname, nbsteps, nbtot, nu_zoomx))
    res.append(dims)
    return res

def transform_xcoords(zxcol, zylig, zdxlu, nlayer=1, factor=1):
    xcols, dxlus = [], []
    for igig in range(zxcol.shape[0]):
        nb = np.extract(zylig[igig] != 1e20, zylig[igig]).shape[0]
        xcols2 = np.tile(zxcol[igig], nb)
        xcols2 = np.extract(xcols2 != 1e20, xcols2)
        dxlus2 = np.tile(zdxlu[igig], nb)
        dxlus2 = np.extract(dxlus2 != 1e20, dxlus2)
        if nlayer > 1:
            # need to paste coords for multilayer to match dims of zvar
            # dim = ncol*nlig*nlay*ngig
            xcols2 = np.tile(xcols2, nlayer)
            dxlus2 = np.tile(dxlus2, nlayer)
        xcols.append(xcols2)
        dxlus.append(dxlus2)
    xcols = np.hstack(xcols)*factor
    dxlus = np.hstack(dxlus)*factor
    return xcols, dxlus

def transform_ycoords(zxcol, zylig, zdylu, nlayer=1, factor=1):
    yligs, dylus = [], []
    for igig in range(zylig.shape[0]):
        yligs2, dylus2 = [], []
        for i in range(len(zxcol[igig][zxcol[igig] != 1e+20])):
            tmp1 = zylig[igig][zylig[igig] != 1e+20]
            tmp2 = zdylu[igig][zdylu[igig] != 1e+20]
            if nlayer > 1:
                # need to paste coords for multilayer to match dims of zvar
                # dim = ncol*nlig*nlay*ngig
                tmp1 = np.tile(tmp1, nlayer)
                tmp2 = np.tile(tmp2, nlayer)
            yligs2.append(tmp1)
            dylus2.append(tmp2)
        yligs2 = np.vstack(yligs2).transpose().flatten()
        dylus2 = np.vstack(dylus2).transpose().flatten()
        yligs.append(yligs2)
        dylus.append(dylus2)
    yligs = np.hstack(yligs)*factor
    dylus = np.hstack(dylus)*factor
    return yligs, dylus

def set_layers(dims):
    # add layer to match dim of zvar
    zlay = []
    for igig in range(len(dims)):
        for z in range(dims[igig][-1]):
            zlay.append(np.tile(z+1, dims[igig][0] * dims[igig][1]))
    zlay = np.hstack(zlay)
    return zlay

def assign_coords(da_in):
    # TODO, add layer (z) only if nb_lay > 1 ? for lighter files
    da = da_in.assign_coords(
        x=  ('zone', np.around(da_in['x'].data, 1) ),
        y = ('zone', np.around(da_in['y'].data, 1) ),
        z = ('zone', np.around(da_in['z'].data, 1) ),
    )
    da = da.set_index(zone=['z', 'y', 'x']).unstack('zone')
    da = da.sortby('z').sortby('y').sortby('x')
    return da
    

def marthe_grid_as_nc(filename, dates, varname='CHARGE', title='marthe model'):
    (
        zvar, zdates, isteps, zxcol,
        zylig, zdxlu, zdylu, dims
    ) = read_chasim_charges(xfile=filename, varname=varname)
    
    xcols, dxlus = transform_xcoords(zxcol, zylig, zdxlu, nlayer=dims[0][-1])
    yligs, dylus = transform_ycoords(zxcol, zylig, zdylu, nlayer=dims[0][-1])
    zlus = set_layers(dims)

    # TODO add condition to add z only if n_layer > 1
    ds = xr.Dataset(
        data_vars=dict(
            charge=(["time", "zone"], zvar),
            x=("zone", xcols),
            y=("zone", yligs),
            z=("zone", zlus), # ajout lay
            dx=("zone", dxlus),
            dy=("zone", dylus)
        ),
        coords={
            'time': dates,
            'zone': range(1, zvar.shape[1] + 1)
        },
        attrs={
            'modname': title,
            'Marthe_Grid_version': 9.0,
            # 'Units' : 'should be xr.DataArray.attrs'
        }
    )
    
    return ds

if __name__ == '__main__':
    import matplotlib.pyplot as plt
    
    print(gm.__doc__)
    print(gm.modgridmarthe.__doc__)
    
    xfiles={'hallue': 'chasim_hallue.out'}
    xfiles={'mart-npc': 'chasim_npc_gig.out'}
    
    # TODO: merge martpy.read_past() (AM) here, to get timesteps with grid edition
    date_range_1 = pd.date_range('2020-11-01', '2020-12-31', freq='M')   # fake dates for testing
    date_range_2 = pd.date_range('2020-12-01', '2020-12-31', freq='M')   # fake dates for testing
    # date_range_100 = date_range_100.insert(0, '1958-7-31')

    date_range = {
        'hallue'  : date_range_1,
        'mart-npc': date_range_2,
    }

    for modele, filename in xfiles.items():
        dates = date_range[modele]
        
        ds = marthe_grid_as_nc(filename, dates, varname='CHARGE')
        masque = ds['charge'].where(ds['charge'] != 9999.).dropna(dim='zone') # drop nan_val
        ds = ds.sel(zone=masque['zone'])
        ds.to_netcdf('{0}_CHARGES.nc'.format(modele))

        dsbis = assign_coords(ds)
        # dsbis['charge'].plot.pcolormesh(x='x', y='y', row='z', col='time')
        # Pour les gigognes, la grille irrégulière créée rend discontinu le graphique
        # soit interpol, soit geopandas --> polyg.
        dsbis['charge'].sel(z=[6,9]).plot.pcolormesh(x='x', y='y', row='z', col='time')
        # dsbis['charge'].sel(z=[4,6,10]).plot.imshow(x='x', y='y', row='z', col='time')
        plt.show()
        plt.close()
