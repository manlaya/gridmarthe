#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import xarray as xr
import geopandas as gpd
from shapely.geometry import Polygon
import shapely

from gridmarthe.core import _get_dims_from_attrs, _get_extend_from_attrs
from ..conventions import _parse_global_attrs, _assign_xy_attrs, _assign_z_attrs
from ..grid_utils import _nearest_node
from ..processing.gis import to_geodataframe


def create_grid_domain(
    x0,
    y0,
    dx,
    dy,
    nx=None,
    ny=None,
    x1=None,
    y1=None,
    nlayer=1,
    default_value=1.,
    epsg=None,
):
    """ Create a Marthe grid domain as an xarray DataArray

    The MARTHE grid domain is a 3D grid with permeability values.
    This function creates a grid domain with a given origin, cell size, and
    dimensions. The grid is initialized with a default value.

    Parameters
    ----------
    x0 : float
        X coordinate of the origin (bottom-left if dy>0 usually, or top-left?)
        Marthe origin convention: Lower Left corner.
    y0 : float
        Y coordinate of the origin.
    dx : float
        Cell size in X direction.
    dy : float
        Cell size in Y direction.
    nx : int, optional
        Number of cells in X direction. Required if x1 is None.
    ny : int, optional
        Number of cells in Y direction. Required if y1 is None.
    x1 : float, optional
        X coordinate of the opposite corner (Upper Right). Used to compute nx if
        nx is None.
    y1 : float, optional
        Y coordinate of the opposite corner (Upper Right). Used to compute ny if
        ny is None.
    nlayer : int, optional
        Number of layers, by default 1.
    default_value : float, optional
        Default permeability value for the grid cells, by default 1.
    epsg : int, optional
        EPSG code of the coordinate reference system, by default None.

    Returns
    -------
    xarray.Dataset
        Dataset representing the grid, initialized with default_value.
    """
    if x0 is None or y0 is None:
        raise ValueError("Origin (x0, y0) must be provided.")

    if dx is None or dy is None:
        raise ValueError("Grid spacing (dx, dy) must be provided.")

    # Compute nx, ny if not provided
    if nx is None:
        if x1 is None:
            raise ValueError("Either nx or x1 must be provided.")
        nx = int(abs(x1 - x0) / dx)

    if ny is None:
        if y1 is None:
            raise ValueError("Either ny or y1 must be provided.")
        ny = int(abs(y1 - y0) / dy)

    # Generate coordinates (cell centers)
    # x0 + dx/2 + i*dx
    x_coords = x0 + dx/2 + np.arange(nx) * dx
    y_coords = y0 + dy/2 + np.arange(ny) * dy
    layer_coords = np.arange(1, nlayer + 1)

    # map coords to match zone dimensions
    x_coords = np.tile(x_coords, (nlayer * ny))
    # each y coords is repeated along xcoords (nx times), then results is tiled over layers
    y_coords = np.tile(np.repeat(y_coords[::-1], nx), nlayer)
    layer_coords = np.repeat(layer_coords, (ny * nx))

    # Create dataset
    # Dimensions: layer * y * x => gridmarthe convention = flatten array
    data = np.full((1, nlayer * ny * nx), default_value)  # (time, zone)

    _coords_attrs = _assign_xy_attrs(epsg)
    grid = xr.Dataset(
        data_vars={
            'permeab': (['time', 'zone'], data),
            'x': (['zone'], x_coords, _coords_attrs.get('x', {})),
            'y': (['zone'], y_coords, _coords_attrs.get('y', {})),
            'z': (['zone'], layer_coords, _assign_z_attrs()),
            'dx': (['zone'], np.repeat(dx, nx * ny * nlayer)),
            'dy': (['zone'], np.repeat(dy, nx * ny * nlayer))
        },
        coords={
            'zone': np.arange(1, np.size(data) + 1),
            'time': np.array([0.]),  #datetime(1850,1,1)
        },
        attrs=_parse_global_attrs(
            '', [[nx, ny, nlayer]], 1, 0., False,
            dx, dy, x_coords, y_coords, epsg
        )
    )

    return grid


def create_grid_from_dataframe():
    # TODO create a grid from a dataframe of x,y coordinates, [z], variables
    # z would be the layer number, variables can be permeab, hsubs, topog, etc.
    # --> allow direct import of unstructured grids (?) - maybe not for 1st version
    raise NotImplementedError()


def create_grid_from_raster():
    # TODO create a grid from a list raster files
    # a list of raster with topo, hsubs_1, hsubs2, ... hsubs_n
    raise NotImplementedError()


def create_grid_from_shape(
    shp_path,
    dx,
    dy,
    nlayer=1,
    default_value=1.,
    epsg=None,
    active_only=True,
    zooms=None,
):
    """
    Create a Marthe grid domain from a polygon shapefile.

    The grid extent is derived from the shapefile bounding box.
    Defaultly activates only cells whose centers fall inside polygons.

    Parameters
    ----------
    shp_path : str
        Path to the shapefile.
    dx : float
        Cell size in X direction.
    dy : float
        Cell size in Y direction.
    nlayer : int, optional
        Number of layers, by default 1.
    default_value : float, optional
        Default permeability value for the grid cells, by default 1.
    epsg : int, optional
        EPSG code of the coordinate reference system. If None, use shapefile CRS.
    active_only : bool, optional
        If True, only cells within the polygon are active, by default True.
    zooms : `list`, optional
        Placeholder for nested-grid support, by default None.
        **Future** (not yet implemented)

    Returns
    -------
    xarray.Dataset
        Dataset representing the grid, initialized with default_value.
    """

    # Load the shapefile
    gdf = gpd.read_file(shp_path)

    if gdf.empty:
        raise ValueError("Input shapefile is empty")

    if not gdf.geom_type.isin(["Polygon", "MultiPolygon"]).all():
        raise ValueError(
            "Input layer must contain Polygon/MultiPolygon geometries."
        )

    domain_geom = gdf.union_all()

    if epsg is None and gdf.crs is not None:
        try:
            epsg = gdf.crs.to_epsg()
        except Exception:
            epsg = None

    # Get the bounding box of the union domain
    x0, y0, x1, y1 = domain_geom.bounds

    grid = create_grid_domain(
        x0=x0,
        y0=y0,
        dx=dx,
        dy=dy,
        x1=x1,
        y1=y1,
        nlayer=nlayer,
        default_value=default_value,
        epsg=epsg
    )

    # Optionally set active domain inside polygon
    if active_only:
        inactive_code = 0 # for permeability
        points = shapely.points(grid["x"].values, grid["y"].values)
        inside = shapely.covers(domain_geom, points)
        grid['permeab'] = grid['permeab'].where(inside, inactive_code)

    return grid


def add_zoom(
    grid,
    x0_zoom,
    y0_zoom,
    xfactor,
    yfactor,
    x1_zoom,
    y1_zoom,
    default_value=1,
    mask_polygon=None,
    epsg=None
):
    """Add a zoom grid to an existing grid, given the zoom domain and zoom
    factors in x and y directions.

    Parameters
    ----------
    grid : xarray.Dataset
        The grid to which the zoom grid will be added.
        The grid must have the following variables: x, y, dx, dy
    x0_zoom : float
       x-coordinate of the lower left corner of the zoom domain
    y0_zoom : float
      y-coordinate of the lower left corner of the zoom domain
    xfactor : float
        zoom factor in the x direction
        xfactor = 1 means no zoom
        xfactor > 1 means zoom in the x direction
    yfactor : float
       zoom factor in the y direction
    x1_zoom : float
        x-coordinate of the upper right corner of the zoom domain
    y1_zoom : float
        y-coordinate of the upper right corner of the zoom domain
    default_value : float, optional
       default value for the zoom grid (e.g. 1e-6 for permeability).
       Default value is 1.
    mask_polygon : shapely.geometry.Polygon, optional
        Polygon to mask the zoom grid.
        Default value is None.
    epsg : int, optional
        EPSG code of the grid. Default is None.

    Returns
    -------
    grid : xarray.Dataset
        The grid with the zoom grid added.
    """
    # FIXME how to assert epsg ?
    inactive_code = 0  # for permeability in main grid
    inactive_subgrid = -9999.  # inactive subgrid (but active main grid)

    dims = _get_dims_from_attrs(grid.attrs.get('original_dimensions'))
    nlayer = dims[0][-1]
    nrow_main = dims[0][0]
    ncol_main = dims[0][1]

    nvals = ncol_main * nrow_main * nlayer
    xy_arr = np.array([grid['x'][:nvals].values, grid['y'][:nvals].values]).T
    main_points = shapely.points(xy_arr[:,0], xy_arr[:,1])

    if len(dims) > 1:
        # TODO: test that zoom does not overlap any previous zoom
        _has_existing_zoom = True
        nzoom = len(dims) - 1
        idx_zoom = np.prod(dims, axis=1)
        # check _filter_shallow_only: that was a similar pb
    else:
        _has_existing_zoom = False

    # regular main grid dx and dy
    dx = grid['dx'][:nvals].values[0]
    dy = grid['dy'][:nvals].values[0]

    # -- snap to main grid cells edges
    # get nearest main center cell
    idx_0, _ = _nearest_node((x0_zoom, y0_zoom), xy_arr)
    idx_1, _ = _nearest_node((x1_zoom, y1_zoom), xy_arr)

    (x0_zoom, y0_zoom), (x1_zoom, y1_zoom) = xy_arr[idx_0,:], xy_arr[idx_1, :]

    # compute cell edge for lower left and upper right corners
    x0_zoom += dx/2
    y0_zoom -= dy/2
    x1_zoom += dx/2
    y1_zoom -= dy/2

    x0, y0, x1, y1 = _get_extend_from_attrs(grid.attrs.get('extend'))

    if (
        x0_zoom < x0
        or x1_zoom > x1
        or y0_zoom < y0
        or y1_zoom > y1
    ):
        raise ValueError(
            "Snapped zoom grid exceeds main grid extent."
        )

    # create zoom grid with 1 halo main cell
    dx = dx / xfactor
    dy = dy / yfactor
    nx = int(abs(x1_zoom - x0_zoom) / dx)
    ny = int(abs(y1_zoom - y0_zoom) / dy)

    x_coords = x0_zoom + dx/2 + np.arange(nx) * dx
    y_coords = y0_zoom + dy/2 + np.arange(ny) * dy

    # add halo cell centers
    x_coords = np.concatenate([
            [x_coords[0] - dx * (xfactor+1) / 2], x_coords,
            [x_coords[-1] + dx * (xfactor+1) / 2]
    ])
    y_coords = np.concatenate([
            [y_coords[0] - dy * (xfactor+1) / 2], y_coords,
            [y_coords[-1] + dy * (xfactor+1) / 2]
    ])
    layer_coords = np.arange(1, nlayer + 1)

    # map coords to match zone dimensions
    # update nx ny
    nx = nx + 2 # halo cells
    ny = ny + 2 # halo cells
    x_coords = np.tile(x_coords, (nlayer * ny))
    y_coords = np.tile(np.repeat(y_coords[::-1], nx), nlayer)
    layer_coords = np.repeat(layer_coords, (ny * nx))

    # Create dataset
    # Dimensions: layer * y * x => gridmarthe convention = flatten array
    data = np.full((1, nlayer * ny * nx), default_value)  # (time, zone)

    _coords_attrs = _assign_xy_attrs(epsg)

    dx_data = np.concatenate([[dx*xfactor], np.repeat(dx, nx-2), [dx*xfactor]])
    dy_data = np.concatenate([[dy*yfactor], np.repeat(dy, ny-2), [dy*yfactor]])

    dx_data = np.tile(dx_data, (nlayer * ny))
    dy_data = np.tile(np.repeat(dy_data[::-1], nx), nlayer)

    zoom_grid = xr.Dataset(
        data_vars={
            'permeab': (['time', 'zone'], data),
            'x': (['zone'], x_coords, _coords_attrs.get('x', {})),
            'y': (['zone'], y_coords, _coords_attrs.get('y', {})),
            'z': (['zone'], layer_coords, _assign_z_attrs()),
            'dx': (['zone'], dx_data),
            'dy': (['zone'], dy_data)
        },
        coords={
            'zone': np.arange(1, np.size(data) + 1),
            'time': np.array([0.]),  #datetime(1850,1,1)
        },
        attrs=_parse_global_attrs(
            '', [[nx, ny, nlayer]], 1, 0., False,
            dx, dy, x_coords, y_coords, epsg
        )
    )

    zoom_points_with_halo = shapely.points(zoom_grid["x"].values,
                                           zoom_grid["y"].values)

    if mask_polygon is None:
        # all cells in zoom grid are active, set main grid cells to inactive if
        # their centers are inside the zoom domain
        zoom_coords = (
            (x0_zoom, y0_zoom),
            (x1_zoom, y0_zoom),
            (x1_zoom, y1_zoom),
            (x0_zoom, y1_zoom),
            (x0_zoom, y0_zoom)
        )
        zoom_polygon = Polygon(zoom_coords)
    else:
        zoom_polygon = mask_polygon

    # set main grid cells to inactive if their centers are inside the mask_polygon
    # and if nested is active
    inside = shapely.covers(zoom_polygon, main_points)
    grid['permeab'][0, :nvals] = np.where(inside, inactive_code, grid['permeab'][0, :nvals])

    # mask_polygon is provided, use it to set active/inactive cells in zoom grid
    # FIXME: get 0 from main grid inactive cells, and halo cells, otherwise set -9999.
    inside = shapely.covers(zoom_polygon, zoom_points_with_halo)
    zoom_grid['permeab'] = zoom_grid['permeab'].where(inside, inactive_code)

    nested_grid = xr.concat([grid, zoom_grid],dim="zone")
    nested_grid = nested_grid.assign_coords(zone=np.arange(1, nested_grid.sizes["zone"] + 1))

    # update dims
    zoom_dims = _get_dims_from_attrs(zoom_grid.attrs.get('original_dimensions'))
    dims.extend(zoom_dims)
    nested_grid.attrs['original_dimensions'] = (
        'x,y,z [grids]: ' + '; '.join(
            [' '.join(map(str, x)) for x in dims]
        )
    )
    nested_grid.attrs['nested_grid'] = True

    return nested_grid


def add_zoom_from_shape(grid, zooms, epsg=None):
    """Add a zoom grid from a shapefile defining the zoom domain, and zoom
    factors in x and y directions.  zooms is a list of dict with keys: shape,
    xfactor, yfactor, default_value (optional)

    >>> zooms = [
    ...     {
    ...         "shape": "river1_zone.shp",
    ...         "xfactor": 4,
    ...         "yfactor": 4,
    ...         "default_value": 1
    ...     },
    ...     {
    ...         "shape": "river2_zone.shp",
    ...         "xfactor": 5,
    ...         "yfactor": 5,
    ...         "default_value": 1
    ...     }
    ... ]
    """
    # FIXME assert non-intersection between zoom domains if multiple
    epsg = epsg if epsg is not None else grid.attrs.get('epsg')
    gdf_grid = to_geodataframe(grid)
    for zoom in zooms:
        gdf_zoom = gpd.read_file(zoom['shape'])
        # get cells intersecting zoom domain to ensure coherent snapping
        # after mask_polygon filter
        grid_geom_zoom = gdf_grid.geometry.intersects(gdf_zoom.unary_union)
        domain_geom_zoom = gdf_grid.iloc[grid_geom_zoom.values].union_all()
        x0_zoom, y0_zoom, x1_zoom, y1_zoom = domain_geom_zoom.bounds

        grid = add_zoom(
            grid,
            x0_zoom=x0_zoom,
            y0_zoom=y0_zoom,
            x1_zoom=x1_zoom,
            y1_zoom=y1_zoom,
            xfactor=zoom['xfactor'],
            yfactor=zoom['yfactor'],
            default_value=zoom.get('default_value', 1),
            mask_polygon=domain_geom_zoom,
            epsg=epsg
        )
    return grid
