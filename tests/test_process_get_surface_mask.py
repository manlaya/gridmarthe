#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
import gridmarthe as gm


def test_surf_mask(plot=False):
    
    grid = gm.load_marthe_grid('./tests/data/craie_npc_gig.permh', drop_nan=True)
    surf = gm.get_surface_layer(ds=grid)
    
    assert np.allclose(np.unique(surf.z.data), np.array([1, 2, 4, 5, 6, 8, 9])), \
    "Surface layer identification failed"
    
    surf2 = gm.get_surface_layer(ds=grid, aquif_layers=[6,8,9])
    assert np.allclose(np.unique(surf2.z.data), [6,8,9]), \
    "Surface layer identification with subset failed"
    
    if plot:
        # Plot with geopandas
        # gdf = gm.to_geodataframe(surf)
        # gm.plot_outcrop(gdf)
        # plt.show()     
        toto = gm.assign_coords(surf, add_lay=False)
        ## gm.plot_nested_grid(toto, var='z')
        gm.plot_outcrop(toto)
        plt.show()
        plt.close('all')
    
    print("========================")
    print('surface mask test passed')


if __name__ == "__main__":
    test_surf_mask()