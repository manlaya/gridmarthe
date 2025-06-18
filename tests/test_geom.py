#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gridmarthe as gm

# np.set_printoptions(threshold=np.inf)

model_name = 'craie_npc'
hsubs = gm.load_marthe_grid('./tests/data/{}.hsubs'.format(model_name))
topo  = gm.load_marthe_grid('./tests/data/{}.topog'.format(model_name))
permh = gm.load_marthe_grid('./tests/data/{}_nogig.permh'.format(model_name), varname='PERMEAB')
mask = gm.get_active_mask(permh, as_array=True)['zone'].data

geom = gm.compute_geometry(topo, hsubs, mask)  # ok
geom = gm.compute_geometry(topo, hsubs)  # ok

