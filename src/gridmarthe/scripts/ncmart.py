#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later
#
#    This file is part of gridmarthe.
#
#    gridmarthe is a python library to manage grid files for
#    MARTHE hydrogeological computer code from French Geological Survey (BRGM).
#    Copyright (C) 2024  BRGM
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
import os, sys, textwrap
from argparse import ArgumentParser, RawDescriptionHelpFormatter

import xarray as xr

import gridmarthe as gm
from gridmarthe.__version__ import _copyleft


# Usage: `ncmart PATH_CHASIM PATH_PASTP [-o output] [-v varname]`
def parse_args():
    """ CLI program """
    parser = ArgumentParser(
        prog='ncmart',
        # usage='%(prog)s [options]',
        formatter_class=RawDescriptionHelpFormatter,
        description="Convert a Marthe grid file to netCDF format.",
        epilog=textwrap.dedent(_copyleft)
    )

    # TODO split `dump` into subcommand ?
    # https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser.add_subparsers
    # subparsers = parser.add_subparsers(help='subcommand help')
    # parser_a = subparsers.add_parser('a', help='a help')
    # parser_a.add_argument('bar', type=int, help='bar help')

    # option 0 or two: gridfile, timestep
    parser.add_argument(
        'opt',
        metavar='grid [timesteps]',
        type=str,
        nargs='*',# nargs='+'
        help=(
            'Paths to marthe grid and, optionally, timesteps files. '
            'If gridfile is already a netCDF file, ncmart allows you to modify '
            'it (with xyfactor, attrs, etc.).'
        )
    )
    parser.add_argument('--output'  , '-o', type=str, default=None, help='Output filename. Default is input.nc')
    parser.add_argument('--varname' , '-n', type=str, default=None, help='Variable Name (field) to read, default is None: i.e variable will be parsed from file and ONLY the first variable will be read. Pass \'all\' to get all variables.')
    parser.add_argument('--as2d'    , '-d', action="store_const", const=True, default=False, help='Store grid as 2D (or more), default is 1D for space dimension, ie reduced horizontal grid') #choices=('True','False'), dest='monnomdevariable'
    parser.add_argument('--xyfactor', '-x', type=float, default=1., help='Transformation factor for coordinates. Optional, default is 1 (no transformation).')
    parser.add_argument('--dump'    , '-H', action="store_const", const=True, default=False, help='Dump variables names, like ncdump -h FILE.')
    parser.add_argument('--attrs'   , '-a', type=str, default=None, help='Add global attributes. Comma separated for multiple attrs, = is the separator for key, value. Example: `-a "references=RP-XXXXX-FR,toto=tata"`')
    parser.add_argument('--version' , '-v', action="store_const", const=True, default=False, help='Show version and exit')

    args = parser.parse_args()

    if args.version:
        print('gridmarthe {}'.format(gm.__version__))
        print(_copyleft)
        sys.exit(0)

    if len(args.opt) == 0:
        print('ncmart: no argument/option')
        parser.print_usage()  # less verbose than print_help
        print('use ncmart -h for more help')
        sys.exit(1)

    fname, ext = os.path.splitext(args.opt[0])
    args.fname, args.ext = fname, ext

    if args.output is not None:
        dirout = os.path.dirname(args.output)
        if dirout != '':
            os.makedirs(dirout, exist_ok=True)
    else:
        args.output = '{}.nc'.format(fname)

    if os.path.exists(args.output):
        os.remove(args.output)

    if args.varname is not None:
        args.varname = args.varname.upper()

    return args


def main():
    """
    Convert a Marthe Grid file to NetCDF format, using gridmarthe pymodule
    """
    args   = parse_args()
    fpastp = args.opt[1] if len(args.opt) > 1 else None

    if args.dump:
        _var = gm.scan_var(args.opt[0])
        print('Variable found in file:', _var)
        sys.exit(0)

    if not args.ext.endswith('nc'):
        ds = gm.load_marthe_grid(
            args.opt[0],
            fpastp=fpastp,
            drop_nan=True,
            varname=args.varname,
            xyfactor=args.xyfactor
        )
    else:
        # allow transformation of existing netcdf
        ds = xr.open_dataset(args.opt[0])
        if args.xyfactor > 1:
            ds['x'].data *= args.xyfactor
            ds['y'].data *= args.xyfactor
            ds['dx'].data *= args.xyfactor
            ds['dy'].data *= args.xyfactor
            ds.attrs['scale_factor'] = args.xyfactor

    if args.as2d:
        ds = gm.assign_coords(ds)
        # ds = ds.isel(Y=slice(None, None, -1))  # inverse Y-axis, eg for QGIS view

    # add user attrs
    if args.attrs is not None:
        _attrs = args.attrs.split(',')
        _attrs = [x.split('=') for x in _attrs]
        _attrs = {k.strip(): v.strip() for k, v in _attrs}
        ds.attrs = {**ds.attrs, **_attrs}

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

