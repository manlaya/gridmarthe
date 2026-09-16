#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import gridmarthe as gm
from gridmarthe.core import scan_var, modgridmarthe
import pytest

DATA_PATH = './tests/data'


def test_scan_var_single_variable():
    """Test scanning a file with a single variable"""
    permh_file = f'{DATA_PATH}/hallue.permh'
    var = scan_var(permh_file)
    assert isinstance(var, np.ndarray), 'scan_var should return numpy array'
    assert len(var) == 1, 'Should find at least one variable'
    assert 'PERMEAB' in var, 'PERMEAB should be in single variable permh file'


def test_scan_var_multiple_variables():
    """Test scanning a file with multiple variables"""
    out_file = f'{DATA_PATH}/chasim_hallue_2var.out'
    var = scan_var(out_file)
    assert isinstance(var, np.ndarray), 'scan_var should return numpy array'
    assert len(var) == 2, 'Should find two variables'
    # CHARGE should be present in simulation output
    assert any('CHARGE' in v.upper() for v in var), 'CHARGE should be in simulation output'
    assert any('%SATURAT' in v.upper() for v in var), 'CHARGE should be in simulation output'


def test_scan_var_nested_grid():
    """Test scanning a nested grid file"""
    permh_file = f'{DATA_PATH}/Somme_V3_Surfex.permh'
    var = scan_var(permh_file)
    assert isinstance(var, np.ndarray), 'scan_var should return numpy array'
    assert len(var) == 1, 'Should find one variable, even for nested grids'
    assert 'PERMEAB' in var, 'PERMEAB should be in nested grid permh file'


def test_scan_var_multilayer():
    """Test scanning a multilayer file"""
    permh_file = f'{DATA_PATH}/craie_npc_gig.permh'
    var = scan_var(permh_file)
    assert isinstance(var, np.ndarray), 'scan_var should return numpy array'
    assert len(var) == 1, 'Should find one variable'
    assert 'PERMEAB' in var, 'PERMEAB should be in multilayer permh file'


def test_scan_var_return_type():
    """Test that scan_var returns string array"""
    permh_file = f'{DATA_PATH}/hallue.permh'
    var = scan_var(permh_file)
    # Check that all elements are strings
    for v in var:
        assert isinstance(v, (str, np.str_)), f'All elements should be strings, got {type(v)}'


def test_fortran_io_error():
    # before v0.5, Fortran IO error was not captured and would either
    # cause a sys.exit or a  ValueError: Varname (CHARGE) not found in xfile.
    # in load_marthe_grid ; wrongly interpreted as a missing variable.
    with pytest.raises(gm.FortranError):
        scan_var('non_existent_file')


def test_fortran_io_stat():
    var, iostat = modgridmarthe.scan_typevar(f'{DATA_PATH}/hallue.permh')
    assert iostat == 0

    # not a file
    var, iostat = modgridmarthe.scan_typevar('non_existent_file')
    assert iostat == -2

    # a file but not a grid - should not cause a stop
    var, iostat = modgridmarthe.scan_typevar('tests/data/albien.pastp')
    assert iostat != 0


if __name__ == '__main__':
    test_scan_var_single_variable()
    test_scan_var_multiple_variables()
    test_scan_var_nested_grid()
    test_scan_var_multilayer()
    test_scan_var_return_type()
    print("All scan_var tests passed!")
