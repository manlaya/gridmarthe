#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import gridmarthe as gm


def _check_times(times, is_time=True):
    assert isinstance(times, pd.DataFrame)
    assert 'step' in times.columns
    assert 'time' in times.columns
    assert times['step'].dtype == 'int64'
    if is_time:
        # pandas 3.0 : datetime64[ns] -> <M8[ns]
        # assert times['time'].dtype in ['datetime64[ns]', '<M8[us]']
        assert np.issubdtype(times['time'].dtype, np.datetime64)


def test_read_times():
    times = gm.read_dates_from_pastp('tests/data/hallue.pastp')
    _check_times(times)
    assert times['time'].iloc[0] == pd.Timestamp('1995-07-31 00:00:00')
    assert times['time'].iloc[-1] == pd.Timestamp('2012-07-31 00:00:00')


def test_read_times_messy_debug():
    times = gm.read_dates_from_pastp('tests/data/MOD82_Surfex_BV_Ext.pastp')
    _check_times(times)
    assert times['time'].iloc[0] == pd.Timestamp('1995-07-31 00:00:00')
    assert times['time'].iloc[-1] == pd.Timestamp('2025-07-31 00:00:00')


def test_read_times_int_fmt():
    times = gm.read_dates_from_pastp('tests/data/albien.pastp')
    _check_times(times, is_time=False)
    assert np.issubdtype(times['time'].dtype, np.integer)


if __name__ == "__main__":
    test_read_times()
    test_read_times_messy_debug()
    test_read_times_int_fmt()
