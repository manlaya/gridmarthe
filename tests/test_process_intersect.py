#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import gridmarthe as gm


def _get_test_data():
    df = pd.DataFrame(
        {
            "x": [607616.6, 607.83e3],
            "y": [2553064.4, 2553.4e3],
            "value": [1, 3]
        }
    )
    ds = gm.load_marthe_grid('tests/data/hallue.permh', xyfactor=1e3, drop_nan=True)
    idx1 = gm.search_zone(ds, x=df['x'].values[0], y=df['y'].values[0])
    idx2 = gm.search_zone(ds, x=df['x'].values[1], y=df['y'].values[1])
    assert idx1.zone == idx2.zone
    return ds, df


def test_intersect_nearest():
    ds, df = _get_test_data()
    df_mean = gm.intersect_grid(ds, df, method='nearest', agg='mean')
    df_sum = gm.intersect_grid(ds, df, method='nearest', agg='sum')

    assert len(df_mean) == len(df_sum) == 1
    assert df_mean.values == 2
    assert df_sum.values == 4


def test_intersect_exact():
    ds, df = _get_test_data()
    df_mean = gm.intersect_grid(ds, df, method='exact', agg='mean')
    df_sum = gm.intersect_grid(ds, df, method='exact', agg='sum')

    assert len(df_mean) == len(df_sum) == 1
    assert df_mean.values == 2
    assert df_sum.values == 4


if __name__ == '__main__':
    test_intersect_nearest()
    test_intersect_exact()
