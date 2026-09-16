#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import tempfile

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for testing
import matplotlib.pyplot as plt

import numpy as np
import gridmarthe as gm
from gridmarthe.plot import plot_mesh_time_serie


DATA_PATH = './tests/data'
PATH_TMP_OUTPUTS = './tests/tmp_outputs'


# Helper to close all figures after each test
def cleanup_plots():
    """Close all matplotlib figures to prevent memory leaks"""
    plt.close('all')


# --- Tests for plot_nested_grid ---

def test_plot_nested_grid_basic():
    """Test that plot_nested_grid runs and returns an axis"""
    permh_file = f'{DATA_PATH}/Somme_V3_Surfex.permh'
    ds = gm.load_marthe_grid(permh_file, varname='PERMEAB', drop_nan=True)
    ds = gm.assign_coords(ds)
    
    # Need to select time and layer for datasets with those dimensions
    if 'time' in ds.dims:
        ds = ds.isel(time=0)
    if 'z' in ds.dims:
        ds = ds.isel(z=0)
    
    ax = gm.plot_nested_grid(ds)
    assert ax is not None, 'Should return a matplotlib axis'
    assert isinstance(ax, plt.Axes), 'Should return a matplotlib Axes object'
    cleanup_plots()


def test_plot_nested_grid_with_varname():
    """Test plot_nested_grid with specific varname"""
    permh_file = f'{DATA_PATH}/Somme_V3_Surfex.permh'
    ds = gm.load_marthe_grid(permh_file, varname='PERMEAB', drop_nan=True)
    ds = gm.assign_coords(ds)
    
    if 'time' in ds.dims:
        ds = ds.isel(time=0)
    if 'z' in ds.dims:
        ds = ds.isel(z=0)
    
    ax = gm.plot_nested_grid(ds, varname='permeab')
    assert ax is not None, 'Should return a matplotlib axis'
    cleanup_plots()


def test_plot_nested_grid_with_ax():
    """Test plot_nested_grid with provided axis"""
    permh_file = f'{DATA_PATH}/Somme_V3_Surfex.permh'
    ds = gm.load_marthe_grid(permh_file, varname='PERMEAB', drop_nan=True)
    ds = gm.assign_coords(ds)
    
    if 'time' in ds.dims:
        ds = ds.isel(time=0)
    if 'z' in ds.dims:
        ds = ds.isel(z=0)
    
    fig, ax = plt.subplots()
    returned_ax = gm.plot_nested_grid(ds, ax=ax)
    assert returned_ax is ax, 'Should return the same axis that was provided'
    cleanup_plots()


def test_plot_nested_grid_save_to_file():
    """Test that plot_nested_grid can save to file"""
    permh_file = f'{DATA_PATH}/Somme_V3_Surfex.permh'
    ds = gm.load_marthe_grid(permh_file, varname='PERMEAB', drop_nan=True)
    ds = gm.assign_coords(ds)
    
    if 'time' in ds.dims:
        ds = ds.isel(time=0)
    if 'z' in ds.dims:
        ds = ds.isel(z=0)
    
    with tempfile.TemporaryDirectory(dir=PATH_TMP_OUTPUTS) as tmpdir:
        fig, ax = plt.subplots()
        gm.plot_nested_grid(ds, ax=ax)
        output_file = os.path.join(tmpdir, 'test_nested_grid.png')
        fig.savefig(output_file, dpi=100)
        cleanup_plots()
        
        assert os.path.exists(output_file), 'Plot file should be created'
        assert os.path.getsize(output_file) > 0, 'Plot file should not be empty'


# --- Tests for plot_outcrop ---

def test_plot_outcrop_basic():
    """Test that plot_outcrop runs with xarray Dataset"""
    permh_file = f'{DATA_PATH}/craie_npc_gig.permh'
    ds = gm.load_marthe_grid(permh_file, varname='PERMEAB', drop_nan=True)
    
    # Get surface layer for outcrop plot
    surf = gm.get_surface_layer(ds)
    surf = gm.assign_coords(surf, add_lay=False)
    
    fig, ax, cbar = gm.plot_outcrop(surf)
    assert fig is not None, 'Should return a figure'
    assert ax is not None, 'Should return an axis'
    assert cbar is not None, 'Should return a colorbar axis'
    cleanup_plots()


def test_plot_outcrop_save_to_file():
    """Test that plot_outcrop can save to file"""
    permh_file = f'{DATA_PATH}/craie_npc_gig.permh'
    ds = gm.load_marthe_grid(permh_file, varname='PERMEAB', drop_nan=True)
    surf = gm.get_surface_layer(ds)
    surf = gm.assign_coords(surf, add_lay=False)
    
    with tempfile.TemporaryDirectory(dir=PATH_TMP_OUTPUTS) as tmpdir:
        output_file = os.path.join(tmpdir, 'test_outcrop.png')
        gm.plot_outcrop(surf, file_out=output_file, show=False)
        cleanup_plots()
        
        assert os.path.exists(output_file), 'Plot file should be created'


# --- Tests for plot_cross_section ---

def test_plot_cross_section_basic():
    """Test that plot_cross_section runs and returns axes"""
    # Use hallue_multilayer which has a simpler structure
    permh_file = f'{DATA_PATH}/hallue_multilayer.permh'
    topo = gm.load_marthe_grid(f'{DATA_PATH}/hallue_multilayer.topog', varname='H_TOPOGR')
    hsub = gm.load_marthe_grid(f'{DATA_PATH}/hallue_multilayer.hsubs', varname='H_SUBSTRAT')
    
    # Create geometry
    permh = gm.load_marthe_grid(permh_file, varname='PERMEAB', drop_nan=True)
    geom = gm.compute_geometry(topo, hsub, permh.zone)
    ds = gm.assign_coords(geom)
    
    # Slice cross section at a y value
    if len(ds.y) > 0:
        yc = ds.y.values[len(ds.y) // 2]
        ds_xs = gm.slice_cross_section(ds, y=yc)
        
        # Provide custom cmap, norm, and labels to avoid colormap length issue
        from matplotlib import colors, cm
        n_layers = len(np.unique(ds_xs['z'].data))
        custom_cmap = colors.ListedColormap(cm.tab20.colors[:n_layers])
        bounds = np.arange(1, n_layers + 2)
        custom_norm = colors.BoundaryNorm(bounds, custom_cmap.N)
        
        ax, cax = gm.plot_cross_section(ds_xs, cmap=custom_cmap, norm=custom_norm)
        assert ax is not None, 'Should return an axis'
        assert cax is not None, 'Should return a colorbar axis'
        cleanup_plots()


def test_plot_cross_section_with_fig_ax():
    """Test plot_cross_section with provided figure and axis"""
    permh_file = f'{DATA_PATH}/hallue_multilayer.permh'
    topo = gm.load_marthe_grid(f'{DATA_PATH}/hallue_multilayer.topog', varname='H_TOPOGR')
    hsub = gm.load_marthe_grid(f'{DATA_PATH}/hallue_multilayer.hsubs', varname='H_SUBSTRAT')
    
    permh = gm.load_marthe_grid(permh_file, varname='PERMEAB', drop_nan=True)
    geom = gm.compute_geometry(topo, hsub, permh.zone)
    ds = gm.assign_coords(geom)
    
    if len(ds.y) > 0:
        yc = ds.y.values[len(ds.y) // 2]
        ds_xs = gm.slice_cross_section(ds, y=yc)
        
        from matplotlib import colors, cm
        n_layers = len(np.unique(ds_xs['z'].data))
        custom_cmap = colors.ListedColormap(cm.tab20.colors[:n_layers])
        bounds = np.arange(1, n_layers + 2)
        custom_norm = colors.BoundaryNorm(bounds, custom_cmap.N)
        
        fig, ax = plt.subplots()
        returned_ax, returned_cax = gm.plot_cross_section(
            ds_xs, fig=fig, ax=ax, cmap=custom_cmap, norm=custom_norm
        )
        assert returned_ax is ax, 'Should return the same axis'
        cleanup_plots()


# --- Tests for plot_mesh_time_serie ---

def test_plot_mesh_time_serie_basic():
    """Test that plot_mesh_time_serie runs and returns an axis"""
    out_file = f'{DATA_PATH}/chasim_hallue.out'
    ds = gm.load_marthe_grid(out_file, varname='CHARGE', drop_nan=True)
    # Don't assign coords - use the 1D zone dimension
    
    # Select a specific zone
    zone_id = ds.zone.values[0]
    ax = plot_mesh_time_serie(ds, zone=zone_id, show=False)
    assert ax is not None, 'Should return a matplotlib axis'
    cleanup_plots()


def test_plot_mesh_time_serie_multiple_datasets():
    """Test plot_mesh_time_serie with multiple datasets"""
    out_file = f'{DATA_PATH}/chasim_hallue.out'
    ds1 = gm.load_marthe_grid(out_file, varname='CHARGE', drop_nan=True)
    
    # Create a second dataset (same structure)
    ds2 = ds1.copy()
    
    zone_id = ds1.zone.values[0]
    ax = plot_mesh_time_serie(ds1, ds2, zone=zone_id, show=False)
    assert ax is not None, 'Should return a matplotlib axis'
    cleanup_plots()


def test_plot_mesh_time_serie_custom_varname():
    """Test plot_mesh_time_serie with custom varname"""
    out_file = f'{DATA_PATH}/chasim_hallue.out'
    ds = gm.load_marthe_grid(out_file, varname='CHARGE', drop_nan=True)
    
    zone_id = ds.zone.values[0]
    ax = plot_mesh_time_serie(ds, zone=zone_id, varname='charge', show=False)
    assert ax is not None, 'Should return a matplotlib axis'
    cleanup_plots()


# --- Tests for plot_veloc_quiver ---

def test_plot_veloc_quiver_basic():
    """Test that plot_veloc_quiver runs and returns an axis"""
    veloc_file = f'{DATA_PATH}/veloci.out'
    ds = gm.read_velocity(veloc_file)
    # Don't assign_coords - velocity data should keep zone dimension
    # and have x, y, z as coordinates
    
    ax = gm.plot_veloc_quiver(ds)
    assert ax is not None, 'Should return a matplotlib axis'
    cleanup_plots()


def test_plot_veloc_quiver_with_ax():
    """Test plot_veloc_quiver with provided axis"""
    veloc_file = f'{DATA_PATH}/veloci.out'
    ds = gm.read_velocity(veloc_file)
    
    fig, ax = plt.subplots()
    returned_ax = gm.plot_veloc_quiver(ds, ax=ax)
    assert returned_ax is ax, 'Should return the same axis'
    cleanup_plots()


def test_plot_veloc_quiver_options():
    """Test plot_veloc_quiver with various options"""
    veloc_file = f'{DATA_PATH}/veloci.out'
    ds = gm.read_velocity(veloc_file)
    
    # Test with different options
    ax = gm.plot_veloc_quiver(ds, xyfreq=2, color_mod=True)
    assert ax is not None, 'Should return a matplotlib axis'
    cleanup_plots()


def test_plot_veloc_quiver_save_to_file():
    """Test that plot_veloc_quiver can save to file"""
    veloc_file = f'{DATA_PATH}/veloci.out'
    ds = gm.read_velocity(veloc_file)
    
    with tempfile.TemporaryDirectory(dir=PATH_TMP_OUTPUTS) as tmpdir:
        fig, ax = plt.subplots()
        gm.plot_veloc_quiver(ds, ax=ax)
        output_file = os.path.join(tmpdir, 'test_veloc.png')
        fig.savefig(output_file, dpi=100)
        cleanup_plots()
        
        assert os.path.exists(output_file), 'Plot file should be created'


if __name__ == '__main__':
    # Run all tests
    test_plot_nested_grid_basic()
    test_plot_nested_grid_with_varname()
    test_plot_nested_grid_with_ax()
    test_plot_nested_grid_save_to_file()
    
    test_plot_outcrop_basic()
    test_plot_outcrop_save_to_file()
    
    test_plot_cross_section_basic()
    test_plot_cross_section_with_fig_ax()
    
    test_plot_mesh_time_serie_basic()
    test_plot_mesh_time_serie_multiple_datasets()
    test_plot_mesh_time_serie_custom_varname()
    
    test_plot_veloc_quiver_basic()
    test_plot_veloc_quiver_with_ax()
    test_plot_veloc_quiver_options()
    test_plot_veloc_quiver_save_to_file()
    
    print("All plot tests passed!")
