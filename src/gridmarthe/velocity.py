#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
from io import StringIO
import numpy as np
import pandas as pd


def read_velocity(fveloc):
    """ Read and parse the velocity file output of MARTHE `veloci.out`

    Parameters
    ----------
    fveloc : str, Path
        path to file
    
    Returns
    -------
    xr.Dataset
    """

    with open(fveloc, 'r', encoding='ISO-8859-1') as f:
        content = f.read()

    times = re.findall(r'Step=\s*(?P<step>\d+)\s*;\s*Date=\s*(?P<date>[+-]?\d+(?:\.\d+)?)', content)
    times = [(int(step), float(date)) for step, date in times]  # convert str to int/float
    grids = re.split(r'^.*Step=\s*\d+\s*;\s*Date=\s*\d+.*$', content, flags=re.MULTILINE)[1:]

    res = []
    coords = []
    for i, grid in enumerate(grids):
        # exemple line in a grid: (x,y,z)(Vx,Vy,Vz,Module m.s-1)
        #     9.500000E+02   3.250000E+03   1.690750E+02  0.000E+00 -8.255E-04  0.000E+00 M=  8.255E-04 #,Z,Y,X=    0    1    1   10
        df = pd.read_csv(
            StringIO(grid),
            sep=r'\s+',
            skiprows=1,  # cause title/headers still here
            header=None,
            names=['x', 'y', 'z', 'vx', 'vy', 'vz', 'M_dummy', 'vmod', 'xyz_dummy', 'igrid', 'lay', 'row', 'col'],
            dtype={'x': float, 'y': float, 'z': float, 'vx': float, 'vy': float, 'vz': float,}
        )
        df = df.drop(columns=['M_dummy', 'xyz_dummy'])
        
        df['istep'] = times[i][0]
        df['zone'] = np.arange(1, len(df) + 1)
        
        if i == 0:
            # get coordinates only at first timestep
            coords.append(df[['zone', 'x', 'y', 'z', 'igrid', 'lay', 'row', 'col']].set_index('zone'))
        
        df = df.drop(columns=['x', 'y', 'z', 'igrid', 'lay', 'row', 'col'])
        res.append(df.set_index(['istep', 'zone']))
    
    res = pd.concat(res)
    coords = pd.concat(coords)
    res = res.to_xarray().merge(coords.to_xarray())
    res = res.assign_coords(time=('istep', np.array([x[1] for x in times])))
    return res
