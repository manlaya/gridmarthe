#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import gridmarthe as gm


def test_read_veloc_from_marthe():
    data_path = 'tests/data/veloci.out'
    ds = gm.read_velocity(data_path)
    assert 'vx' in ds.data_vars, 'Vx variable not found'
    assert 'vy' in ds.data_vars, 'Vy variable not found'
    assert 'vz' in ds.data_vars, 'Vz variable not found'
    assert ds.vx.shape == ds.vy.shape == ds.vz.shape, 'wrong shape for velocity components'
    assert 'vmod' in ds.data_vars, 'Vmod variable not found'
    vmod_calculated = (ds.vx**2 + ds.vy**2 + ds.vz**2)**0.5
    assert np.allclose(ds.vmod, vmod_calculated, atol=1e-8), 'Vmod values incorrect'
    print('Test read veloc from marthe success!')


if __name__ == '__main__':
    test_read_veloc_from_marthe()
