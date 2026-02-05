# -*- coding: utf-8 -*-
import os
import subprocess

import gridmarthe as pm
# from gridmarthe import calc_river_network


DATA_PATH = './tests/data'

def test_calc_river_network():
    file_topo = os.path.join(os.path.abspath(DATA_PATH), "craie_npc.topog")
    fexis_riv_out = os.path.join(os.path.abspath(DATA_PATH), "exis_riv_out.riv")
    fafflu_out = os.path.join(os.path.abspath(DATA_PATH), "afflu_num_out.aff_r")
    ftronc_out = os.path.join(os.path.abspath(DATA_PATH), "riv_reach_out.trc_r")
    friv_tree_out = os.path.join(os.path.abspath(DATA_PATH), "riv_tree_out.arb_r")
    pm.calc_river_network(fpresence=file_topo, n_neigh_station = 2, fexis_riv_out = fexis_riv_out, friv_tree_out = friv_tree_out, fafflu_num_out = fafflu_out,
                       friv_reach_out = ftronc_out)
    
   
    # call cleanmgrid (for layer)
    # need INDIC_RIVI added in MARTGRID_FILES in cleanmgrid.py
    subprocess.run(
        [
            "cleanmgrid", "-l", "1", "-g", "0", "-n", fexis_riv_out
        ]
    )
    
    subprocess.run(
        [
            "cleanmgrid", "-l", "1", "-g", "0", "-n", fafflu_out
        ]
    )

    subprocess.run(
        [
            "cleanmgrid", "-l", "1", "-g", "0", "-n", ftronc_out
        ]
    )
    
    # calculated data by python
    exis_riv_dat_py = pm.load_marthe_grid(fexis_riv_out)
    afflu_num_dat_py = pm.load_marthe_grid(fafflu_out)
    tronc_riv_dat_py = pm.load_marthe_grid(ftronc_out)
    
    # calculated data by winmarthe
    exis_riv_dat_win = pm.load_marthe_grid(os.path.join(os.path.abspath(DATA_PATH), "exits_riv_out_ref.riv"))
    afflu_num_dat_win = pm.load_marthe_grid(os.path.join(os.path.abspath(DATA_PATH), "riv_reach_out_ref.aff_r"))
    tronc_riv_dat_win = pm.load_marthe_grid(os.path.join(os.path.abspath(DATA_PATH), "allu_num_out_ref.trc_r"))    
    
    assert exis_riv_dat_py.equals(exis_riv_dat_win)
    assert afflu_num_dat_py.equals(afflu_num_dat_win)
    assert tronc_riv_dat_py.equals(tronc_riv_dat_win)
    
    assert open(friv_tree_out,'r', encoding='latin-1').read() == open(os.path.join(os.path.abspath(DATA_PATH), "tiv_tree_out_ref.arb_r"),'r', encoding='latin-1').read()

    
if __name__ == "__main__":
    DATA_PATH = './data'
    test_calc_river_network()