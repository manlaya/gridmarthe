#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import os, sys
from argparse import ArgumentParser
import gridmarthe as gm


# Usage: `ncmart PATH_CHASIM PATH_PASTP [-o output] [-v varname]` 

def parse_args():
    """ CLI program """
    parser = ArgumentParser(
        prog='ncmart',
        description="Convert a Marthe GridFile to netCDF format."
    )
    
    parser.add_argument('opt', metavar='chasim pastp', type=str, nargs='+', help='Paths to chasim and pastp files are expected')
    parser.add_argument('--output'  , '-o'  , type=str, default=None, help='Output filename. Default is input.nc')
    parser.add_argument('--variable', '-v'  , type=str, default=None, help='Variable to read, default is None; i.e variable will be parse from file and ONLY the first variable will be read.')
    parser.add_argument('--as2d', '-d', action="store_const", const=True, default=False, help='Store grid as 2D (or more), default is 1D for space dimension') #choices=('True','False'), dest='monnomdevariable'
    parser.add_argument('--xyfactor', '-x', type=float, default=1., help='Transformation factor for coordinates. Optionnal, default is 1 (no transformation).')
    args = parser.parse_args()
    
    if args.output is not None:
        dirout = os.path.dirname(args.output)
        if dirout != '':
            os.makedirs(dirout, exist_ok=True)
    else:
        fname, ext = os.path.splitext(args.opt[0])
        args.output = '{}.nc'.format(fname)
    
    if os.path.exists(args.output):
        os.remove(args.output)

    if args.variable is not None:
        args.variable = args.variable.upper()

    return args


def main():
    """
    Convert a Marthe Grid file to NetCDF format, using gridmarthe pymodule
    """
    args   = parse_args()
    fpastp = args.opt[1] if len(args.opt) > 1 else None
    
    ds = gm.load_marthe_grid(
        args.opt[0],
        fpastp=fpastp,
        drop_nan=True,
        varname=args.variable,
        xyfactor=args.xyfactor
    )

    if args.as2d:
        ds = gm.assign_coords(ds)

    encode = {
        x: {'zlib': True, 'complevel': 6} for x in ds.keys()
    }
    ds.to_netcdf(args.output, engine='h5netcdf', encoding=encode)
    return 0
    
    
if __name__ == "__main__":
    
    """
    Usage
        ncmart $CHASIM $FPASTP
    """
    status = main()
    sys.exit(status)
   
