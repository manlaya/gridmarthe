#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Tests for ncmart.py script using pytest and mock for CLI arguments.
"""

import os
import sys
from unittest.mock import patch, MagicMock, call
import pytest

from gridmarthe.scripts.ncmart import parse_args, main


def create_mock_args(**kwargs):
    """Create a MagicMock args object with default values that can be overridden."""
    defaults = {
        'opt': ['test_grid.chasim'],
        'fname': 'test_grid',
        'ext': '.chasim',
        'output': 'test_grid.nc',
        'varname': None,
        'nan': None,
        'grid_id': False,
        'as2d': False,
        'ugrid': False,
        'xyfactor': 1.0,
        'epsg': 27572,
        'dump': False,
        'attrs': None,
        'version': False,
        'debug': False
    }

    # Apply kwargs to override defaults
    defaults.update(kwargs)

    # Create mock args object
    mock_args = MagicMock()
    for key, value in defaults.items():
        setattr(mock_args, key, value)

    return mock_args


# ==================== Parse Args Tests ====================

def test_parse_args_basic_marthe_file():
    """Test parsing basic arguments with a Marthe grid file."""
    with patch('sys.argv', ['ncmart', 'test_grid.chasim']):
        args = parse_args()

        assert args.opt == ['test_grid.chasim']
        assert args.fname == 'test_grid'
        assert args.ext == '.chasim'
        assert args.output == 'test_grid.nc'
        assert args.varname is None
        assert args.nan is None
        assert args.grid_id is False
        assert args.as2d is False
        assert args.ugrid is False
        assert args.xyfactor == 1.
        assert args.epsg == 27572
        assert args.dump is False
        assert args.attrs is None


def test_parse_args_with_timesteps():
    """Test parsing with grid file and timesteps file."""
    with patch('sys.argv', ['ncmart', 'test_grid.chasim', 'test_pastp.pastp']):
        args = parse_args()

        assert args.opt == ['test_grid.chasim', 'test_pastp.pastp']
        assert args.fname == 'test_grid'
        assert args.ext == '.chasim'


def test_parse_args_with_output_option():
    """Test parsing with custom output filename."""
    with patch('sys.argv', ['ncmart', 'test_grid.chasim', '--output', 'custom_output.nc']):
        args = parse_args()
        assert args.output == 'custom_output.nc'


def test_parse_args_with_varname():
    """Test parsing with varname option."""
    with patch('sys.argv', ['ncmart', 'test_grid.chasim', '-n', 'PIEZOMETRY']):
        args = parse_args()
        assert args.varname == 'PIEZOMETRY'


def test_parse_args_varname_uppercase():
    """Test that varname is converted to uppercase."""
    with patch('sys.argv', ['ncmart', 'test_grid.chasim', '--varname', 'piezometry']):
        args = parse_args()
        assert args.varname == 'PIEZOMETRY'


def test_parse_args_with_nan_value():
    """Test parsing with custom NaN value."""
    with patch('sys.argv', ['ncmart', 'test_grid.chasim', '--nan', '999.0']):
        args = parse_args()
        assert args.nan == 999.0


def test_parse_args_with_nan_deactivated():
    """Test parsing with NaN dropout deactivated."""
    with patch('sys.argv', ['ncmart', 'test_grid.chasim', '--nan', '-1']):
        args = parse_args()
        assert args.nan == -1


def test_parse_args_with_grid_id():
    """Test parsing with grid-id flag."""
    with patch('sys.argv', ['ncmart', 'test_grid.chasim', '--grid-id']):
        args = parse_args()
        assert args.grid_id is True


def test_parse_args_with_as2d():
    """Test parsing with as2d flag."""
    with patch('sys.argv', ['ncmart', 'test_grid.chasim', '--as2d']):
        args = parse_args()
        assert args.as2d is True


def test_parse_args_with_ugrid():
    """Test parsing with ugrid flag."""
    with patch('sys.argv', ['ncmart', 'test_grid.chasim', '--ugrid']):
        args = parse_args()
        assert args.ugrid is True


def test_parse_args_with_xyfactor():
    """Test parsing with xyfactor option."""
    with patch('sys.argv', ['ncmart', 'test_grid.chasim', '--xyfactor', '2.5']):
        args = parse_args()
        assert args.xyfactor == 2.5


def test_parse_args_with_epsg():
    """Test parsing with epsg option."""
    with patch('sys.argv', ['ncmart', 'test_grid.chasim', '--epsg', '4326']):
        args = parse_args()
        assert args.epsg == 4326


def test_parse_args_with_dump():
    """Test parsing with dump flag."""
    with patch('sys.argv', ['ncmart', 'test_grid.chasim', '--dump']):
        args = parse_args()
        assert args.dump is True


def test_parse_args_with_attrs():
    """Test parsing with attrs option."""
    with patch('sys.argv', ['ncmart', 'test_grid.chasim', '--attrs', 'key1=value1,key2=value2']):
        args = parse_args()
        assert args.attrs == 'key1=value1,key2=value2'


def test_parse_args_netcdf_input():
    """Test parsing with netCDF input file."""
    with patch('sys.argv', ['ncmart', 'input.nc']):
        args = parse_args()

        assert args.opt == ['input.nc']
        assert args.fname == 'input'
        assert args.ext == '.nc'
        assert args.output == 'input.nc'


def test_parse_args_output_directory_creation():
    """Test that output directory is created if it doesn't exist."""
    with patch('sys.argv', ['ncmart', 'test_grid.chasim', '--output', 'output_dir/output.nc']):
        with patch('gridmarthe.scripts.ncmart.os.path.dirname') as mock_dirname:
            with patch('gridmarthe.scripts.ncmart.os.makedirs') as mock_makedirs:
                mock_dirname.return_value = 'output_dir'
                args = parse_args()

                assert args.output == 'output_dir/output.nc'
                mock_dirname.assert_called_once_with('output_dir/output.nc')
                mock_makedirs.assert_called_once_with('output_dir', exist_ok=True)


def test_parse_args_existing_output_removed():
    """Test that existing output file is removed."""
    with patch('sys.argv', ['ncmart', 'test_grid.chasim']):
        with patch('gridmarthe.scripts.ncmart.os.path.exists') as mock_exists:
            with patch('gridmarthe.scripts.ncmart.os.remove') as mock_remove:
                mock_exists.return_value = True
                args = parse_args()

                assert args.output == 'test_grid.nc'
                # Check that our specific call was made
                calls = [call for call in mock_exists.call_args_list if call[0][0] == 'test_grid.nc']
                assert len(calls) == 1
                mock_remove.assert_called_once_with('test_grid.nc')


def test_parse_args_version_exit():
    """Test parsing with version flag - should exit with code 0."""
    with patch('sys.argv', ['ncmart', '--version']):
        with patch('gridmarthe.scripts.ncmart.gm') as mock_gm:
            mock_gm.__version__ = '1.0.0'
            with patch('builtins.print') as mock_print:
                with pytest.raises(SystemExit) as exc_info:
                    parse_args()

                assert exc_info.value.code == 0
                mock_print.assert_called()


def test_parse_args_debug_exit():
    """Test parsing with debug flag - should exit with code 1."""
    with patch('sys.argv', ['ncmart', '--debug']):
        with patch('builtins.print') as mock_print:
            with pytest.raises(SystemExit) as exc_info:
                parse_args()

            assert exc_info.value.code == 1
            mock_print.assert_called()


def test_parse_args_no_arguments_exit():
    """Test parsing with no arguments - should exit with code 1."""
    with patch('sys.argv', ['ncmart']):
        with patch('builtins.print') as mock_print:
            with patch('argparse.ArgumentParser.print_usage') as mock_print_usage:
                with pytest.raises(SystemExit) as exc_info:
                    parse_args()

                assert exc_info.value.code == 1
                mock_print_usage.assert_called_once()


# ==================== Main Function Tests ====================

def test_main_dump_mode():
    """Test main function in dump mode."""
    with patch('sys.argv', ['ncmart', 'test_grid.chasim', '--dump']):
        with patch('gridmarthe.scripts.ncmart.parse_args') as mock_parse_args:
            with patch('gridmarthe.scripts.ncmart.gm') as mock_gm:
                with patch('builtins.print') as mock_print:
                    # Setup mock args
                    mock_args = create_mock_args(dump=True, opt=['test_grid.chasim'])
                    mock_parse_args.return_value = mock_args

                    # Setup mock scan_var
                    mock_gm.scan_var.return_value = ['VAR1', 'VAR2']

                    with pytest.raises(SystemExit) as exc_info:
                        main()

                    assert exc_info.value.code == 0
                    mock_gm.scan_var.assert_called_once_with('test_grid.chasim')


def test_main_marthe_grid_conversion():
    """Test main function converting Marthe grid to netCDF."""
    with patch('sys.argv', ['ncmart', 'test_grid.chasim']):
        with patch('gridmarthe.scripts.ncmart.parse_args') as mock_parse_args:
            with patch('gridmarthe.scripts.ncmart.gm') as mock_gm:
                with patch('gridmarthe.scripts.ncmart.xr') as mock_xr:
                    # Setup mock args
                    mock_args = create_mock_args(
                        opt=['test_grid.chasim'],
                        fname='test_grid',
                        ext='.chasim',
                        output='test_grid.nc',
                        dump=False,
                        nan=None,
                        varname=None,
                        xyfactor=1.0,
                        epsg=27572
                    )
                    mock_parse_args.return_value = mock_args

                    # Setup mock dataset
                    mock_ds = MagicMock()
                    mock_gm.load_marthe_grid.return_value = mock_ds
                    mock_ds.to_netcdf = MagicMock()

                    result = main()

                    # Check that load_marthe_grid was called with correct args
                    mock_gm.load_marthe_grid.assert_called_once()
                    call_args = mock_gm.load_marthe_grid.call_args
                    assert call_args[0][0] == 'test_grid.chasim'
                    assert call_args[1]['fpastp'] is None
                    assert call_args[1]['drop_nan'] is True
                    assert call_args[1]['nan_value'] is None

                    # Check that to_netcdf was called
                    mock_ds.to_netcdf.assert_called_once()
                    assert result == 0


def test_main_with_timesteps():
    """Test main function with timesteps file."""
    with patch('sys.argv', ['ncmart', 'test_grid.chasim', 'test_pastp.pastp']):
        with patch('gridmarthe.scripts.ncmart.parse_args') as mock_parse_args:
            with patch('gridmarthe.scripts.ncmart.gm') as mock_gm:
                # Setup mock args
                mock_args = create_mock_args(
                    opt=['test_grid.chasim', 'test_pastp.pastp'],
                    fname='test_grid',
                    ext='.chasim',
                    output='test_grid.nc',
                    dump=False
                )
                mock_parse_args.return_value = mock_args

                # Setup mock dataset
                mock_ds = MagicMock()
                mock_gm.load_marthe_grid.return_value = mock_ds
                mock_ds.to_netcdf = MagicMock()

                main()

                # Check that load_marthe_grid was called with fpastp
                call_args = mock_gm.load_marthe_grid.call_args
                assert call_args[1]['fpastp'] == 'test_pastp.pastp'


def test_main_netcdf_input_with_xyfactor():
    """Test main function with netCDF input and xyfactor transformation."""
    with patch('sys.argv', ['ncmart', 'input.nc', '--xyfactor', '2.0']):
        with patch('gridmarthe.scripts.ncmart.parse_args') as mock_parse_args:
            with patch('gridmarthe.scripts.ncmart.gm') as mock_gm:
                with patch('gridmarthe.scripts.ncmart.xr') as mock_xr:
                    # Setup mock args
                    mock_args = create_mock_args(
                        opt=['input.nc'],
                        fname='input',
                        ext='.nc',
                        output='input.nc',
                        dump=False,
                        xyfactor=2.0
                    )
                    mock_parse_args.return_value = mock_args

                    # Setup mock dataset
                    mock_ds = MagicMock()
                    mock_xr.open_dataset.return_value = mock_ds
                    mock_ds.to_netcdf = MagicMock()
                    mock_ds.attrs = {}

                    main()

                    # Check that xr.open_dataset was called
                    mock_xr.open_dataset.assert_called_once_with('input.nc')
                    # Check that scale_factor was added to attrs
                    assert 'scale_factor' in mock_ds.attrs


def test_main_with_ugrid():
    """Test main function with ugrid conversion."""
    with patch('sys.argv', ['ncmart', 'test_grid.chasim', '--ugrid']):
        with patch('gridmarthe.scripts.ncmart.parse_args') as mock_parse_args:
            with patch('gridmarthe.scripts.ncmart.gm') as mock_gm:
                # Setup mock args
                mock_args = create_mock_args(
                    opt=['test_grid.chasim'],
                    fname='test_grid',
                    ext='.chasim',
                    output='test_grid.nc',
                    dump=False,
                    ugrid=True
                )
                mock_parse_args.return_value = mock_args

                # Setup mock dataset
                mock_ds = MagicMock()
                mock_gm.load_marthe_grid.return_value = mock_ds
                mock_gm.create_ugrid.return_value = mock_ds  # Return the same dataset
                mock_ds.to_netcdf = MagicMock()

                main()

                # Check that create_ugrid was called
                mock_gm.create_ugrid.assert_called_once()


def test_main_with_as2d():
    """Test main function with as2d conversion."""
    with patch('sys.argv', ['ncmart', 'test_grid.chasim', '--as2d']):
        with patch('gridmarthe.scripts.ncmart.parse_args') as mock_parse_args:
            with patch('gridmarthe.scripts.ncmart.gm') as mock_gm:
                # Setup mock args
                mock_args = create_mock_args(
                    opt=['test_grid.chasim'],
                    fname='test_grid',
                    ext='.chasim',
                    output='test_grid.nc',
                    dump=False,
                    as2d=True
                )
                mock_parse_args.return_value = mock_args

                # Setup mock dataset
                mock_ds = MagicMock()
                mock_gm.load_marthe_grid.return_value = mock_ds
                mock_gm.assign_coords.return_value = mock_ds  # Return the same dataset
                mock_ds.to_netcdf = MagicMock()

                main()

                # Check that assign_coords was called
                mock_gm.assign_coords.assert_called_once()


def test_main_with_attrs():
    """Test main function with custom attributes."""
    with patch('sys.argv', ['ncmart', 'test_grid.chasim', '--attrs', 'key1=value1,key2=value2']):
        with patch('gridmarthe.scripts.ncmart.parse_args') as mock_parse_args:
            with patch('gridmarthe.scripts.ncmart.gm') as mock_gm:
                # Setup mock args
                mock_args = create_mock_args(
                    opt=['test_grid.chasim'],
                    fname='test_grid',
                    ext='.chasim',
                    output='test_grid.nc',
                    dump=False,
                    attrs='key1=value1,key2=value2'
                )
                mock_parse_args.return_value = mock_args

                # Setup mock dataset
                mock_ds = MagicMock()
                mock_ds.attrs = {}
                mock_gm.load_marthe_grid.return_value = mock_ds
                mock_ds.to_netcdf = MagicMock()

                main()

                # Check that attrs were added to dataset
                assert 'key1' in mock_ds.attrs
                assert 'key2' in mock_ds.attrs
                assert mock_ds.attrs['key1'] == 'value1'
                assert mock_ds.attrs['key2'] == 'value2'


def test_main_with_nan_dropout_deactivated():
    """Test main function with NaN dropout deactivated."""
    with patch('sys.argv', ['ncmart', 'test_grid.chasim', '--nan', '-1']):
        with patch('gridmarthe.scripts.ncmart.parse_args') as mock_parse_args:
            with patch('gridmarthe.scripts.ncmart.gm') as mock_gm:
                # Setup mock args
                mock_args = create_mock_args(
                    opt=['test_grid.chasim'],
                    fname='test_grid',
                    ext='.chasim',
                    output='test_grid.nc',
                    dump=False,
                    nan=-1
                )
                mock_parse_args.return_value = mock_args

                # Setup mock dataset
                mock_ds = MagicMock()
                mock_gm.load_marthe_grid.return_value = mock_ds
                mock_ds.to_netcdf = MagicMock()

                main()

                # Check that load_marthe_grid was called with drop_nan=False
                call_args = mock_gm.load_marthe_grid.call_args
                assert call_args[1]['drop_nan'] is False


def test_main_with_custom_nan_value():
    """Test main function with custom NaN value."""
    with patch('sys.argv', ['ncmart', 'test_grid.chasim', '--nan', '999.0']):
        with patch('gridmarthe.scripts.ncmart.parse_args') as mock_parse_args:
            with patch('gridmarthe.scripts.ncmart.gm') as mock_gm:
                # Setup mock args
                mock_args = create_mock_args(
                    opt=['test_grid.chasim'],
                    fname='test_grid',
                    ext='.chasim',
                    output='test_grid.nc',
                    dump=False,
                    nan=999.0
                )
                mock_parse_args.return_value = mock_args

                # Setup mock dataset
                mock_ds = MagicMock()
                mock_gm.load_marthe_grid.return_value = mock_ds
                mock_ds.to_netcdf = MagicMock()

                main()

                # Check that load_marthe_grid was called with correct nan_value
                call_args = mock_gm.load_marthe_grid.call_args
                assert call_args[1]['nan_value'] == 999.0
                assert call_args[1]['drop_nan'] is True


def test_main_with_varname():
    """Test main function with specific varname."""
    with patch('sys.argv', ['ncmart', 'test_grid.chasim', '--varname', 'PIEZOMETRY']):
        with patch('gridmarthe.scripts.ncmart.parse_args') as mock_parse_args:
            with patch('gridmarthe.scripts.ncmart.gm') as mock_gm:
                # Setup mock args
                mock_args = create_mock_args(
                    opt=['test_grid.chasim'],
                    fname='test_grid',
                    ext='.chasim',
                    output='test_grid.nc',
                    dump=False,
                    varname='PIEZOMETRY'
                )
                mock_parse_args.return_value = mock_args

                # Setup mock dataset
                mock_ds = MagicMock()
                mock_gm.load_marthe_grid.return_value = mock_ds
                mock_ds.to_netcdf = MagicMock()

                main()

                # Check that load_marthe_grid was called with correct varname
                call_args = mock_gm.load_marthe_grid.call_args
                assert call_args[1]['varname'] == 'PIEZOMETRY'


def test_main_with_grid_id():
    """Test main function with grid-id option."""
    with patch('sys.argv', ['ncmart', 'test_grid.chasim', '--grid-id']):
        with patch('gridmarthe.scripts.ncmart.parse_args') as mock_parse_args:
            with patch('gridmarthe.scripts.ncmart.gm') as mock_gm:
                # Setup mock args
                mock_args = create_mock_args(
                    opt=['test_grid.chasim'],
                    fname='test_grid',
                    ext='.chasim',
                    output='test_grid.nc',
                    dump=False,
                    grid_id=True
                )
                mock_parse_args.return_value = mock_args

                # Setup mock dataset
                mock_ds = MagicMock()
                mock_gm.load_marthe_grid.return_value = mock_ds
                mock_ds.to_netcdf = MagicMock()

                main()

                # Check that load_marthe_grid was called with add_id_grid and add_col_row
                call_args = mock_gm.load_marthe_grid.call_args
                assert call_args[1]['add_id_grid'] is True
                assert call_args[1]['add_col_row'] is True


def test_main_ugrid_uses_netcdf4_engine():
    """Test that ugrid conversion uses netcdf4 engine."""
    with patch('sys.argv', ['ncmart', 'test_grid.chasim', '--ugrid']):
        with patch('gridmarthe.scripts.ncmart.parse_args') as mock_parse_args:
            with patch('gridmarthe.scripts.ncmart.gm') as mock_gm:
                # Setup mock args
                mock_args = create_mock_args(
                    opt=['test_grid.chasim'],
                    fname='test_grid',
                    ext='.chasim',
                    output='test_grid.nc',
                    dump=False,
                    ugrid=True
                )
                mock_parse_args.return_value = mock_args

                # Setup mock dataset
                mock_ds = MagicMock()
                mock_gm.load_marthe_grid.return_value = mock_ds
                mock_gm.create_ugrid.return_value = mock_ds  # Return the same dataset
                mock_ds.to_netcdf = MagicMock()

                main()

                # Check that to_netcdf was called with netcdf4 engine
                call_args = mock_ds.to_netcdf.call_args
                assert call_args[1]['engine'] == 'netcdf4'


def test_main_non_ugrid_uses_h5netcdf_engine():
    """Test that non-ugrid conversion uses h5netcdf engine with compression."""
    with patch('sys.argv', ['ncmart', 'test_grid.chasim']):
        with patch('gridmarthe.scripts.ncmart.parse_args') as mock_parse_args:
            with patch('gridmarthe.scripts.ncmart.gm') as mock_gm:
                # Setup mock args
                mock_args = create_mock_args(
                    opt=['test_grid.chasim'],
                    fname='test_grid',
                    ext='.chasim',
                    output='test_grid.nc',
                    dump=False,
                    ugrid=False
                )
                mock_parse_args.return_value = mock_args

                # Setup mock dataset
                mock_ds = MagicMock()
                mock_ds.data_vars = {'var1': MagicMock(), 'var2': MagicMock()}
                mock_gm.load_marthe_grid.return_value = mock_ds
                mock_ds.to_netcdf = MagicMock()

                main()

                # Check that to_netcdf was called with h5netcdf engine and encoding
                call_args = mock_ds.to_netcdf.call_args
                assert call_args[1]['engine'] == 'h5netcdf'
                assert 'encoding' in call_args[1]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--no-cov"])
