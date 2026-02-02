import os
from typing import Union

import pandas as pd
import xarray as xr
import numpy as np

from gridmarthe.core import (
    _calc_flow_directions,
    _transform_xcoords,
    _transform_ycoords,
    _decode_title
)

from gridmarthe.grid.conventions import (
    _parse_global_attrs,
    _assign_xy_attrs,
    VARS_ATTRS
)


def calc_flow_directions(
    ftopo: str,
    fpresence: Union[str,None] = None,
    flow_dirs_type: str = "marthe",
    eps_topo: float = 0.1,
    var_attrs: dict = {},
    xyfactor: Union[int, float] = 1.,
    epsg: int = 27572,
    model_attrs: dict = {
        'domain' : 'FR-France',
        'institution': 'BRGM, French Geological Survey, Orléans, France'
    },
    engine: str = 'xarray',

):
    """ Calculate flow dirction based on topography

    Parameters
    ----------
    ftopo: str
        A path to topography file (.topo)

    fpresence: str, optional
        A path to presence of area surface file.
        If None (by default) is passed, it is set as the topography file path.

    flow_dirs_type: str, optional
        Type of D8 flow directions, e.g. ``marthe`` or ``ArcGis`` or ``Qgis``.

        By default, it is ``marthe``.

        If ``marthe`` is passed:
            1001 -- North,     1002 -- East,      1003 -- South,     1004 -- West
            1005 -- Northeast, 1006 -- Southeast, 1007 -- Southwest, 1008 -- Northwest
            9999 -- for any grid cell adjacent to the edge of the domain.

        If ``ArcGis`` is passed:
            1 -- East,  2 -- Southeast,  4 -- South,  8 -- Southwest
            16 -- West, 32 -- Northwest, 64 -- North, 128 -- Northeast
            0 -- for any grid cell adjacent to the edge of the domain.

        If ``Qgis`` is passed:
            1 -- East,  2 -- Northeast,  3 -- North,  4 -- Northwest
            5 -- West,  6 -- Southwest,  7 -- South,  8 -- Southeast
            0 -- for any grid cell adjacent to the edge of the domain.

    eps_topo: float, optional
        Correction d'altitude unitaire (?), a positif float value.
        By default, it is 0.1. Any negatif value will be replace by 0.1

    var_attrs: dict, optional
    Dictionnary of attributes to add to variable DataArray.

    epsg: int, optional
        EPSG code for projection. Default is 27572 for legacy reasons (Lambert 2 Etendu, for France).
        Used to write CRS information in attributes. Useful for GUI (eg visualisation in QGIS).

    model_attrs: dict, optional
        Dictionnary of attributes to add to Dataset.
        by default, gis attrs are added and can be modified

    engine: str, optional
        Engine to use for returned object. Default is 'xarray', which return xarray.Dataset object.
        Another option is 'numpy', which return a list of numpy arrays :
        [zvar, zdates, isteps, zxcol, zylig, zdxlu, zdylu, ztitle, dims]

    Returns
    -------
    ds: xr.Dataset
        A xarray.Dataset object containing flow direction values and attributes.

    Three files are saved automatically.
        A calculated flow directions file named ``ddr_dir_aval.d_ava``
        A corrected topography file named ``ddr_topo_corr.topog``
        A listing file named ``ddr_calc_flow_direction.listing``

    TODO: For esay implementation, modgridmarthe.read_grid is used in '_parse_gridmarthe.py' to return
        ds attributes

    Example:
        >>> import gridmarthe as gm
        ... ds = gm.calc_flow_directions(ftopo='./tests/data/craie_npc.topog',
        ...                         fpresence='./tests/data/craie_npc.topog',
        ...                         flow_dirs_type='marthe',
        ...                         eps_topo=0.1
        ... )
    """
    if fpresence is None:
        fpresence = ftopo

    fout_dir=os.path.abspath(os.path.join(os.path.dirname(ftopo), "ddr_dir_aval.d_ava"))
    fout_topo=os.path.abspath(os.path.join(os.path.dirname(ftopo), "ddr_topo_corr.topop"))
    flisting=os.path.abspath(os.path.join(os.path.dirname(ftopo), "ddr_calc_flow_direction.txt"))

    if flow_dirs_type.lower() == "marthe":
        ityp_direct=0
    elif flow_dirs_type.lower() == "arcgis":
        ityp_direct=1
    elif flow_dirs_type.lower() == "qgis":
        ityp_direct=2
    else:
        raise Exception("Unknown type of D8 flow directions.")

    if (eps_topo <= 0.):
        eps_topo = 0.1

    (
        zvar, zdates, isteps, zxcol,
        zylig, zdxlu, zdylu, ztitle, dims
    ) = _calc_flow_directions(fpresence, ftopo, fout_dir, fout_topo, flisting, ityp_direct, eps_topo)

    if engine == 'numpy':
        return [zvar, zdates, isteps, zxcol, zylig, zdxlu, zdylu, ztitle, dims]

    # # --- Create xarray.Dataset object
    is_nested = False # no nested
    title = _decode_title(ztitle)
    xcols, dxlus = _transform_xcoords(zxcol, zylig, zdxlu, nlayer=dims[0][-1], factor=xyfactor)
    yligs, dylus = _transform_ycoords(zxcol, zylig, zdylu, nlayer=dims[0][-1], factor=xyfactor)

    varname = 'DIRECT_AVAL'
    vattrs = VARS_ATTRS.get(varname.lower(), {})
    vattrs.update(var_attrs)
    _coords_attrs = _assign_xy_attrs(epsg)
    dic_data = {
        varname.lower() : (["time", "zone"], zvar, vattrs), #dict(**vattrs, **var_attrs)
        'x'  : ("zone", xcols, _coords_attrs.get('x', {})),
        'y'  : ("zone", yligs, _coords_attrs.get('y', {})),
        'dx' : ("zone", dxlus),
        'dy' : ("zone", dylus)
    }
    dates = pd.date_range('1850', '1900', 1)

    xyfactor = 1
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

    ds['zone'].attrs['compress'] = "y x"

    return ds
