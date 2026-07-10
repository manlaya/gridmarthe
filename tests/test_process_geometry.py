#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import gridmarthe as gm


# np.set_printoptions(threshold=np.inf)

def test_compute_geometry():

    model_name = 'hallue_multilayer'
    hsubs = gm.load_marthe_grid('./tests/data/{}.hsubs'.format(model_name))
    topo  = gm.load_marthe_grid('./tests/data/{}.topog'.format(model_name))
    permh = gm.load_marthe_grid('./tests/data/{}.permh'.format(model_name), varname='PERMEAB')

    mask = gm.get_active_mask(permh, as_array=True, only_mask=True)['zone'].data

    geom = gm.compute_geometry(topo, hsubs)  # ok
    geom_mask = gm.compute_geometry(topo, hsubs, mask)  # ok

    # add tests
    # pour ça il faut un vrai topo et hsubs, (réalisé avec Winmarthe)
    # puis lire le résultat et comparer aux résultats de compute_geometry
    true_depth = gm.load_marthe_grid('./tests/data/{}_depth.sem'.format(model_name), varname='TRAVA')
    true_thick = gm.load_marthe_grid('./tests/data/{}_thick.sem'.format(model_name), varname='TRAVA')

    assert np.allclose(
        geom['depth'].sel(zone=mask),
        true_depth['trava'].sel(zone=mask)
    ), "depth does not match"

    assert np.allclose(
        geom['thickness'].sel(zone=mask),
        true_thick['trava'].sel(zone=mask)
    ), "thickness does not match"

    assert np.isin(geom_mask.zone.data, mask).all(), "mask does not match"
    assert np.allclose(geom_mask['depth'].data, true_depth['trava'].sel(zone=mask))
    assert np.allclose(geom_mask['thickness'].data, true_thick['trava'].sel(zone=mask))

    print("test_compute_geometry passed")


if __name__ == "__main__":
    test_compute_geometry()
