#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# import os;os.chdir('tests')
import matplotlib.pyplot as plt

import gridmarthe as gm


grid = gm.load_marthe_grid('./tests/data/craie_npc.permh', drop_nan=True)
surf = gm.get_surface_layer(ds=grid)

# Plot with geopandas
gdf = gm.to_geodataframe(surf)
gm.plot_outcrop(gdf, engine='gpd')
plt.show()

# Plot with xarray
toto = gm.assign_coords(surf, add_lay=False)
# gm.plot_nested_grid(toto, var='z')
gm.plot_outcrop(toto)
plt.show()
# plt.close('all')