#! /usr/bin/env python3
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

import os, warnings

from typing import Union

import pandas as pd
import numpy as np
import xarray as xr

from gridmarthe.core import (
    modgridmarthe,
    _read_marthe_grid,
    _transform_xcoords,
    _transform_ycoords,
    _set_layers,
    _get_id_grid,
    _get_col_and_lig,
    _decode_title,
    _parse_dims_from_xr_attrs,
    _extract_zvar_from_ds,
    scan_var,
    FortranError
)

from ..grid_utils import (
    read_dates_from_pastp,
    assign_coords,
    stack_coords,
    dropna,
    fillna,
    replace,
    get_default_variable
)

from ..conventions import (
    _assign_z_attrs,
    _assign_xy_attrs,
    _parse_global_attrs,
    VARS_ATTRS
)

from .._pkg_utils import deprecated_alias, _check_args


@deprecated_alias(nanval='nan_value')
@deprecated_alias(keepligcol='add_col_row')
def load_marthe_grid(
    filename: str,
    varname: Union[str, None] = None,
    fpastp: Union[str, None] = None,
    dates=None,
    drop_nan: bool = False,
    nan_value: Union[int, float, list, None] = None,
    xyfactor: Union[int, float] = 1.,
    shallow_only=False,
    add_col_row: bool = False,
    add_id_grid: bool = False,
    title: Union[str, None] = None,
    var_attrs: dict = {},
    epsg: int = 27572,
    full_3d: bool = False,
    drop_time: bool = False,
    model_attrs: dict = {
        'domain' : 'FR-France',
        'institution': 'BRGM, French Geological Survey, Orléans, France'
    },
    engine: str = 'xarray',
    verbose: bool=False,
    **kwargs,
):
    """ Read Marthe Grid File as xarray.Dataset

    The gridfile is read as a sequence: the variable for all layer
    for main grid, then all layer for nested grids, is stored in
    a 1D vector for every timestep. A single spatial identifier
    ``zone`` is used to map spatial coordinates.

    Before plot operations, user can assign coordinates (set x,y
    as dimension coordinates and drop zone) to get 2-D arrays (or
    3D arrays if multilayer) for every timesteps.

    Parameters
    ----------
    filename: str
        A path to marthegrid file (.permh, .out, etc.)

    varname : str, optional
        variable to access in martgrid file, e.g ``CHARGE`` for groundwater head.
        See marthegrid file content.
        If None  is passed (default), function will scan all varnames in filename
        and keep first only.
        If 'all' is passed,  function will scan all varnames in filename and keep all.
        All datavars are added to dataset, using recursive call to func
        if wrong variable name is passed, empty data will be returned.

    fpastp: str, optional
        A pastp file to read for dates

    dates: sequence, optional
        Can be a pd.date_range, pd.Series, pd.DatetimeIndex, np.array or list of
        datetime/np.datetime objects.
        If no dates (or no fpastp) is provided, a fake sequence of dates from
        1850 to 1900 will be used for xarray object

    drop_nan: bool, optional
        Drop nan values (corresponding to nan_value) in xarray object to return.
        Default is False (keep nan values).

    nan_value: float or list of float, optional
        A code value for nan values. The default value is inferred from field name.
        E.g. of default nan values:

        - hydraulic conductivity: 0 or -9999. (Warning: a value of +9999. is not
          a NaN value for hydraulic conductivity. See Marthe User Guide for explanation
          about this code, refering here to impervious layer);

        - hydraulic head: 9999.;

        - groundwater flow: 0. (9999. is used as special value for this field);

        - any other: 9999.

    xyfactor: int or float, optional
        factor to transform X and Y values. e.g.: 1000 to convert km XY to meters.
        Default is 1.

    shallow_only: bool, optional
        Boolean to read only the first layer. Default is False.
        Warning: only valid for NON nested grids for now.

    add_col_row: bool, optional
        Add columns (col) and rows (row, formerly lig (v<=0.1.3)) index (from 1 to n).
        Default is False.

    add_id_grid: bool, optional
        Add grid id (from 0 to n), useful for nested grids.
        0 is main grid, Default is False

    title: str , optional
        Title for grid attributes. Default is None (not used)

    var_attrs: dict, optional
        Dictionnary of attributes to add to variable DataArray.

    epsg: int, optional
        EPSG code for projection. Default is 27572 for legacy reasons (Lambert 2 Etendu,
        for France). Used to write CRS information in attributes. Useful for GUI
        (eg visualisation in QGIS).

    full_3d: bool, optional
        Is z dimension an aquifer layer or real Z axis (in meters for exemple)
        Default is False (z is aquifer layer number)

    drop_time: bool, optional
        Drop time dimension even if only one timestep is present.
        Default is False. If True and only one timestep, time dimension is removed.
        Useful for parameters grids.

    model_attrs: dict, optional
        Dictionnary of attributes to add to Dataset.
        by default, gis attrs are added and can be modified

        >>> {
        ...    'domain': 'FR-France',
        ...    'institution': 'BRGM, French Geological Survey, Orléans, France'
        ... }

        For example, if your data is associated with a reference (report, paper, etc.):
        >>> {
        ...    'references': 'https://doi.org/...'
        ... }

    engine: str, optional
        Engine to use for returned object. Default is 'xarray', which return
        xarray.Dataset object.
        Another option is 'numpy', which return a list of numpy arrays :
        [zvar, zdates, isteps, zxcol, zylig, zdxlu, zdylu, ztitle, dims]

    verbose: bool, optional
        Print some information about execution in stdout.
        Default is False.

    Returns
    -------
    ds: xr.Dataset
        A xarray.Dataset object containing values and attributes read from Marthe
        grid file.
    """

    # Fortran error cause sys exit. To avoid this, we add a test on file first
    if not os.path.exists(filename):
        raise FileNotFoundError(
            "File : `{}` does not exist. Please check syntax/path.".format(filename)
        )

    # check if no wrong argument is passed to function, suggest closest match if so
    _check_args(load_marthe_grid, kwargs)

    if varname is None:
        if verbose:
            warnings.warn(
                "Warning, no varname passed to function `_read_marthe_grid`. "
                "Taking the first varname in filename",
                category=UserWarning,
                stacklevel=1,
            )
        varname = scan_var(filename)
        if verbose:
            print('Variables founded: ', varname)
        if len(varname) >= 1:
            varname = varname[0]
        else:
            varname = ''
            # if no varname read from scan, it can be a bug (some version of marthe
            # did not write field name in metadata)
            if not shallow_only:
                raise ValueError(
                    'No variable founded in file, please consider check file or clean it '
                    '(cleanmgrid util or winmarthe)'
                )

    elif varname.lower() == 'all':
        varname  = scan_var(filename)
        # -- recursive call
        arrays = []
        for var in varname:
            arrays.append(load_marthe_grid(
                filename, var, fpastp, dates, nan_value, drop_nan, xyfactor,
                shallow_only, add_col_row, add_id_grid, title, var_attrs, epsg,
                full_3d, drop_time, model_attrs, engine, verbose
            ))
        return xr.merge(arrays, compat='no_conflicts')

    elif varname.islower():
        # in marthegridfiles, varnames are always uppercase;
        # if user pass lowercase, this avoid error/empty array
        varname = varname.upper()

    # --- read var, xycoords, timesteps, etc. from file
    (
        zvar, zdates, isteps, zxcol,
        zylig, zdxlu, zdylu, ztitle, dims
    ) = _read_marthe_grid(filename, varname, shallow_only=shallow_only)

    if engine == 'numpy':
        return [zvar, zdates, isteps, zxcol, zylig, zdxlu, zdylu, ztitle, dims]

    # --- transform data and parse into xarray.Dataset
    if shallow_only:
        # shadow_only(time, gig, values) -> (time, values)
        # for now, only valid for regular (non nested) grids
        # TODO nested grid shallow only?
        zvar = zvar[:, 0, :]

    if title is None:
        title = _decode_title(ztitle)

    # bool to check if nested grid
    is_nested = len(dims) > 1

    # memo: dims = [maingrid[x, y, z], gig1[x, y, z], ...]
    xcols, dxlus = _transform_xcoords(zxcol, zylig, zdxlu, nlayer=dims[0][-1], factor=xyfactor)
    yligs, dylus = _transform_ycoords(zxcol, zylig, zdylu, nlayer=dims[0][-1], factor=xyfactor)

    if varname == '':
        varname = 'variable'  # security if force mode

    # Get attributes
    vattrs = VARS_ATTRS.get(varname.lower(), {})
    vattrs.update(var_attrs)
    _coords_attrs = _assign_xy_attrs(epsg)

    # prepare data
    dic_data = {
        varname.lower() : (["time", "zone"], zvar, vattrs),
    }

    dic_coords = {
        'x'  : ("zone", xcols, _coords_attrs.get('x', {})),
        'y'  : ("zone", yligs, _coords_attrs.get('y', {})),
        'dx' : ("zone", dxlus),
        'dy' : ("zone", dylus)
    }

    if add_col_row:
        if is_nested:
            add_id_grid = True  # force to add id_grid if nested grid
        cols, ligs   = _get_col_and_lig(dims)
        dic_data['col'] = ("zone", cols)
        dic_data['row'] = ("zone", ligs)

    if add_id_grid:
        dic_data['id_grid'] = ("zone", _get_id_grid(dims))

    # if z z dimension exists (multilayer/3D model)
    _has_z_dim = dims[0][-1] > 1
    if _has_z_dim:
        zlus = _set_layers(dims)
        dic_data['z'] = ("zone", zlus, _assign_z_attrs(full_3d)) # add lay

    if fpastp is not None:
        # add dates from a pastp file, case of non-uniform timesteps
        # or edition not set every timestep
        timesteps = read_dates_from_pastp(fpastp)
        dates = timesteps.loc[timesteps['timestep'].isin(isteps), 'date'].values
        dates = pd.DatetimeIndex(dates) # only for frequency
    elif dates is None:
        if verbose:
            warnings.warn(
                'Warning: No dates or fpastp provided, using default (fake) dates'
                'to constructed xarray object.',
                category=UserWarning,
                stacklevel=1
            )
        # dates = pd.date_range('1850', '1900', len(isteps))  // old v_<0.4
        dates = np.arange(len(isteps))  # use integer for dummy time

    # --- Create xarray.Dataset object
    ds = xr.Dataset(
        data_vars=dic_data,
        coords={
            'time': dates,
            'zone': np.arange(1, zvar.shape[1] + 1, dtype=np.int32)
        },
        attrs={
            **_parse_global_attrs(title, dims, xyfactor, dates, is_nested, dxlus, dylus, xcols, yligs, epsg),
            **model_attrs
        }
    )

    if drop_time and ds.sizes['time'] == 1:
        ds = ds.drop_dims('time')

    # add non-dimensionnal coordinates
    # ds = ds.assign_coords(  # future
    # TODO more tests before assigning coords xy (compat?)
    # TODO assign also metadata ? 'domain_size': dims
    ds = ds.assign(
        dic_coords
    )

    # add attributes for Reduced horizontal grid
    # https://cfconventions.org/Data/cf-conventions/cf-conventions-1.11/cf-conventions.html#reduced-horizontal-grid
    ds['zone'].attrs['compress'] = "z y x" if _has_z_dim else "y x"

    # --- Drop NaN values
    if drop_nan:
        if nan_value is None:
             # if no  user defined nanval, try to get corresponding val in dict
             # other, default to 9999.
            nan_value = vattrs.get('missing_value', 9999.)

        if not isinstance(nan_value, (list, tuple)):
            nan_value = [nan_value]
        elif isinstance(nan_value, tuple):
            nan_value = list(nan_value)

        if (
            (varname.lower() == 'permeab' or filename.endswith("permh"))
            and is_nested
            and -9999. not in nan_value
        ):
            nan_value += [-9999.]

        ds = dropna(ds, varname, nan_value)
        # add range zone of active cells. memo: remove tuple to set as dimension
        ds['izone'] = ('zone', np.arange(1, np.size(ds['zone'].data) + 1, dtype=np.int32))

    # FIXME better, prevent bug at write :
    # https://github.com/pydata/xarray/issues/7722
    # https://stackoverflow.com/questions/65019301/variable-has-conflicting-fillvalue-and-missing-value-cannot-encode-data-when
    # del ds[varname.lower()].encoding['missing_value']
    return ds


def reset_geometry(ds, path_to_permh: str, variable='permeab', fillna=False):
    """ Reset a Marthe grid geometry based on permh dataset

    This function is useful/used, to reconstruct the geometry of the dataset
    (if NaN were dropped for example), before writting marthe grid, where the full
    domain is needed (including non active cells).

    Note
    ----

    Join is performed with xy[z] (if xy are present in coords) or zone
    to get zone back in full domain (if dropped, or nan were dropped, etc.).

    If nan were dropped during :py:func:`gridmarthe.load_grid_marthe`, 'zone_all'
    was added and will be used (this variable store the zone index before the reindexing
    during :py:func:`gridmarthe.dropna`).

    Parameters
    ----------
    ds: xr.Dataset

    path_to_permh: str
        path to the .permh file containing domain

    variable: str
        variable (ds key) containing data

    fillna: bool (optional)
        to fillna WITH permh nan value.
        permh nan value are used because it can contain different nan values
        (0 and -9999 for nested grids)
        for simplier nan fills, this can be performed outside of this function.

    Returns
    -------
        xr.Dataset containing original variables and geometry read from permh file
    """
    da = ds.copy()
    # All values (nan, nested grid margins) should be included in permh dataset.
    permh = load_marthe_grid(
        path_to_permh,
        drop_nan=False,
        add_id_grid=True,
        add_col_row=True,
        verbose=False
    )

    if 'x' in da.coords.keys():
        da = stack_coords(da, dropna=True)
        coords = [x for x in da.coords.keys() if x in ['x', 'y', 'z']]  # if xy assert only existing coords in xyz
    else:
        coords = ['zone']

    # to pandas for simplier join/merge operations
    da = da.to_dataframe().reset_index()

    # get real zone back
    grid = permh.to_dataframe().reset_index()
    grid['inactive'] = grid['permeab']
    grid = grid.drop('permeab', axis=1)
    # todo groupby time, loop on time and join grid every timestep... if needed to write with time ?
    # mostly used for parameters...
    tmp = grid.merge(
        da.loc[:, coords+[variable]],
        on=coords,
        suffixes=['', '_y'],
        how='left',
    )
    tmp = tmp.drop(tmp.filter(regex='_y$', axis=1),axis=1) # drop overlapping cols, if there is some.
    if fillna:
        # Do not use .fillna() because different codes are used for nested.
        tmp[variable] = np.where(np.isnan(tmp[variable]), grid['inactive'], tmp[variable])
    tmp = tmp.drop('inactive', axis=1)
    tmp = tmp.set_index(['time', 'zone']).to_xarray()
    tmp.attrs = ds.attrs # get back attrs
    return tmp


def write_marthe_grid(
    ds,
    fileout='grid.out',
    varname=None,
    file_permh: str|None = None,
    nan_value=9999.,
    title=None,
    dims=None,
    force_full_grid=False,
    debug=False
):
    """ Write Dataset as MartheGrid v9 file

    Notes
    -----

    ds should contain x, y, dx, dy, attrs[['title', 'original_dimensions']]
    in case of error, please use :py:func:`gridmarthe.reset_geometry` first.
    When providing a path to ``file_permh`` argument, this is called automatically.

    A good pratice is to provide the permh file when writing dataset to marthegrid format.

    >>> gm.write_marthe_grid(ds, 'toto.out', file_permh='./mymodel/model.permh')

    WARNING: This function was developped to write parameters grids to marthe format.
    Not to recreate simulation results (hydraulic head at several timesteps for example)
    as gridmarthe format.
    This means that this function should not be used for dataset with several timesteps.
    Example, to create a new initial hydraulic head file based on simulation, select the
    timestep in dataset before writing.

    >>> ds = ds_head.isel(time=-1)
    >>> gm.write_marthe_grid(ds, 'mymodel.charg')

    Parameters
    ----------
    ds: xr.Dataset
        dataset containing data, coordinates (x,y[,z]), dx,dy and dimensions (in attrs).
        Data needs to be a reduced horizontal grid (see :py:func:`stack_coords` if needed).

    fileout: str
        filename to write

    varname: str, optional
        variable name (key) containing values. Default is None and variable will
        be inferred from dataset (first non coordinates/dimension variable name).

    file_permh: str, optional
        path to the permh file corresponding to current Marthe model.
        Needed to recreate full dimension if NaN dropped before.

    nan_value: float, optional
        custom value to fillna, when using a `permh` field to reset geometry

    title: str, optional
        title written in marthe grid file

    dims: list of array, optional
        list containing array of dimension for every grid (ie len(dims) > 1 if nested grid)

        - format is `[[x_main_grid, y_main_grid, z_main_grid], [x_nested_1, ...], ...]`
        eg. `[[354,252,2], [182,156,2]]`
        - if only main grid : `[[nx,ny,nz]]`
        - if None (default, dims will be parsed from `ds.attrs['original_dimensions']` which is added
        when read with :py:func:`gridmarthe.load_marthe_grid`. If not present (lost in some computation for example),
        please use py:func:`gridmarthe.reset_geometry` or provide list of dims manually.

    force_full_grid: bool, optional
        force to write full grid (even if grid is constant). Default is False
        By default, Marthe will write a compact form of grid is constant.

    debug: bool, optional
        print debug informations. Default is False

    Returns
    -------
    status: int.
        0 if everything's ok. 1 otherwise.
    """
    # TODO: infer nx, ny, nz, ngrid from ds ? --> allow to create a custom grid
    varname = varname.lower() if varname is not None else get_default_variable(ds)
    ds2 = ds.copy()
    if 'time' not in ds2.dims:
        ds2 = ds2.expand_dims('time')

    nan_value = VARS_ATTRS.get(varname, {}).get('missing_value', 9999.) if nan_value is None else nan_value

    if file_permh is not None:
        # if permeab, fill_na with permh file (because either 0 or -9999.)
        _fill_na = varname == 'permeab'
        # reset geometry with full domain (stored in permh file)
        ds2 = reset_geometry(ds2, path_to_permh=file_permh, variable=varname, fillna=_fill_na)
        if not _fill_na:
            # if not permh variable, fill nan with constant values, based on variable
            if nan_value is None:
                nan_value = VARS_ATTRS.get(varname, {}).get('missing_value', 9999.)
            ds2  = fillna(ds2, varname, nan_value)

    if dims is None:
        dims = _parse_dims_from_xr_attrs(ds2.attrs.get('original_dimensions'))

    # if after parsing, still None, raise error.
    if dims is None:
        raise ValueError(
            "Original dimensions cannot be None."
            "Attributes was not founded in dataset so pleave provide a list with original domain dimensions"
        )

    # --- Check if expected dimensions match variable dimensions
    # if not, recreate full grid with domain grid (permh file)
    _test_shape = np.prod(np.array(dims), axis=1).sum() != np.size(ds2[varname].data)
    if _test_shape:
        # if dimension differs, file_permh is required
        error = "Expected size and actual size (from variable array) differs. "
        error += "Make sure to provide a `permh_file` to reconstruc geometry."
        raise ValueError(error)

    # extract variables from dataset
    (
        zvar, zdates,
        zxcol, zylig, zdxlu, zdylu,
        ztitle, izdates
    ) = _extract_zvar_from_ds(ds2, varname)

    if title is None and ztitle == '':
        title = 'Marthe Grid '  # dummy arg to set type as string

    # assert valid shapes before passing args to fortran edsem
    # fix bug if .isel(time=X) and no permh file
    _shape_var = np.shape(zvar)
    if len(_shape_var) < 2:
        zvar = np.expand_dims(zvar, axis=0)
    if len(np.shape(zdates)) == 0:
        zdates = np.array([zdates])

    # call fortran module to write marthe grid
    status = modgridmarthe.write_grid(
        zvar=zvar,
        xcol=zxcol,
        ylig=zylig,
        dxlu=zdxlu,
        dylu=zdylu,
        typ_don=varname.upper(),
        titsem=title, #TODO debug use of ztitle
        n_dims=dims,
        nval=len(zvar[0]),
        ngrid=len(dims),
        nsteps=len(zdates),
        dates=izdates,
        debug=debug,
        force_full_grid=force_full_grid,
        xfile=fileout
    )

    if status != 0:
        raise FortranError(
            f'Fortran subroutine EDISEM failed with status {status}\n'
            'Please check array consistency : 9999. or 0. for nan values (no np.nan),'
            'do not drop nan val before write or provide a `file_permh`.',
            status
        )

    return status
