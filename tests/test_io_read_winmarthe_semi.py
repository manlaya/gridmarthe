#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path

import pytest
import numpy as np

import gridmarthe as gm
from gridmarthe.core import _read_marthe_grid


def test_read_sem_from_winmarthe():
    sem_file = 'tests/data/thickness.sem'
    ds = gm.load_marthe_grid(sem_file)
    assert 'trava' in ds.data_vars
    assert np.size(ds.trava) == 1058832


@pytest.mark.filterwarnings("ignore:No variable name found.")
def test_read_sem_shallow_only():
    xfile = 'tests/data/test_shallow.trc_r'
    ext = Path(xfile).suffix.strip('.')
    # res = _read_marthe_grid(xfile, varname='', shallow_only=True)
    ds = gm.load_marthe_grid(xfile, shallow_only=True)
    x = ds['trc_r'].data[0,:]
    assert len(x[x!=0]) > 0
    assert np.size(x) == 2862
    assert ext in ds.data_vars


if __name__ == '__main__':

    test_read_sem_from_winmarthe()
    test_read_sem_shallow_only()
