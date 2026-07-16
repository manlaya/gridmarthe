#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd

from .gutils import _polygonize


# or get_transect
def slice_cross_section(grid, x=None, y=None, agg_along_axis=None):
    """ grid needs geom infos and to have x,y as dimension.
    See :py:func:`gridmarthe.compute_geometry` and :py:func:`gridmarthe.assign_coords`

    Parameters
    ----------
    grid: xarray.Dataset
        Dataset with geometry infos, x,y as dimensions.

    x, y : float, optional
        Coordinates on which search for cross section transect.

    agg_along_axis : str, optional
       If not None, aggregate along axis (mean). Accepted values are 'x' or 'y'.

    Returns
    -------
    xr.Dataset
        Dataset for cross section transect.

    Examples
    --------
    >>> geom = gm.compute_geometry(topo, hsub, mask.zone)
    >>> ds_2d = gm.assign_coords(geom)
    >>> ds_xsection = slice_cross_section(ds_2d, x=6.116e5)
    """
    # idea: set from bbox...
    # slice not authorized in sel with nearest
    # npoints=100
    coords = {
        'x': x,
        'y': y,
        # 'x': np.linspace(x1, x2, npoints),
        # 'x': slice(*[x1, x2]),
        # 'y': slice(*[y1, y2]),
    }
    coords = {k: v for k, v in coords.items() if v is not None}
    crossect = grid.sel(method='nearest', **coords)  # tolerance=2e3
    if agg_along_axis is not None:
        crossect = crossect.mean(dim=(agg_along_axis), skipna=True)

    return crossect


def _mk_cross_section_geom(ds_xsection):
    """ Create polygon geometries for cross section plot

    Parameters
    ----------
    ds_xsection : xarray.Dataset
        dataset sliced on cross section transect. Geometry informations
        `z_upper`, `z_lower`, `dx` and `dy` must be present.
        See :py:func:`gridmarthe.compute_geometry`
    mode : str, optional
        Mode of cross section ('x' or 'y', default is 'x'). Wether the cross
        section is done along x or y axis.

    Returns
    -------
    pd.DataFrame
        dataframe with geometry column `geom`

    Notes
    -----
    - TODO: more flexible transect
    """
    if 'time' in ds_xsection.dims:
        ds_xsection = ds_xsection.copy().isel(time=0)
    # Warning, the following is True only in the current state of
    # slicing along one full axis. The remaining coordinates is scalar
    # and therefore not a dimension in the data array
    if 'x' in ds_xsection.dims:
        mode = 'x'
    elif 'y' in ds_xsection.dims:
        mode = 'y'
    else:
        raise ValueError('Argument `ds_xsection` has no x or y dimension coordinates.')

    df = ds_xsection.to_dataframe().reset_index().dropna()
    grp = df.groupby(['x', 'y'])
    geoms = []
    for _, dff in grp:
        geoms.append(pd.DataFrame(
            _polygonize(
                np.round(dff[mode].values - dff[f'd{mode}'].values/2, 2),
                dff['z_lower'].values,
                np.round(dff[mode].values + dff[f'd{mode}'].values/2, 2),
                dff['z_upper'].values
            ),
            index=dff.index,
            columns=['geom']
        ))

    df = df.join(pd.concat(geoms))
    return df
