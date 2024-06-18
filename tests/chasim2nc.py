#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import gridmarthe as gm

# needs, xarray, netcdf4, h5netcdf

def main(fchasim, fpastp, fnc):
    ds = gm.load_marthe_grid(fchasim, fpastp=fpastp, dropna=True, varname='CHARGE')
    encode = {'charge': {'zlib': True, 'complevel': 7}}
    ds.to_netcdf(fnc, engine='h5netcdf', encoding=encode)
    return 0
    
    
if __name__ == "__main__":
    
    import os, sys
    from pathlib import Path
    
    os.makedirs('nc', exist_ok=True)
    
    # chasim = sys.argv[1]
    # pastp = sys.argv[2]

    chasim='./data/chasim_hallue.out'
    pastp='./data/hallue.pastp'
    nc = Path('nc', os.path.basename(chasim.replace("out", "nc")))

    status = main(chasim, pastp, nc)
    sys.exit(status)
   
