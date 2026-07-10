#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import gridmarthe as gm


PATH_DATA = './tests/data'


def test_corresponding_zone_dropna():
    
    # load the grid and the mask to extract values on zones
    permh  = gm.load_marthe_grid(f'{PATH_DATA}/craie_npc_nogig.permh', drop_nan=True)
    mask   = permh.zone.data
    h_subs = gm.load_marthe_grid(f'{PATH_DATA}/craie_npc.hsubs').sel(zone=mask)

    if gm.__version__ == '0.1.2':
        surf = gm.get_min_layer(h_subs)
    else:
        surf = gm.get_surface_layer(h_subs)

    df1 = permh.to_dataframe().reset_index().round({'x': 2, 'y': 2})
    df2 = surf.to_dataframe().reset_index().round({'x': 2, 'y': 2})
    df = df1.merge(
        df2, on=['x', 'y'], suffixes=['','_r'],
        how='left'
    ) # merge return NaNs in df with gridmarthe 0.1.3 !
    # because `zone` index is not the same in permh and h_subs
    # in v0.1.3 the zone index is reset from 1 to n_zone if drop_nan is True
    # use this test to avoid such modifications and more hours lost in debugging

    np.allclose(df1.x.values, df.x.values)

    assert not np.all(np.isnan(df['h_substrat'].values)), "Join error, might come from dtype / round / Wrong merge field"
    print("=============================")
    print("corresponding_zone_dropna test passed")
    return


if __name__ == "__main__":
    
    test_corresponding_zone_dropna()
