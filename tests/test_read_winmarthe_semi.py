#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import gridmarthe as gm
from gridmarthe.core import _read_marthe_grid


def test_read_sem_from_winmarthe():
    sem_file = 'tests/data/thickness.sem'
    ds = gm.load_marthe_grid(sem_file)
    print('Test read sem from winmarthe success!')


def test_read_sem_shallow_only():
    xfile = 'tests/data/test_shallow.trc_r'
    res = _read_marthe_grid(xfile, varname='', shallow_only=True)
    ds = gm.load_marthe_grid(xfile, shallow_only=True)
    x=ds['variable'].data[0,:]
    assert len(x[x!=0]) > 0
    # xx = gm.assign_coords(ds)['variable']
    # xx = xx.where(xx > 0)
    # xx.isel(time=0).plot.pcolormesh()
    # from matplotlib import pyplot as plt
    # plt.show()


if __name__ == '__main__':

    # test_read_sem_from_winmarthe()
    test_read_sem_shallow_only()
