from gridmarthe.grid.processing.flowdirections import calc_flow_directions
import os
import pandas as pd
import numpy as np
import xarray as xr
import gridmarthe as gm


DATA_PATH = './tests/data'
OUTPUT_PATH = './tests/tmp_outputs'


def test_calc_flow_direct():
    file_presence = os.path.join(os.path.abspath(DATA_PATH), "craie_npc.topog")
    file_topo = os.path.join(os.path.abspath(DATA_PATH), "craie_npc.topog")

    ds = calc_flow_directions(file_presence,file_topo)
    assert isinstance(ds, xr.Dataset)

    # write ds to grid data
    # FIXME by default max_layer = 1
    gm.write_marthe_grid(ds=ds, fileout=os.path.join(os.path.abspath(OUTPUT_PATH), "test_write_dir_aval.d_ava"), varname='direct_aval')
    ds_read = gm.load_marthe_grid(os.path.join(os.path.abspath(OUTPUT_PATH), "test_write_dir_aval.d_ava"))
    assert ds.equals(ds_read)

    # use gridmarthe to read full data ?
    dir_aval_python = pd.read_csv(f"{DATA_PATH}{os.sep}ddr_dir_aval.d_ava", skiprows=28, nrows=305, header=None, sep="\t")
    dir_aval_ref_fortran = pd.read_csv(f"{DATA_PATH}{os.sep}dir_aval_craie_npc_ref.d_ava", skiprows=28, nrows=305, header=None, sep="\t")

    topo_correct_python = pd.read_csv(f"{DATA_PATH}{os.sep}ddr_topo_corr.topop", skiprows=28, nrows=305, header=None, encoding="latin1", sep="\t")
    topo_correct_ref_fortran = pd.read_csv(f"{DATA_PATH}{os.sep}topo_corr_craie_npc_ref.topop", skiprows=28, nrows=305, header=None, encoding="latin1", sep="\t")

    assert np.allclose(dir_aval_python.values, dir_aval_ref_fortran.values, rtol=1e-05, atol=1e-08, equal_nan=True)
    assert np.allclose(topo_correct_python.values, topo_correct_ref_fortran.values, rtol=1e-05, atol=1e-08, equal_nan=True)

if __name__ == "__main__":
    DATA_PATH = './data'
    test_calc_flow_direct()
