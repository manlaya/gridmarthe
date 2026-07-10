#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import xarray as xr
import pytest

import gridmarthe as gm


@pytest.fixture
def sample_dataset():
    """Create a sample flattened xarray Dataset for testing."""
    n = 1000
    zone = np.arange(1, n + 1)

    # Simulate grid-like x, y (irregular spacing for realism)
    x_vals = np.linspace(4.3e5, 8.1e5, n) + np.random.randn(n) * 1e3
    y_vals = np.linspace(2.2e6, 2.6e6, n) + np.random.randn(n) * 1e3
    z_vals = np.random.choice([1, 2, 3, 4, 5, 6], size=n)
    dx_vals = np.full(n, 2e3)
    dy_vals = np.full(n, 2e3)

    ds = xr.Dataset(
        data_vars={
            'z': ('zone', z_vals),
            'x': ('zone', x_vals),
            'y': ('zone', y_vals),
            'dx': ('zone', dx_vals),
            'dy': ('zone', dy_vals),
        },
        coords={'zone': ('zone', zone)}
    )
    return ds


def test_x_range_selection(sample_dataset):
    xmin, xmax = 5e5, 7e5
    subset = gm.sel_xy(sample_dataset, x=(xmin, xmax))
    x_vals = subset['x'].values
    assert np.all((x_vals >= xmin) & (x_vals <= xmax))


def test_y_range_selection(sample_dataset):
    ymin, ymax = 2.3e6, 2.5e6
    subset = gm.sel_xy(sample_dataset, y=(ymin, ymax))
    y_vals = subset['y'].values
    assert np.all((y_vals >= ymin) & (y_vals <= ymax))


def test_z_selection(sample_dataset):
    z_val = 3
    subset = gm.sel_xy(sample_dataset, z=z_val)
    z_vals = subset['z'].values
    assert np.all(z_vals == z_val)


def test_z_range_selection(sample_dataset):
    zmin, zmax = 2, 4
    subset = gm.sel_xy(sample_dataset, z=(zmin, zmax))
    z_vals = subset['z'].values
    assert np.all((z_vals >= zmin) & (z_vals <= zmax))


def test_x_and_y_range(sample_dataset):
    subset = gm.sel_xy(sample_dataset, x=(5e5, 6e5), y=(2.3e6, 2.4e6))
    x_vals = subset['x'].values
    y_vals = subset['y'].values
    assert np.all((x_vals >= 5e5) & (x_vals <= 6e5))
    assert np.all((y_vals >= 2.3e6) & (y_vals <= 2.4e6))


def test_point_selection_nearest(sample_dataset):
    target_x = 4.4e5
    target_y = 2.2e6
    # ds = sample_dataset()
    # subset = gm.sel_xy(ds, x=target_x, y=target_y, method='nearest', tolerance=1e4)
    subset = gm.sel_xy(sample_dataset, x=target_x, y=target_y, method='nearest', tolerance=1e4)
    assert len(subset.zone) > 0
    # Check that at least one point is within tolerance
    x_vals = subset['x'].values
    y_vals = subset['y'].values
    distances = np.sqrt((x_vals - target_x)**2 + (y_vals - target_y)**2)
    assert np.any(distances <= 1e4)


def test_no_selection_returns_full(sample_dataset):
    subset = gm.sel_xy(sample_dataset)
    assert len(subset.zone) == len(sample_dataset.zone)


def test_empty_selection_returns_empty(sample_dataset):
    subset = gm.sel_xy(sample_dataset, x=(1e5, 2e5), y=(1e6, 1.5e6))  # Out of range
    assert len(subset.zone) == 0


def test_exact_match_close_to_data(sample_dataset):
    # Pick an actual x,y from the dataset
    idx = 100
    # sample_dataset = sample_dataset()
    x0 = sample_dataset['x'].values[idx]
    y0 = sample_dataset['y'].values[idx]
    z0 = sample_dataset['z'].values[idx]

    subset = gm.sel_xy(sample_dataset, x=x0, y=y0, z=z0)

    # Should include the original point (floating point might prevent exact match)
    # So we use isclose
    x_vals = subset['x'].values
    y_vals = subset['y'].values
    z_vals = subset['z'].values

    assert np.any(np.isclose(x_vals, x0) & np.isclose(y_vals, y0) & (z_vals == z0))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
