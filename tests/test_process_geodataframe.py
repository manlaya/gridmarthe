#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gridmarthe as gm
import geopandas as gpd


def test_convert_gdf():
    permh = gm.load_marthe_grid('tests/data/hallue.permh', drop_nan=True)
    gdf = gm.to_geodataframe(permh)
    assert isinstance(gdf, gpd.GeoDataFrame)
    assert gdf.geometry.is_valid.all()
    assert len(gdf) == 927
    assert 'geometry' in list(gdf.columns)
    assert gdf.index.names == ('time', 'zone')


def test_convert_gdf_time_fmt():
    ds = gm.load_marthe_grid('tests/data/chasim_hallue.out', fpastp="tests/data/hallue.pastp", drop_nan=True)
    gdf = gm.to_geodataframe(ds, fmt='wide')
    assert isinstance(gdf, gpd.GeoDataFrame)
    assert gdf.geometry.is_valid.all()
    assert 'charge_19950731' in gdf.columns
    assert 'time' not in gdf.index.names
