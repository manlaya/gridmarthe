#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later
#
#    This file is part of gridmarthe.
#
#    gridmarthe is a python library to manage grid files for
#    MARTHE hydrogeological computer code from French Geological Survey (BRGM).
#    Copyright (C) 2024  BRGM
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

import re
import numpy as np

from .coremod import modgridmarthe         # compiled fortran module


class FortranError(Exception):
    def __init__(self, message, iostat):
        self.message = message
        super().__init__(self.message)
        self.iostat = iostat

    def __str__(self):
        return f"Error Code: {self.iostat}: {self.message}"


def _datetime64_to_float(zdates, origin='1970-01-01T00:00:00'):
    # Memo: here, origin should be defined from pastp (time since timestep 0)
    idate = (zdates - np.datetime64(origin)) / np.timedelta64(1, 's')
    # fake dates from load_marthe_grid will be set to 0,
    # meaning timestep -9999. (eg used in parameters grids)
    idate = np.where(idate < 0., 0., idate)
    return idate


def _scan_dim_py(xfile):
    with open(xfile, 'r', encoding='ISO-8859-1') as f:
        head = [next(f) for x in range(25)]
    head = '\n'.join(head)

    ncol = int(re.search(r'Ncolumn=(\d+)', head, re.MULTILINE).group(1))
    nrow = int(re.search(r'Nrows=(\d+)', head, re.MULTILINE).group(1))
    return [[ncol, nrow, 1]]


def scan_var(xfile):
    """ List all variables stored in a Marthe grid file """
    var = modgridmarthe.scan_typevar(xfile)  # get a list of unique type_var that are in xfile
    var = np.char.strip(np.char.decode(var, 'ISO-8859-1'))  # decode byte array provided by f2py
    var = var[var != '']  # get rid of empty element provided by fortran code
    return var


def _read_marthe_grid(xfile, varname=None, shallow_only=False):
    """ Read a Marthe grid file
    using fortran wrapper, for a specific variable

    Parameters
    ----------
    xfile: str
        Filename to read
    varname : str
        string of variable in xfile to get values.
        Default is None (retrieve first variable found in xfile)

    Returns
    -------
    zvar  : np.array
        variable read from marthe grid file as numpy ndarray (one vector)
    zdates: np.array
        array of dates (from start))
    isteps: np.array
        array of indexes of timesteps
    zxcol : np.array
        array of x coordinates
    zylig : np.array
        array of y coordinates
    zdxlu : np.array
        array of dx (equals np.diff(x))
    zdylu : np.array
        array of dy (equals np.diff(y))
    ztitle: np.array
        title of marthe grid file read
    dims  : np.array
        list of dimensions of grid [maingrid[x, y, z], nestedgrid1[...], ...]
    """
    # nu_zoomx = modgridmarthe.scan_nu_zoomx(xfile)  # scan nb of nested grids (gig)
    dims, nbsteps = modgridmarthe.scan_dim(
        xfile, varname if varname is not None else ''
    )

    dims = dims[~np.all(dims == 0, axis=1), :]  # filter out dims, as fortran initiate large array with 0
    nu_zoomx = dims.shape[0] - 1  # update nb of nested grids (gig) from dims
    nbtot = np.prod(dims, axis=1).sum()

    if nbtot == 0:
        if not shallow_only:
            raise ValueError(f'Varname ({varname}) not found in xfile. No data to parse.')
        else:
            dims = _scan_dim_py(xfile)
            nbtot =  np.prod(dims, axis=1).sum()
            nbsteps, nu_zoomx = 1, 0

    if dims[0][-1] == 0:
        raise ValueError(
            f'Main grid has 0 layer. Please check your file ({xfile})'
            f' and variable name ({varname}). If missing metadata, '
            'try to use `cleanmgrid` command line tool to fix it.'
        )

    if shallow_only:
        res = list(modgridmarthe.read_grid_shallow(xfile, varname, nbsteps, dims[0][-1] ,nbtot, nu_zoomx))
    else:
        res = list(modgridmarthe.read_grid(xfile, varname, nbsteps, nbtot, nu_zoomx))

    res.append(dims)
    return res


def _transform_xcoords(zxcol, zylig, zdxlu, nlayer=1, factor=1):
    xcols, dxlus = [], []
    for igig in range(zxcol.shape[0]):
        nb = np.extract(zylig[igig] != 1e+20, zylig[igig]).shape[0]
        xcols2 = np.tile(zxcol[igig], nb)
        xcols2 = np.extract(xcols2 != 1e+20, xcols2)
        dxlus2 = np.tile(zdxlu[igig], nb)
        dxlus2 = np.extract(dxlus2 != 1e+20, dxlus2)
        if nlayer > 1:
            # need to paste coords for multilayer to match dims of zvar
            xcols2 = np.tile(xcols2, nlayer)
            dxlus2 = np.tile(dxlus2, nlayer)
        xcols.append(xcols2)
        dxlus.append(dxlus2)
    xcols = np.hstack(xcols)*factor
    dxlus = np.hstack(dxlus)*factor
    return xcols, dxlus


def _transform_ycoords(zxcol, zylig, zdylu, nlayer=1, factor=1):
    yligs, dylus = [], []
    zxcol = zxcol[~np.all(zxcol == 1e+20, axis=1)]  # filter out zxcol, as fortran initiate large array with 1e+20
    zylig = zylig[~np.all(zylig == 1e+20, axis=1)]  # filter out zxcol, as fortran initiate large array with 1e+20
    for igig in range(zylig.shape[0]):
        yligs2, dylus2 = [], []
        for i in range(len(zxcol[igig][zxcol[igig] != 1e+20])):
            tmp1 = zylig[igig][zylig[igig] != 1e+20]
            tmp2 = zdylu[igig][zdylu[igig] != 1e+20]
            if nlayer > 1:
                # need to paste coords for multilayer to match dims of zvar
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


def _set_layers(dims):
    # add layer to match dim of zvar
    zlay = []
    for igig in range(len(dims)):
        for z in range(dims[igig][-1]):
            zlay.append(np.tile(z+1, dims[igig][0] * dims[igig][1]))
    zlay = np.hstack(zlay)
    return zlay #.astype(np.int32)


def _decode_title(title, encoding='ISO-8859-1'):
    title = title.decode(encoding)
    title = re.search(r'(\D+)\s+Pas\s+\d+;', title)
    if title is not None:
        return title.group(1).strip()
    else:
        return None


def _get_col_and_lig(dims):
    """ Add col/lig indexes (i,j) """
    # cols are xcoords index (x are sorted asc)
    # ligs are ycoords index (y are sorted dsc)
    # dims = [maingrid[x, y, z], gig[x, y, z], ...]
    # cols and lig indexes are a range from 1 to len(x), for each grid. Same index col/lig, for every layer (z dim).
    cols, ligs = [], []
    for grid in dims:
        zcols = np.arange(1, grid[0]+1)
        zligs = np.arange(1, grid[1]+1) # lig 0 is max y ; max lig is min y.
        # add res tiled on y and z dims, for xcols
        cols = np.append(cols, np.tile(zcols, grid[-1] * grid[1]))
        # for ylig, it's a bit different, we need to map ylig on shape of xcol for each ylig, then tile on z dim
        # e.g. we need:
        # [xcol] 1, 2, 3, 4, 5
        # [ylig]   [ value ]
        # 1,     1  1  1  1  1
        # 2,     2  2  2  2  2
        # 3,     ...
        # but flattened, so: repeat ylig value on xcol size, then tile on z_dim size
        ligs = np.append(ligs, np.tile(np.repeat(zligs, zcols.shape[0]), grid[-1]))
    return cols.astype(np.int32), ligs.astype(np.int32)


def _get_id_grid(dims):
    # add id grid : 0 = main grid, >0 = nested grid(s)
    id_grids = []
    for igig in range(len(dims)):
        id_grids.append(np.tile(igig, np.prod(dims[igig])))
    id_grids = np.hstack(id_grids)
    return id_grids


def _get_dims_from_attrs(str_dims):
    if str_dims is None:
        return None
    else:
        _tmp = str_dims.replace('x, y, z [grids]: ', '').split('; ')
        return [list(map(int, x.split(' '))) for x in _tmp]


# def sort_data(ds):
    # TODO:
    # s'assurer de l'ordre si ds a été retravaillé :
        # order by z, y, x, dx
    # extraire les x, y, dx, dy selon dims = pas de doublons
    # print('not yet available')


def _compute_dxdy():
    # TODO
    raise NotImplementedError


def _extract_zvar_from_ds(ds, varname):

    zvar    = ds[varname].data
    zdates  = ds.time.data
    zxcol   = ds.x.data
    zylig   = ds.y.data
    zdxlu   = ds.dx.data
    zdylu   = ds.dy.data
    ztitle  = ds.attrs.get('title')
    izdates = _datetime64_to_float(zdates) if isinstance(zdates[0], np.datetime64) else zdates

    return (
        zvar, zdates,
        zxcol, zylig, zdxlu, zdylu,
        ztitle, izdates
    )

def _calc_flow_directions(
    file_presence, file_topo, file_out_direct,
    file_out_topo, file_listing, ityp_direct, eps_top
):
    res1 = modgridmarthe.calc_flow_direct(
        file_presence, file_topo, file_out_direct,
        file_out_topo, file_listing, ityp_direct, eps_top
    )
    # nu_zoomx = modgridmarthe.scan_nu_zoomx(file_out_direct)  # scan nb of nested grids (gig)
    varname = ''
    dims, nbsteps = modgridmarthe.scan_dim(file_out_direct, varname) # nu_zoomx
    nu_zoomx = dims.shape[0] - 1  # update nb of nested grids (gig) from dims
    dims = dims[~np.all(dims == 0, axis=1), :]  # filter out dims, as fortran initiate large array with 0
    dims[0][-1] = 1
    nbtot = np.prod(dims, axis=1).sum()

    res = list(modgridmarthe.read_grid(file_out_direct, varname, nbsteps, nbtot, nu_zoomx))
    # print(res)
    # dims[0][-1] = 0
    res.append(dims)
    return res

def _calc_riv_network(file_presence_in, file_flowdir_in, ityp_dir, surf_riv, nperio_reach, n_neigh_station, file_exis_riv_in,
                      file_drainage_surf_in, file_xy_surf_hydro_station, file_col_row_sous_bv_in, file_nb_sous_bv_out,
                      file_exis_riv_out, file_drainage_surf_out, file_riv_branch_tree_out, file_num_afflu_out, file_riv_tronc_out,
                      file_histo_out, file_sous_bassin_out, file_listing):

    modgridmarthe.calc_riv_network(file_presence_in, file_flowdir_in, ityp_dir, surf_riv, nperio_reach, n_neigh_station, file_exis_riv_in,
                      file_drainage_surf_in, file_xy_surf_hydro_station, file_col_row_sous_bv_in, file_nb_sous_bv_out,
                      file_exis_riv_out, file_drainage_surf_out, file_riv_branch_tree_out, file_num_afflu_out, file_riv_tronc_out,
                      file_histo_out, file_sous_bassin_out,  file_listing)


if __name__ == '__main__':

    # print(_lecsem.__doc__)
    print(modgridmarthe.__doc__)
