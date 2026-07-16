# -*- coding: utf-8 -*-

import numpy as np
import xarray as xr
import geopandas as gpd  # ruff:ignore[banned-import-alias]
from shapely.geometry import Point
from scipy.spatial import cKDTree

from .gis import to_geodataframe


def intersect_grid(ds, df, method='nearest', agg='mean', value='value', epsg='EPSG:27572'):
    """Intersect a dataframe with grid

    This function map the grid indices to the dataframe coordinates
    and allow to regroup data by grid cell.

    Parameters
    ----------
    ds : xarray.Dataset
       Grid dataset. Must have x and y coordinates.
       Must have a cell index variable named 'zone'
    df : pandas.DataFrame
        Dataframe to intersect with grid. Must have x and y columns
    method : str, optional
        Method to use for intersection. By default, the nearest cell is used.
        If method = 'exact', then a conversion of the grid to polygons is done
        and the intersection is performed. This is slower but more accurate.
        If method = 'nearest', then the nearest cell is used. This is faster
        but can lead to less accurate results if resolution within grid vary.
    agg : str, optional
        Aggregation method to use for data regrouped by grid cell. By default,
        the mean is used.
    value: str, optional
        Name of the variable to aggregate in `df` (name of the column). By
        default 'value'.
    epsg : str or int, optional
        Projection to use for the grid and the dataframe. By default, the
        projection used is 'EPSG:27572' (Lambert 2Etendu).

    Returns
    -------
    xarray.Dataset
     Dataset with the same structure as the input grid
     but with the data from the dataframe.
    """
    if method == 'exact':

        cells_gdf = to_geodataframe(ds, epsg=epsg).reset_index()
        pts_gdf = gpd.GeoDataFrame(
            df, geometry=[Point(xy) for xy in zip(df.x, df.y)],
            crs=epsg,
        )
        joined = gpd.sjoin(
            pts_gdf,
            cells_gdf[["zone", "geometry"]],
            predicate="within",
        )

        return joined.groupby("zone")[value].agg(agg)

    elif method == 'nearest':
        # use Rtree ?
        grid_xy = np.column_stack([ds.x.values, ds.y.values])
        tree = cKDTree(grid_xy)
        pts_xy = df[["x", "y"]].values
        _, idx = tree.query(pts_xy)
        df["zone"] = ds.zone.values[idx]

        return df.groupby("zone")[value].agg(agg)

    else:
        raise ValueError(f"Unknown method {method}")
