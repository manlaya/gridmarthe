#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gridmarthe as gm

# np.set_printoptions(threshold=np.inf)

model_name = 'craie_npc'
hsubs = gm.load_marthe_grid('../../mart_cabbalr_no_lay2_new_topo/{}.hsubs'.format(model_name))
topo  = gm.load_marthe_grid('../../mart_cabbalr_no_lay2_new_topo/{}.topog'.format(model_name))
permh = gm.load_marthe_grid('../../mart_cabbalr_no_lay2_new_topo/{}.permh'.format(model_name), varname='PERMEAB')
mask = gm.get_mask_array(permh)['zone'].data

geom = gm.compute_geometry(topo, hsubs, mask)
geom = gm.compute_geometry(topo, hsubs)


