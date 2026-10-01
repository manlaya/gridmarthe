#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later
#
#    This file is part of gridmarthe.
#
#    gridmarthe is a python library to manage grid files for
#    MARTHE hydrogeological computer code from French Geological Survey (BRGM).
#    Copyright (C) 2025  BRGM
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
from ._common import _copyleft


def parse_args():
    """ CLI program """
    parser = ArgumentParser(
        prog='martshp',
        formatter_class=RawDescriptionHelpFormatter,
        description="Convert a Marthe GridFile to shapefile format.",
        epilog=textwrap.dedent(_copyleft)
    )

    parser.add_argument(
        'opt',
        metavar='grid timesteps',
        type=str,
        nargs='*',
        help=(
            'Paths to marthe grid [and timesteps if result] files are expected.'
            'If input is already a netcdf file, this script allow the '
            'conversion to shapefile/gpkg.'
        )
    )
    parser.add_argument(
        '--output', '-o',
        type=str,
        default=None,
        help='Output filename. Default is input.nc'
    )
    parser.add_argument(
        '--varname', '-n',
        type=str,
        default=None,
        help='Variable (field) to read, default is None: i.e variable will be '
             'parsed from file and ONLY the first variable will be read. '
             'Pass \'all\' to get all variables.'
    )
    parser.add_argument(
        '--xyfactor', '-x',
        type=float,
        default=1.,
        help='Transformation factor for coordinates. Optional, '
             'default is 1 (no transformation).'
    )
    parser.add_argument(
        '--gpkg', '-g',
        action="store_const",
        const=True,
        default=False,
        help='Use GPKG format instead of shapefile'
    )
    parser.add_argument(
        '--mask', '-m',
        action="store_const",
        const=True,
        default=False,
        help='Only get a mask of active domain'
    )
    parser.add_argument(
        '--nan', '-N',
        type=float,
        default=None,
        help='Custom NaN value for output. Optional, default is infer from '
             'Marthe variable. Use -N -1 to deactivate NaN dropout.'
    )
    parser.add_argument(
        '--grid-id', '-k',
        action="store_const",
        const=True,
        default=False,
        help='add grid id, column and row ids to output'
    )
    parser.add_argument(
        '--epsg', '-e',
        type=int,
        default=27572,
        help='EPSG code for coordinates. Optional, default is set to 27572 '
             '(France legacy projection Lambert zone II/extension, EPSG:27572).'
    )

    parser.add_argument(
        '--version', '-v',
        action="store_const",
        const=True,
        default=False,
        help='Show version and exit'
    )
    parser.add_argument(
        '--wide_fmt', '-w',
        action="store_const",
        const=True,
        default=False,
        help='Use wide format (columns) for time'
    )
    parser.add_argument(
        '--debug', '-G',
        action="store_const",
        const=True,
        default=False,
        help='Debug mode, print options and exit'
    )

    args = parser.parse_args()

    if args.version:
        print('gridmarthe {}'.format(gm.__version__))
        print(_copyleft)
        sys.exit(0)

    if len(args.opt) == 0:
        print('martshp: no argument/option')
        parser.print_usage()  # less verbose than print_help
        print('use martshp -h for more help')
        sys.exit(1)

    fname, ext = os.path.splitext(args.opt[0])
    args.fname, args.ext = fname, ext
    if args.output is not None:
        dirout = os.path.dirname(args.output)
        if dirout != '':
            os.makedirs(dirout, exist_ok=True)
    else:
        args.output = '{}.shp'.format(fname)

    if args.gpkg:
        fname, ext = os.path.splitext(args.output)
        args.output = '{}.gpkg'.format(fname)

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

    if not args.ext.endswith('nc'):
        ds = gm.load_marthe_grid(
            args.opt[0],
            fpastp=fpastp,
            drop_nan=args.nan != -1,
            nan_value=args.nan,
            add_id_grid=args.grid_id,
            add_col_row=args.grid_id,
            varname=args.varname,
            xyfactor=args.xyfactor,
            epsg=args.epsg
        )
    else:
        ds = xr.open_dataset(args.opt[0])
        if args.xyfactor > 1:
            ds['x'].data *= args.xyfactor
            ds['y'].data *= args.xyfactor
            ds['dx'].data *= args.xyfactor
            ds['dy'].data *= args.xyfactor
            ds.attrs['scale_factor'] = args.xyfactor
            # TODO: reset epsg in attrs with pyproj

    if args.mask:
        mask = gm.get_active_mask(ds)
        mask.to_file(args.output)
        sys.exit(0)

    #ds = gm.assign_coords(ds)
    gdf = gm.to_geodataframe(ds, fmt='long' if not args.wide_fmt else 'wide')
    gdf.to_file(args.output)
    return 0


if __name__ == "__main__":

    status = main()
    sys.exit(status)
