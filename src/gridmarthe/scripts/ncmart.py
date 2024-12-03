#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import os, sys
from argparse import ArgumentParser
import gridmarthe as gm


def parse_args():
    parser = ArgumentParser(
        prog='ncmart',
        description="""Convert a Marthe GridFile to netCDF format.
Usage: `chasim2nc PATH_CHASIM PATH_PASTP [-o output] [-v varname]
"""
    )
    parser.add_argument('opt', metavar='chasim pastp', type=str, nargs='+', help='Paths to chasim and pastp files are expected')
    parser.add_argument('--output'  , '-o'  , type=str, default=None, help='output filename. Default is input.nc')
    parser.add_argument('--variable', '-v'  , type=str, default='CHARGE', help='variable to read, default is CHARGE')
    args = parser.parse_args()
    if args.output is not None:
        dirout = os.path.dirname(args.output)
        if dirout != '':
            os.makedirs(dirout, exist_ok=True)
    else:
        args.output = args.opt[0].replace('out', 'nc')
    return args


def main():
    """
    Convert a Marthe Grid file to NetCDF format, using gridmarthe pymodule
    """
    args   = parse_args()
    ds     = gm.load_marthe_grid(args.opt[0], fpastp=args.opt[1], drop_nan=True, varname=args.variable)
    encode = {'charge': {'zlib': True, 'complevel': 6}}
    ds.to_netcdf(args.output, engine='h5netcdf', encoding=encode)
    return 0
    
    
if __name__ == "__main__":
    
    """
    Usage
        ncmart $CHASIM $FPASTP
    """
    status = main()
    sys.exit(status)
   
