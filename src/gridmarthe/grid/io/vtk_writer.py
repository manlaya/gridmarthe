#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gridmarthe.operasem.vtk_writer

Export gridmarthe grid to vtk format, using `vtkwriters` python library
(https://gitlab.com/brgm/geomodelling/io/vtkwriters)
"""

from pathlib import Path
from datetime import datetime

import numpy as np
import vtkwriters as vtkw


def _get_vertices_connectivity(geom):
    """ Get vertices and connectivity from marthe grid geometry, for pvd export

    Parameters
    ----------
    geom : xr.Dataset
        The grid to convert. Needs to have all geometry informations/variables.
        See :py:func:`gridmarthe.compute_geometry`

    Returns
    -------
    np.ndarray, np.ndarray, str
        The vertices, connectivity and cell type ('voxel')
    """
    # extract grid infos
    # nc = np.shape(geom['x'].data)[-1]  # here we have x (or y) for every center cells
    dx = geom['dx'].data
    dy = geom['dy'].data
    dz = geom['z_upper'].data[0] - geom['z_lower'].data[0]  # only dt=0, assume no grid variation during time
    zc = geom['z_upper'].data[0] - dz/2
    cc = np.stack((geom['x'].data, geom['y'].data, zc), axis=-1)  # center cells array

    # cell nodes (8 nodes per cell)
    cn = np.reshape(np.tile(cc, 8), (-1, 8, 3))

    # use voxel vtk cell types (this could be changed)
    cn[:, [0, 2, 4, 6], 0] -= dx[:, None]  # left side
    cn[:, [1, 3, 5, 7], 0] += dx[:, None]  # right side
    cn[:, [0, 1, 4, 5], 1] -= dy[:, None]  # front side
    cn[:, [2, 3, 6, 7], 1] += dy[:, None]  # rear side
    cn[:, [0, 1, 2, 3], 2] -= dz[:, None]  # bottom side
    cn[:, [4, 5, 6, 7], 2] += dz[:, None]  # top side

    # vertices
    vertices = np.reshape(cn, (-1, 3))
    # cell nodes connectivity: self-explicit no nodes is duplicated
    connectivity = np.arange(vertices.shape[0])
    connectivity.shape = -1, 8

    return vertices, connectivity, "voxel"


def convert_grid_to_vtk(grid, varname, time=None, output_tpl='output/gm_vtk'):
    """ Convert a gridmarthe grid to a vtk grid.

    Parameters
    ----------
    grid : gridmarthe.GridMarthe
        The grid to convert, with variable to export `varname`
        In addition, it needs to have all geometry informations/variables.
        See :py:func:`gridmarthe.compute_geometry`
    varname: str
       name of the variable to export
    time : str or datetime, optional
        time to export, by default None (all times)
    output_tpl : str, optional
       path/template name of file to write. By default, 'output/gm_vtk'.
       Final file names will be `{output_tpl}_{varname}.pvd` and
       `{output_tpl}_{varname}_{time}.pvu`

    Returns
    -------
    None
        Write pvu/pvd files to output directory

    Example
    -------

    >>> import gridmarthe as gm
    >>> model_name = 'hallue_multilayer'
    >>> hsubs = gm.load_marthe_grid('./tests/data/{}.hsubs'.format(model_name), xyfactor=1e3)
    >>> topo  = gm.load_marthe_grid('./tests/data/{}.topog'.format(model_name), xyfactor=1e3)
    >>> permh = gm.load_marthe_grid('./tests/data/{}.permh'.format(model_name), xyfactor=1e3, varname='PERMEAB', drop_nan=True)
    >>> geom = gm.compute_geometry(topo, hsubs).sel(zone=permh.zone.values)
    >>> convert_grid_to_vtk(geom, 'z', time=0, output_tpl='tests/res/vtk/hallue')
    """
    if 'time' not in grid:
        grid = grid.copy().expand_dims({'time': [0]})  # add dummy time dimension

    if time is None :
        time = grid.time.values
    elif isinstance(time, str):
        time = [time]  # convert to list if single time is given
    elif isinstance(time, int):
        time = [grid.time.values[time]]
    elif isinstance(time, datetime):
        time = [time]  # convert to list if single time is given
    elif isinstance(time, (list, np.ndarray)):
        pass  # already a list
    else:
        raise ValueError('time must be a string, datetime or list of datetime')

    if varname not in grid:
        raise KeyError(f"Variable {varname} not found in grid")

    grid = grid.copy().sel(time=time)

    # create a collection of files per timestep
    output_dir = Path(output_tpl).parent
    output_dir.mkdir(exist_ok=True)
    # there is a bug in vtkwriters to handle Path objects, hence this trick
    to_output = lambda s: f"{output_dir}/{s}"

    vertices, cellnodes, celltype = _get_vertices_connectivity(grid)

    snapshots = []
    for i, t in enumerate(time):
        filename = f"output-{i:04d}.vtu"  # TODO, better time name management (strftime, int, etc.)
        vtkw.write_vtu(
            vtkw.vtu_doc(
                vertices,
                cellnodes,
                celltype,
                # as many variable as needed in the celldata dictionnary
                # pointdata argument is also available
                celldata={
                    varname: grid.sel(time=t)[varname].data,
                },
            ),
            to_output(filename),
        )
        snapshots.append((t, filename))

    # write the file describing the simulation (pvd format)
    vtkw.write_pvd(vtkw.pvd_doc(snapshots), to_output("simulation.pvd"))
    return None
