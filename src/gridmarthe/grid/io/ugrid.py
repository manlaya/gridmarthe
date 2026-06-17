#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import xarray as xr

from ..grid_utils import get_default_variable
from ..conventions import UGRID_ATTRS


def _create_corners(ds):
    x_corners = np.column_stack([
        ds.x - ds.dx/2, ds.x + ds.dx/2, ds.x + ds.dx/2, ds.x - ds.dx/2
    ])
    y_corners = np.column_stack([
        ds.y - ds.dy/2, ds.y - ds.dy/2, ds.y + ds.dy/2, ds.y + ds.dy/2
    ])
    return x_corners, y_corners


def _create_faces(ds):
    """ Create faces from a dataset with x, y, dx, dy
    """
    n_zones = ds['zone'].size

    # define vertices (corners of each face)
    x_corners, y_corners = _create_corners(ds)
    vertices_x = x_corners.flatten()
    vertices_y = y_corners.flatten()

    # define connectivity (faces -> nodes)
    # each face i is defined by nodes [4*i, 4*i+1, 4*i+2, 4*i+3]
    _faces = np.arange(n_zones * 4).reshape(n_zones, 4)
    _faces = _faces.astype(np.int32)
    points = np.stack([vertices_x, vertices_y], axis=1)
    # get unique points and inverse indices to get back to original points
    nodes, inverse = np.unique(np.round(points, 3), axis=0, return_inverse=True)
    faces = inverse.reshape(n_zones, 4).astype(np.float32)

    return nodes, faces


def _create_ugrid_dataset(values, varname, xc, yc, nodes, faces, times, layers=None, **attrs):
    # help: https://ugrid-conventions.github.io/ugrid-conventions/#3d-layered-mesh-topology
    # https://ugrid-conventions.github.io/ugrid-conventions/#data-defined-on-unstructured-meshes
    # https://ugrid-conventions.github.io/ugrid-conventions/#fully-3d-unstructured-ie-non-layered-mesh-topology
    # TODO : epxlore the volume coords, volume_connectivity => might be a better solution
    data_dims = ["time", "n_faces"]

    # comment this section as time attrs already written by xarray/netcdf4
    # if datetime64 dtype
    # time_attrs = {}
    # if isinstance(times[0], np.datetime64):
    #     init_time = str(times[0]).split('.')[0]
    #     time_attrs = {
    #         'units' : "days since {}".format(init_time),
    #         'calendar' : "proleptic_gregorian"
    #     }

    if layers is not None:
        # TODO: use this in mulitlayered grids instead of adding a variable for
        # each grids.
        nlay = len(np.unique(layers))
        data_dims.insert(1, "layer")
        z_var = {
            "layer": (["layer"], layers, {
                "standard_name": "model_layer_number",
                "long_name": "layer number",
                "units": "nondimensional",
                "axis": "Z",
                "positive": "down",
            })
        }
    else:
        z_var = {}

    _ = attrs.pop('conventions')  # remove previous conventions from attrs
    uds = xr.Dataset(
        data_vars={
            "mesh_topology": ([], 0, UGRID_ATTRS.get('mesh_topology')),
            "face_node_connectivity": (
                ("n_faces", "n_max_face_nodes"),
                faces.astype(np.float32),
                UGRID_ATTRS.get('face_node_connectivity')
            ),
            "nodes_per_face": (
                ("n_faces",), np.repeat(4, len(faces)),
                UGRID_ATTRS.get('nodes_per_face')
            ),
            varname: (data_dims, values.astype(np.float64), {
                "mesh": "mesh_topology",
                "location": "face",
                "cell_methods": "nMesh2D_face: mean",
                # "grid_mapping" : "projected_coordinate_system"  # variable
            }),
            **z_var
        },
        coords={
            # "time": ("time", times.astype(np.float64), time_attrs),
            # // edit, remove float64 conversion: take advantage of time writing
            # with xarray/netcdf4. Keep this for memory as it leads to issue
            # for visualization in QGIS.
            "time": ("time", times),
            "node_x": (("n_nodes",), nodes[:, 0].astype(np.float32), {
                "standard_name": "projection_x_coordinate",
                "units": "m"
            }),
            "node_y": (("n_nodes",), nodes[:, 1].astype(np.float32), {
                "standard_name": "projection_y_coordinate",
                "units": "m"
            }),
            "face_x": (("n_faces",), xc, {
                "standard_name": "projection_x_coordinate",
                "long_name": "X coordinate of the center of each cell",
                "units": "m",
            }),
            "face_y": (("n_faces",), yc, {
                "standard_name": "projection_y_coordinate",
                "long_name": "Y coordinate of the center of each cell",
                "units": "m",
            }),
        },
        attrs={
            "Conventions": "CF-1.6, UGRID-1.0",
            **attrs
        }
    )
    return uds


def create_ugrid(ds, varname=None):
    """ Create mesh topology following UGRID netCDF convention

    See https://ugrid-conventions.github.io/ugrid-conventions

    Notes
    -----

    This transform allows for vizualization in QGIS as a meshed layer (powered
    by MDAL library).
    As of now, a bug is present with netcdf file writen by h5netcdf engine.
    See https://github.com/lutraconsulting/MDAL/issues/520

    When exporting your dataset, make sure to use the `netcdf4` engine.


    Parameters
    ----------
    ds : xr.Dataset
        A Marthe Dataset as read by gridmarthe
    varname : str, optional
        variable to use in Dataset, by default None (the first non coordinate
        variable is picked)

    Returns
    -------
    xr.Dataset
        A Dataset with UGRID convention variable, e.g. `node_x`, `node_y`,
        `face_node_connectivity`, `mesh_topology`, and assiociated attributes


    Examples
    --------

    >>> import gridmarthe as gm
    >>> ds = gm.load_marthe_grid('./tests/data/hallue.permh')
    >>> uds = create_ugrid(ds)
    >>> uds.to_netcdf('hallue_ugrid.nc', engine='netcdf4')
    """

    ds = ds.copy()

    if varname is None:
        varname = get_default_variable(ds)
    if 'time' not in ds.dims:
        ds = ds.expand_dims('time')

    # if dataset has a z dimension, set it as dim to make a 3D-layered mesh
    if 'z' in ds:
        ds = (
            ds.rename({'z': 'layer'})
            .set_coords('layer')
            .set_index(zone2=["layer", "zone"])
            .unstack('zone2')
        )
        layers = ds.layer.values
        x = np.nanmean(ds.x.values, axis=0)    # aggregate to 2D
        y = np.nanmean(ds.y.values, axis=0)
        dx = np.nanmean(ds.dx.values, axis=0)
        dy = np.nanmean(ds.dy.values, axis=0)
        ds['x'] = ('zone', x)
        ds['y'] = ('zone', y)
        ds['dx'] = ('zone', dx)
        ds['dy'] = ('zone', dy)

        # recursive call with new variable for each layer
        # TODO find a better way of integrating 2D meshed layered data,
        # Avoid loop and add a 3D array (time, layer, faces) ; find a
        # a way to make it work with QGIS/MDAL
        res = []
        for z in layers:
            tmp = ds.sel(layer=z)
            tmp = create_ugrid(tmp, varname)
            tmp = tmp.rename({varname: f'{varname}_{z}'})
            res.append(tmp)
        uds = xr.merge(res, compat='override')
        return uds
    else:
        layers = None

    nodes, faces = _create_faces(ds)
    uds = _create_ugrid_dataset(
        ds[varname].data,
        varname,
        ds.x.values,
        ds.y.values,
        nodes,
        faces,
        times=ds.time.values,
        layers=layers,
        **ds.attrs
    )
    return uds
