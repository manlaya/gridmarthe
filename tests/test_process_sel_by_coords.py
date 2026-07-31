#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import xarray as xr
import pytest

import gridmarthe as gm


@pytest.fixture
def sample_dataset():
    ds = gm.load_marthe_grid(
        'tests/data/hallue.permh',
        drop_nan=True,
        xyfactor=1e3
    )
    return ds


@pytest.fixture
def sample_dataset_multilayer():
    ds = gm.load_marthe_grid(
        'tests/data/hallue_multilayer.permh',
        drop_nan=True,
        xyfactor=1e3
    )
    return ds


def test_x_range_selection(sample_dataset):
    xmin, xmax = 607.85*1e3, 610.95*1e3
    subset = gm.sel_by_coords(sample_dataset, x=(xmin, xmax))
    x_vals = subset['x'].values
    assert np.any((sample_dataset['x'] <= xmin) | (sample_dataset['x'] >= xmax))
    assert np.all((x_vals >= xmin) & (x_vals <= xmax))


def test_y_range_selection(sample_dataset):
    ymin, ymax = 2.56625e+06, 2.56675e+06
    subset = gm.sel_by_coords(sample_dataset, y=(ymin, ymax))
    y_vals = subset['y'].values
    assert np.all((y_vals >= ymin) & (y_vals <= ymax))


def test_z_selection(sample_dataset_multilayer):
    z_val = 3
    subset = gm.sel_by_coords(sample_dataset_multilayer, z=z_val)
    z_vals = subset['z'].values
    assert np.all(z_vals == z_val)


def test_z_range_selection(sample_dataset_multilayer):
    zmin, zmax = 2, 3
    subset = gm.sel_by_coords(sample_dataset_multilayer, z=(zmin, zmax))
    z_vals = subset['z'].values
    assert np.all((z_vals >= zmin) & (z_vals <= zmax))


def test_x_and_y_range(sample_dataset):
    x_range = (605250, 608250)
    y_range = (2554250, 2557250)
    subset = gm.sel_by_coords(sample_dataset, x=x_range, y=y_range)
    x_vals = subset['x'].values
    y_vals = subset['y'].values
    assert np.all((x_vals >= x_range[0]) & (x_vals <= x_range[1]))
    assert np.all((y_vals >= y_range[0]) & (y_vals <= y_range[1]))
    assert len(subset.zone) == 49


def test_point_selection_nearest(sample_dataset):
    target_x, target_y = 606398.6, 2543846.0
    subset = gm.sel_by_coords(sample_dataset, x=target_x, y=target_y, method='nearest', tolerance=500)
    assert len(subset.zone) == 1
    assert subset.zone == 2670
    # Check that at least one point is within tolerance
    x_vals = subset['x'].values
    y_vals = subset['y'].values
    distances = np.sqrt((x_vals - target_x)**2 + (y_vals - target_y)**2)
    assert np.any(distances <= 500)


def test_range_selection_nearest(sample_dataset):
    x_range = (605612.5, 606913.5)
    y_range = (2543214.9, 2544388.5)
    subset = gm.sel_by_coords(sample_dataset, x=x_range, y=y_range, method='nearest', tolerance=500)
    assert len(subset.zone) == 9


def test_x_range_only_nearest(sample_dataset):
    x_range = (605612.5, 606913.5)
    subset = gm.sel_by_coords(sample_dataset, x=x_range, method='nearest', tolerance=500)
    assert len(subset.zone) > 0
    x_vals = subset['x'].values
    assert np.all((x_vals >= x_range[0]) & (x_vals <= x_range[1]))


def test_y_range_only_nearest(sample_dataset):
    y_range = (2543214.9, 2544388.5)
    subset = gm.sel_by_coords(sample_dataset, y=y_range, method='nearest', tolerance=500)
    assert len(subset.zone) > 0
    y_vals = subset['y'].values
    assert np.all((y_vals >= y_range[0]) & (y_vals <= y_range[1]))


def test_x_range_y_scalar_nearest(sample_dataset):
    x_range = (605000, 607000)
    y_target = 2543800.0
    subset = gm.sel_by_coords(sample_dataset, x=x_range, y=y_target, method='nearest', tolerance=500)
    assert len(subset.zone) > 0
    x_vals = subset['x'].values
    y_vals = subset['y'].values
    assert np.all((x_vals >= x_range[0]) & (x_vals <= x_range[1]))
    assert np.any(np.isclose(y_vals, y_target, atol=500))


def test_x_scalar_y_range_nearest(sample_dataset):
    x_target = 606000.0
    y_range = (2543000, 2544000)
    subset = gm.sel_by_coords(sample_dataset, x=x_target, y=y_range, method='nearest', tolerance=500)
    assert len(subset.zone) > 0
    x_vals = subset['x'].values
    y_vals = subset['y'].values
    assert np.any(np.isclose(x_vals, x_target, atol=500))
    y_mid = (y_range[0] + y_range[1]) / 2
    assert np.all(np.abs(y_vals - y_mid) <= 1500)


def test_range_selection_nearest_out_of_tolerance(sample_dataset):
    """Far-away ranges should return empty when tolerance is tight."""
    x_range = (1e8, 1.1e8)
    y_range = (1e8, 1.1e8)
    subset = gm.sel_by_coords(sample_dataset, x=x_range, y=y_range, method='nearest', tolerance=10)
    assert len(subset.zone) == 0


def test_nearest_x_only_returns_all_y_for_nearest_x(sample_dataset):
    """When only x is given with method='nearest', return all points at nearest x."""
    target_x = 599250
    subset = gm.sel_by_coords(sample_dataset, x=target_x, method='nearest', tolerance=1e4)
    assert len(subset.zone) == 2
    # All returned points should have x very close to the nearest x value
    x_vals = subset['x'].values
    idx_nearest = np.argmin(np.abs(sample_dataset['x'].values - target_x))
    nearest_x = sample_dataset['x'].values[idx_nearest]
    assert np.all(np.abs(x_vals - nearest_x) < 1e-10)


def test_nearest_y_only_returns_all_x_for_nearest_y(sample_dataset):
    """When only y is given with method='nearest', return all points at nearest y."""
    target_y = 2543250
    subset = gm.sel_by_coords(sample_dataset, y=target_y, method='nearest', tolerance=1e4)
    assert len(subset.zone) == 5
    y_vals = subset['y'].values
    idx_nearest = np.argmin(np.abs(sample_dataset['y'].values - target_y))
    nearest_y = sample_dataset['y'].values[idx_nearest]
    assert np.all(np.abs(y_vals - nearest_y) < 1e-10)


def test_no_selection_returns_full(sample_dataset):
    subset = gm.sel_by_coords(sample_dataset)
    assert len(subset.zone) == len(sample_dataset.zone)


def test_empty_selection_returns_empty(sample_dataset):
    subset = gm.sel_by_coords(sample_dataset, x=(1e5, 2e5), y=(1e6, 1.5e6))  # Out of range
    assert len(subset.zone) == 0


def test_exact_match_close_to_data(sample_dataset_multilayer):
    # Pick an actual x,y from the dataset
    idx = 100
    # sample_dataset = sample_dataset()
    x0 = sample_dataset_multilayer['x'].values[idx]
    y0 = sample_dataset_multilayer['y'].values[idx]
    z0 = sample_dataset_multilayer['z'].values[idx]

    subset = gm.sel_by_coords(sample_dataset_multilayer, x=x0, y=y0, z=z0)

    # Should include the original point (floating point might prevent exact match)
    # So we use isclose
    x_vals = subset['x'].values
    y_vals = subset['y'].values
    z_vals = subset['z'].values

    assert np.any(np.isclose(x_vals, x0) & np.isclose(y_vals, y0) & (z_vals == z0))


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--no-cov"])
