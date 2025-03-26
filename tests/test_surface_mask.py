#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# import modules
import gridmarthe as gm
import matplotlib.pyplot as plt


import os;os.chdir('tests')


grid = gm.load_marthe_grid('./data/craie_npc.permh', drop_nan=True)
surf = gm.get_surface_layer(ds=grid)
gdf = gm.to_geodataframe(surf)
gm.plot_outcrop(gdf, engine='gpd')
plt.show()

toto = gm.assign_coords(surf, add_lay=False)
# gm.plot_nested_grid(toto, var='z')
gm.plot_outcrop(toto)
plt.show()


# from matplotlib import pyplot as plt
# from mpl_toolkits.axes_grid1 import make_axes_locatable
# from matplotlib import (colors, cm)

# import numpy as np
# import xarray as xr
# import geopandas as gpd

# ds_outcrop=toto.copy()
# ds_outcrop['z'] = ds_outcrop['z']
# assert 'z' in ds_outcrop.keys(), "No `z` dimension. Outcrop plot is not possible."
# maxn = np.nanmax(ds_outcrop['z'].data)

# # custom cbar to force categories
# cmap = cm.tab10 if maxn <= 10 else cm.tab20
# cmap = colors.ListedColormap(cmap.colors[:int(maxn)]) # subset on number of colors, if not wrong legend
# bounds = np.arange(1, maxn+1)
# if len(bounds) == 1:
#     bounds = np.append(bounds, [maxn+1])
# norm = colors.BoundaryNorm(bounds, cmap.N+1,)  # set bins to custom values
# cbar = plt.cm.ScalarMappable(norm=norm, cmap=cmap)

# fig, ax = plt.subplots(1, 1)
# divider = make_axes_locatable(ax)
# cax = divider.append_axes("right", size="5%", pad=0.1)

# # the_plot = ds_outcrop['z'].plot.pcolormesh(
# the_plot = gm.plot_nested_grid(
#     # x='x', y='y',
#     ds_outcrop, var='z',
#     ax=ax,
#     cmap=cmap,
#     levels=bounds,
#     # add_colorbar=False,
# )

# ax_cbar = fig.colorbar(
#     cbar, ax=ax, cax=cax,
#     orientation='vertical',
#     ticks=[x+0.5 for x in bounds], # set labels in the middle of class
#     label='Layers',
# )
# ax_cbar.ax.tick_params(size=0)
# ax_cbar.set_ticklabels(ax_cbar.set_ticklabels(['{:.0f}'.format(x) for x in bounds]))
# plt.show()