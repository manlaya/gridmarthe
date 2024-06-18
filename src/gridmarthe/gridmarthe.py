#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import os, re
from datetime import datetime

import pandas as pd
import numpy as np
import xarray as xr #needs netcdf4


from . import lecsem


""" LECSEM
    Fortran modules created/compiled by JPV
    funcs to read chasim from JPV 
    Adaptation to multilayer and nested grids, AM
    memo : file.out read as seq => all layer then nested grid and all layers too. And so on for every timestep.
    coords with no value read as 1e+20
    zvar read as a single 1D array for every timestep
    
    with decorator accessor, after read (gridmarthe.load_marthe_grid()) xr.Dataset methods can be called directly on read object
    new methods are added with `mart` accessor.
    
    # TODO:
    in utils, xarray ok
    in lec, just use netcdf4 ?
    avoid pandas too ?
    
    
    Example:
        import gridmarthe as gm
        ds = gm.load_marthe_grid('chasim.out')
        ds.resample(time='M').mean() # xr.Dataset method
        ds.mart.assign_coords() # func from gridmarthe.gridmarthe
    
"""

# http://cfconventions.org/Data/cf-standard-names/current/build/cf-standard-name-table.html
# pas vraiment, pour respecter la convention, le nom de variable le plus proche est : water_table_depth / mais on parle de charge pas prof
# proposition à faire dans https://github.com/cf-convention/discuss/issues
# water_table_altitude or level?
VARS_ATTRS = {
    'permeab': {'varname': 'PERMEAB', 'units': 'm/s' , 'missing_value': 0.   , 'standard_name': '', 'long_name': 'aquifer_hydraulic_conductivity'},
    'charge' : {'varname': 'CHARGE' , 'units': 'm'   , 'missing_value': 9999., 'standard_name': 'water_table_level', 'long_name': 'groundwater head'}, #depth
    'saturat': {'varname': 'SATURAT', 'units': '%'   , 'missing_value': 9999., 'standard_name': 'water_table_saturation', 'long_name': 'groundwater_saturation'},
    'debit'  : {'varname': 'DEBIT'  , 'units': 'm3/s', 'missing_value': 9999., 'standard_name': '', 'long_name': 'flow'},
    'debit_rivi'    : {'varname': 'DEBIT_RIVI'   , 'units': 'm3/s', 'missing_value': 9999., 'standard_name': 'water_volume_transport_in_river_channel', 'long_name': 'river_discharge_flow'},
    'qech_riv_napp' : {'varname': 'QECH_RIV_NAPP', 'units': 'm3/s', 'missing_value': 9999., 'standard_name': '', 'long_name': 'surface_groundwater_exchange_flow'},
}


def read_dates_from_pastp(fpastp, encoding='ISO-8859-1'):
    # reading file as raw df - not str ; faster with pandas func
    pastp = pd.read_csv(
        fpastp,
        header=None,
        encoding=encoding
    ).squeeze('columns')

    # First, get steady state time
    idx_0  = pastp.loc[pastp.str.contains(' \*\*\* D.*but de la simulation.*')].index.values[0]
    date_0 = re.findall(r'[0-9]+', pastp.iloc[idx_0] )
    
    # convert as DF
    timesteps = pd.DataFrame([{
        'TimeStep': 0, 
        'Date': datetime(int(date_0[2]), int(date_0[1]), int(date_0[0]) ) 
    }])

    # Then, get all ending times for transient state
    idx  = pastp.loc[pastp.str.contains('^ \*\*\* Le pas.*\d+: se termine.*')]
    # extract dates from strings
    dates= pd.DataFrame(
        idx.str.findall(r'[0-9]+').to_list(),
        columns=['TimeStep', 'day', 'month', 'year'],
        #dtype={'TimeStep':int, 'day':int, 'month':int, 'year':int}
    )
    
    # assign dtype
    dates['TimeStep'] = pd.to_numeric(dates['TimeStep'])

    # convert data as datetime object
    dates['Date'] = pd.to_datetime(dates[['day', 'month', 'year']])
    dates = dates.drop(['month','year', 'day'], axis=1)
    
    return pd.concat([timesteps, dates], axis=0)


def scan_var(xfile):
    var = lecsem.modgridmarthe.scan_typevar(xfile) # get a list of unique type_var that are in xfile
    var = np.char.strip(np.char.decode(var, 'ISO-8859-1')) # decode byte array provided by f2py
    var = var[var != ''] # get rid of empty element provided by fortran code
    return var

def read_marthe_grid(xfile, varname='CHARGE', shallow_only=False):
    """ Read a Marthe grid file
    using fortran wrapper, for a specific variable
    
    Parameters
    ----------
    
    xfile   (str): filename to read
    varname (str): string of variable in xfile to get values. Default is CHARGE (groundwater head)
    
    Returns
    -------
    
    zvar    (np.array): variable read from marthe grid file as numpy ndarray (one vector)
    zdates  (np.array): array of dates (from start))
    isteps  (np.array): array of indexes of timesteps
    zxcol   (np.array): array of x coordinates
    zylig   (np.array): array of y coordinates
    zdxlu   (np.array): array of dx (equals np.diff(x))
    zdylu   (np.array): array of dy (equals np.diff(y))
    ztitle  (np.array): title of marthe grid file read
    dims    (np.array): list of dimensions of grid [maingrid[x, y, z], nestedgrid1[...], ...]
    
    """
    nu_zoomx = lecsem.modgridmarthe.scan_nu_zoomx(xfile) # scan nb of nested grids (gig)
    dims, nbsteps = lecsem.modgridmarthe.scan_dim(xfile, varname, nu_zoomx)
    nbtot = np.prod(dims, axis=1).sum() # product deprecated => prod // DeprecationWarning: `product` is deprecated as of NumPy 1.25.0, and will be removed in NumPy 2.0. Please use `prod` instead.
    if nbtot == 0:
        raise ValueError(f'Varname ({varname}) not found in xfile. No data to parse.')
    
    if shallow_only:
        res = list(lecsem.modgridmarthe.read_grid_shallow( xfile, varname, nbsteps, dims[0][-1] ,nbtot, nu_zoomx ))
    else:
        res = list(lecsem.modgridmarthe.read_grid( xfile, varname, nbsteps, nbtot, nu_zoomx))
    
    res.append(dims)
    return res


def transform_xcoords(zxcol, zylig, zdxlu, nlayer=1, factor=1):
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

def transform_ycoords(zxcol, zylig, zdylu, nlayer=1, factor=1):
    yligs, dylus = [], []
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

def set_layers(dims):
    # add layer to match dim of zvar
    zlay = []
    for igig in range(len(dims)):
        for z in range(dims[igig][-1]):
            zlay.append(np.tile(z+1, dims[igig][0] * dims[igig][1]))
    zlay = np.hstack(zlay)
    return zlay

def decode_title(title, encoding='ISO-8859-1'):
    title = title.decode(encoding)
    title = re.search('(\D+)\s+Pas\s+\d+;', title)
    if title is not None:
        return title.group(1).strip()
    else:
        return None

def get_col_and_lig(dims):
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
        ligs = np.append( ligs, np.tile( np.repeat(zligs, zcols.shape[0]), grid[-1] ) )
    return cols.astype(np.int32), ligs.astype(np.int32)

def get_id_grid(dims):
    # add id grid : 0 = main grid, >0 = nested grid(s)
    id_grids = []
    for igig in range(len(dims)):
        id_grids.append(np.tile(igig, np.prod(dims[igig])))
    id_grids = np.hstack(id_grids)
    return id_grids


def marthe_grid_as_nc(*args, **kwargs):
    return open_mgrid(*args, **kwargs)

def open_mgrid(*args, **kwargs):
    print("Warning, open_mgrid is deprecated, please use load_marthe_grid() in the future")
    return load_marthe_grid(*args, **kwargs)

def load_marthe_grid(
    filename,
    varname=None,
    dates=None,
    fpastp=None,
    nanval=None,
    dropna=False,
    xyfactor=1,
    # shallow_only=False,
    keepligcol=False,
    add_id_grid=False,
    title=None,
    var_attrs={},
    model_attrs={
        'resolution_units': 'm',
        'projection'      : 'epsg:27572',
        'domain'          : 'FR-France',
    },
    verbose=True
):
    """ LECSEM python wrapper
    Fortran modules from marthe src wrapped for python module
    
    memo :  file.out read as seq => all layer then nested grid and all layers too. And so on for every timestep.
            coords with no value read as 1e+20
            zvar read as a single 1D array for every timestep
    
    Parameters
    ----------
        filename    (str):  A path to marthegrid file (*.permh, *.out, etc.)
        varname     (str):  variable to access in martgrid file, e.g `CHARGE` for groundwater head. See marthegrid file content.
                            if None  is passed (default), function will scan all varnames in filename and keep first only
                            if 'all' is passed,  function will scan all varnames in filename and keep all. All datavars are added to dataset, using recursive call to func
                            if wrong variable name is passed, empty data will be returned.
        dates       (sequence, Optionnal): Can be a pd.date_range, pd.Series, pd.DatetimeIndex, np.array or list of datetime/np.datetime objects.
                                           If no dates (or no fpastp) is provided, a fake sequence of dates from 1850 to 1900 will be used for xarray object
        fpastp      (str, Optionnal)     : A pastp file to read for dates
        nanval      (float, Optionnal)   : A code value for nan values. Default is 9999.
        dropna      (bool, Optionnal)    : Drop nan values (corresponding to nanval) in xarray object to return, default is False (keep nan values).
        xyfactor    (int or float, Optionnal): factor to transform X and Y values. e.g.: 1000 to convert km XY to meters. Default is 1.
        keepligcol  (bool, Optionnal): Add columns (col) and rows (lig) index (from 1 to n), Default is False.
        add_id_grid (bool, Optionnal): Add grid id (from 0 to n), useful for nested grids. 0 is main grid, Default is False
        title       (str , Optionnal): Title for grid attributes. Default is None (not used)
        var_attrs   (dict, Optionnal): Dictionnary of attributes to add to variable DataArray.
        model_attrs (dict, Optionnal): Dictionnary of attributes to add to Dataset.
                                       by default, gis attrs are added and can be modified
                                    'resolution_units': 'm',
                                    'projection'      : 'epsg:27572',
                                    'domain'          : 'FR-France',
        verbose     (bool, Optionnal): Print some information about execution in stdout. Default is False.
    
    Returns
    -------
        ds (xr.Dataset): a xarray.Dataset object containing values and attributes read from Marthe grid file.
    
    """
    
    # Fortran error cause sys exit. To avoid this, we add a test on file first
    if not os.path.exists(filename):
        raise FileNotFoundError("File : `{}` does not exist. Please check syntax/path.".format(filename))
    
    if varname is None:
        if verbose:
            print("Warning, no varname passed to function `read_marthe_grid`. Taking the first varname in filename")
        varname = scan_var(filename)
        if verbose:
            print('Variables founded: ', varname)
        if len(varname) >= 1:
            varname = varname[0]
        else:
            # if no varname read from scan, it can be a bug (some version of marthe did not write field name in metadata)
            raise ValueError('No variable founded in file, please consider clean it (cleanmgrid util or winmarthe)')

    elif varname == 'all':
        varname  = scan_var(filename)
        # -- recursive call
        arrays = []
        for var in varname:
            arrays.append( load_marthe_grid(
                filename, var, dates, fpastp, nanval, dropna, xyfactor,
                keepligcol, add_id_grid, title, var_attrs, model_attrs, verbose
            ) )
        return xr.merge(arrays)
        
    elif varname.islower():
        varname = varname.upper() # in marthegridfiles, varnames are always uppercase; if user pass lowercase, this avoid error/empty array
    
    # --- read var, xycoords, timesteps, etc. from file
    (
        zvar, zdates, isteps, zxcol,
        zylig, zdxlu, zdylu, ztitle, dims
    ) = read_marthe_grid(filename, varname) #, shallow_only=shallow_only)
    
    # --- transform data and parse into xarray.Dataset
    if title is None:
        title = decode_title(ztitle)
    
    # memo: dims = [maingrid[x, y, z], gig1[x, y, z], ...]
    xcols, dxlus = transform_xcoords(zxcol, zylig, zdxlu, nlayer=dims[0][-1], factor=xyfactor)
    yligs, dylus = transform_ycoords(zxcol, zylig, zdylu, nlayer=dims[0][-1], factor=xyfactor)
    
    if varname == '': varname = 'variable' # security if force mode
    vattrs = VARS_ATTRS.get(varname.lower(), {})
    vattrs.update(var_attrs)
    dic_data = {
        varname.lower() : (["time", "zone"], zvar, vattrs), #dict(**vattrs, **var_attrs)
        'x'  : ("zone", xcols, {'units': 'm', 'axis': 'X',  'coverage_content_type' : "coordinate"}), #'standard_name': 'longitude',
        'y'  : ("zone", yligs, {'units': 'm', 'axis': 'Y',  'coverage_content_type' : "coordinate"}), #'standard_name': 'latitude' ,
        'dx' : ("zone", dxlus),
        'dy' : ("zone", dylus)
    }
    
    if keepligcol:
        if len(dims) > 1:
            add_id_grid = True # force to add id_grid if nested grid
        cols, ligs   = get_col_and_lig(dims)
        dic_data['col'] = ("zone", cols)
        dic_data['lig'] = ("zone", ligs)
    
    if add_id_grid:
        dic_data['id_grid'] = ("zone", get_id_grid(dims))
    
    if dims[0][-1] > 1:
        zlus = set_layers(dims)
        zattrs = {'units': '-', 'axis': 'Z', 'positive': 'down', 'standard_name': 'depth', 'long_name': 'aquifer_layer'} # not if full 3D ! TODO better
        dic_data['z'] = ("zone", zlus, zattrs) # ajout lay
        
    if fpastp is not None:
        # add dates from a pastp file, case of non-uniform timesteps or edition not set every timestep
        timesteps = read_dates_from_pastp(fpastp)
        dates = timesteps.loc[timesteps['TimeStep'].isin(isteps), 'Date'].values
        dates = pd.DatetimeIndex(dates) # only for frequency
    elif dates is None:
        if verbose:
            print('Warning: No dates or fpastp provided, using default (fake) dates to constructed xarray object.')
        dates = pd.date_range('1850', '1900', len(isteps))
    
    
    ds = xr.Dataset(
        data_vars=dic_data,
        coords={
            'time': dates,
            'zone': range(1, zvar.shape[1] + 1),
            # 'x': (['zone'], xcols),
            # 'y': (['zone'], yligs),
            # 'domain_size': dims, # add non dimension coordinate for info
            # 'domain_origin': [(x0, y0) for igig in grids], # add non dimension coordinate for info
        },
        attrs={
            # attrs must be string, int, float
            'conventions'         :'CF-1.10', # check https://cfconventions.org/
            'title'               : title,
            'marthe_grid_version' : 9.0,
            'original_dimensions' : 'x,y,z [grids]: ' + '; '.join([ ' '.join(map(str, x)) for x in dims]),
            'lon_resolution'      : ', '.join(map(str, np.unique(dxlus))),
            'lat_resolution'      : ', '.join(map(str, np.unique(dylus))),
            'scale_factor'        : xyfactor,
            'extend'              : "xymin : {} {}; xymax: {} {}".format(np.min(xcols), np.min(yligs), np.max(xcols), np.max(yligs)),
            'frequency'           : '{} day(s)'.format(str(dates.to_series().diff().mean().days)),
            'period'              : '{}-{}'.format(pd.to_datetime(dates.min()).year, pd.to_datetime(dates.max()).year), # force pd.date_time, case of pastp => numpydatetime64 / # np.datetime_as_string(i, unit='M')
            'creation_date'       : 'Created on {}'.format(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ UTC')),
            'institution'         : 'BRGM, French Geological Survey, Orléans, France',
            'comment'             : 'Hydrogeological model created with MARTHE code (Thiery, D. 2020. Guidelines for MARTHE v7.8 computer code for hydro-systems modelling. report BRGM/RP-69660-FR).',
            **model_attrs,
        }
    )
    
    if dropna:
        if nanval is None:
            nanval = vattrs.get('missing_value', 9999.) # if no  user defined nanval, try to get corresponding val in dict then 9999. if not present
        ds = dropnan(ds, varname, nanval)
    
    return ds

def dropnan(ds, varname, nanval):
    """ Drop nan values for 1D (or 2D (time, zone)) array
    zone must me a coordinate dimension.
    """
    mask = ds[varname.lower()].where(ds[varname.lower()] != nanval).dropna(dim='zone') # drop nanval
    ds_no_nan = ds.sel(zone=mask['zone'])
    return ds_no_nan


def assign_coords(da_in, add_lay=True, coords=['x', 'y', 'z'], keep_zone=False):
    """ assign coords to set a 1D or 2D (time, zone) array to 3D or 4D 
    """
    if len(coords) == 3:
        z_coords = da_in.get(coords[2], None) # assert z is here, or bypass
    else:
        z_coords = None
    
    if add_lay is False:
        # in some case, even if z is included it should not be treated as coord (ex. plot outcrop)
        z_coords = None
    
    da = da_in.assign_coords(
        x=('zone', np.around(da_in[coords[0]].data, 1) ),
        y=('zone', np.around(da_in[coords[1]].data, 1) ),
    )
    dims = ['y', 'x']
    
    if z_coords is not None:
        da = da.assign_coords(z=('zone', da_in[coords[2]].data))
        dims.insert(0, 'z')
    
    da = da.set_index(zone=dims)
    if not keep_zone:
        da = da.drop_duplicates('zone').unstack('zone') # drop duplicates is a security for nested grids, if dropnan was not performed
    return da.sortby(dims)


def stack_coords(ds, coords=['z', 'y', 'x'], dropna=False):
    """ Transform a 3 or 4D aray into 1 or 2D array 
    inverse of : assign_coords()
    """
    # create zone index
    coords = [d for d in coords if d in ds.coords.keys()] # make sure to drop coords that are not present
    dims = np.prod( [len(ds[d]) for d in coords] ) # create new zone dim
    zone = np.arange(dims)
    
    # stack coords
    ds2 = ds.copy().stack(zone=coords) # multiindex zone grouping coords key
    
    # keep only zone as dim
    ds3 = ds2.drop_vars(['zone'] + coords).assign_coords(zone=('zone', zone))
    
    # get back xy[z] as var
    for c in coords:
        ds3[c] = ('zone', ds2[c].data)
    
    if dropna:
        ds3 = ds3.dropna(dim='zone')
    return ds3



def reset_geometry(ds, permh, variable='permeab', fillna=False, nanval=0.):
    """ Reset a Marthe grid geometry based on permh dataset
    All values (nan, nested grid margins) should be included in
    permh dataset.
    Join is performed with xy[z] (if xy are present in coords) or zone
    to get zone back in full domain (if dropped, or nan were dropped, etc.)
    Useful before writting marthe grid (full domain is needed) 
    """
    da = ds.copy()
    if 'x' in da.coords.keys():
        da = stack_coords(da, dropna=True)
        coords = [x for x in da.coords.keys() if x in ['x', 'y', 'z']] # if xy assert only existing coords in xyz
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
        # tmp = tmp.fillna(nanval) # no because, different codes for nested or not.
        tmp[variable] = np.where(np.isnan(tmp[variable]), grid['inactive'], tmp[variable])
    tmp = tmp.drop('inactive', axis=1)
    tmp = tmp.set_index(['time', 'zone']).to_xarray()
    tmp.attrs = ds.attrs # get back attrs
    return tmp


# def __reset_geometry_from_zone(ds, permh, variable='permeab', nanval=0.):
#     """ Reset a Marthe grid geometry based on permh dataset
#     All values (nan, nested grid margins) should be included in
#     permh dataset.
#     Join is performed with zone to get back all zone (if zone with nanval was dropped)
#     """

#     return tmp

# def reset_geomtry(ds, permh, variable='permeab', nanval=0., mode='zone'):
#     """ Reset a Marthe grid geometry based on permh dataset
#     All values (nan, nested grid margins) should be included in
#     permh dataset.
#     Wrapper func:
#         if mode='xy'    Join is performed with xy[z] to get zone back in full domain
#         if mode='zone'  Join is performed with zone to get back all zone (if zone with nanval was dropped)
#     """
#     if mode == 'xy':
#         return __reset_geometry_from_xy(ds, permh, variable, nanval)
#     elif mode == 'zone':
#         return __reset_geometry_from_zone(ds, permh, variable, nanval)
#     else:
#         raise ValueError('Unknown option `mode` : {}. Please use either "xy" or "zone"'.format(mode))


def parse_dims(str_dims):
    return [list(map(int, x.split(' '))) for x in str_dims.strip('x, y, z [grids]: ').split('; ')]

def datetime64_to_float(zdates, origin='1970-01-01T00:00:00'):
    # Memo: here, origin should be defined from pastp (time since timestep 0)
    idate = (zdates - np.datetime64(origin)) / np.timedelta64(1, 's')
    idate = np.where(idate < 0., 0., idate) # fake dates from load_marthe_grid will be set to 0, meaning timestep -9999. (eg used in parameters grids)
    return idate

def is_sorted(a):
    return np.all(a[:-1] <= a[1:])

def sort_data(ds):
    # TODO:
    # s'assurer de l'ordre si ds a été retravaillé :
        # order by z, y, x
    # extraire les x, y, dx, dy selon dims = pas de doublons
    print('not yet available')

def extract_zvar(ds, varname, dims=None):
    
    zvar    = ds[varname].data
    zdates  = ds.time.data
    zxcol   = ds.x.data
    zylig   = ds.y.data
    zdxlu   = ds.dx.data
    zdylu   = ds.dy.data
    # from pymarthe :         dx, dy = map(abs, map(np.gradient, [xcc,ycc])) # Using the absolute gradient TODO
    ztitle  = ds.attrs.get('title', '')
    if dims is None:
        dims = parse_dims(ds.attrs.get('original_dimensions', None))
    izdates = datetime64_to_float(zdates)

    return (
        zvar, zdates,
        zxcol, zylig, zdxlu, zdylu,
        ztitle, dims, izdates
    )
    
def write_marthe_grid(ds, fileout='toto.out', varname='charge', atitle='', dims=None, debug=False):
    # ds should contain x, y, dx, dy, attrs[['title', 'original_dimensions']]
    # TODO more flexible
    
    (
        zvar, zdates,
        zxcol, zylig, zdxlu, zdylu,
        ztitle, dims, izdates
    ) = extract_zvar(ds, varname, dims)

    if dims is None:
        raise ValueError("""Original dimensions cannot be None.\
Attributes was not founded in dataset so pleave provide a list with original domain dimensions
""")
    
    status = lecsem.modgridmarthe.write_grid(
        xvar=zvar,
        xcol=zxcol,
        ylig=zylig,
        dxlu=zdxlu,
        dylu=zdylu,
        typ_don=varname.upper(),
        titsem=atitle, #TODO debug use of ztitle
        n_dims=dims,
        nval=len(zvar[0]),
        ngrid=len(dims),
        nsteps=len(zdates),
        dates=izdates,
        debug=debug,
        xfile=fileout
    )

    if status != 0:
        print("\033[1;31m\nEDISEM Status={}\033[0m\n".format(status))
        print("""Ooops ! Something bad happen when writting Marthe Grid.
Please check array consistency (9999. or 0. for nan values
[ie, do not drop nan val before write or use `gm.stack_coords()`]) or coordinates order [zyx] """)
    
    return status 


if __name__ == '__main__':
    
    print(lecsem.__doc__)
    print(lecsem.modgridmarthe.__doc__)
    
