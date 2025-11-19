#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
from matplotlib import pyplot as plt, colors, cm
from mpl_toolkits.axes_grid1 import make_axes_locatable

import gridmarthe as gm


def test_cross_section():
    permh = gm.load_marthe_grid('tests/data/craie_npc_nogig.permh', drop_nan=True)
    topo  = gm.load_marthe_grid('tests/data/craie_npc.topog', varname='H_TOPOGR')
    hsub  = gm.load_marthe_grid('tests/data/craie_npc.hsubs', varname='H_SUBSTRAT')
    gwl   = gm.load_marthe_grid('tests/data/chasim_npc.out', varname='CHARGE', drop_nan=True)  # groundwater level

    geom = gm.compute_geometry(topo, hsub, permh.zone)
    geom['charge'] = (('time', 'zone'), gwl['charge'].data)  # add gwl to new dataset with geom

    ds = gm.assign_coords(geom)

    XC = 6.116e5
    ds_xs = gm.slice_cross_section(ds, x=XC)  # here we define a cross section along y axis (x is constant)
    print(ds_xs)

    assert 'y' in ds_xs.dims, "Cross-section should have 'y' dimension"
    assert 'x' not in ds_xs.dims, "Cross-section should not have 'x' dimension"
    assert ds_xs.sizes['y'] > 1  # cross-section has multiple points
    assert ds_xs.sizes['z'] == 10  # we have 10 layers
    


# Visual test - disable for automated testing
def _check_plot_cross_section():
    permh = gm.load_marthe_grid('docs/source/user_guide/example/data/craie_npc.permh', drop_nan=True)
    topo  = gm.load_marthe_grid('docs/source/user_guide/example/data/craie_npc.topog', varname='H_TOPOGR')
    hsub  = gm.load_marthe_grid('docs/source/user_guide/example/data/craie_npc.hsubs', varname='H_SUBSTRAT')
    gwl   = gm.load_marthe_grid('docs/source/user_guide/example/data/chasim_npc.out', varname='CHARGE', drop_nan=True)  # groundwater level

    geom = gm.compute_geometry(topo, hsub, permh.zone)
    geom['charge'] = (('time', 'zone'), gwl['charge'].data)  # add gwl to new dataset with geom

    ds = gm.assign_coords(geom)

    XC = 6.116e5
    ds_xs = gm.slice_cross_section(ds, x=XC)  # here we define a cross section along y axis (x is constant)
    print(ds_xs)
    # We can plot this with the helpful function
    # prep data
    line = ds_xs['charge'].isel(time=-1).sel(z=6).to_dataframe().reset_index()
    surf = gm.get_surface_layer(gwl)

    # prep colormap
    colours = ['slategrey', 'burlywood', 'red', 'yellow', 'orange', 'lightgreen', 'lightgrey', 'steelblue', 'darkgreen', 'brown']
    bounds = np.arange(1, len(colours)+2)  # add a fictive layer at the end because this is lower bounds
    labels = ['Alluv.', 'Limons', 'Fland', 'Land', 'Than', 'Craie', 'No prod.', 'Tur', 'Ceno', 'Carbo']

    cmap = colors.ListedColormap(colours)
    norm = colors.BoundaryNorm(bounds, cmap.N)

    # CREATE AXES
    fig, axes = plt.subplots(ncols=2, figsize=(14,4), width_ratios=[0.5, 0.6])

    # MAP
    ax = axes[0]
    gm.plot_outcrop(
        gm.assign_coords(surf, add_lay=False),
        fig=fig, ax=ax, cmap=cmap, norm=norm, labels=labels, cbar_width=4,
        alpha=0.7
    )
    ax.axvline(x=XC, color='k', label='cross_section')

    # CROSS-SECT
    ax = axes[1]
    gm.plot_cross_section(ds_xs, fig=fig, ax=ax, cmap=cmap, norm=norm, labels=labels)
    line.plot(y="charge", x='y', ax=ax, color='blue', linewidth=0.7, alpha=0.6)  # gwl line
    ax.set_xlim(2.5692e6)

    plt.tight_layout()
    plt.show()
