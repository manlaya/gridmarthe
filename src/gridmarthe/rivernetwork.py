import os

from .functions import (
    _calc_riv_network,
)
from gridmarthe import calc_flow_directions
import gridmarthe as gm

def calc_river_network(
    fpresence: str,
    fflowdir:str = None,
    flow_dirs_type: str = "marthe",
    eps_topo: float = 0.1,
    surf_riv: float = 30.0,
    nperio_reach: int = 1,
    n_neigh_station: int =1,
    fexis_riv_in: str = " ",
    fdrainage_surf_in: str = " ",
    fxy_surf_in: str = " ",
    fcol_row_sous_bv_in: str = " ",
    fnb_sous_bv_out: str = " ",
    fexis_riv_out: str = " ",
    fdrainage_surf_out: str = " ",
    friv_tree_out: str = " ",
    fafflu_num_out: str = " ",
    friv_reach_out: str = " ",
    fhisto_out: str = " ",
    fsous_bassin_out: str = " ",
):
    """
    Docstring for calc_river_network
    
    :param ftopo: Description
    :type ftopo: str
    :param file_flowdir: Description
    :type file_flowdir: str
    :param flow_dirs_type: Description
    :type flow_dirs_type: str
    :param eps_topo: Description
    :type eps_topo: float
    :param surf_riv: Description
    :type surf_riv: float
    :param nperio_tronc: Description
    :type nperio_tronc: int
    :param n_neigh_station: Description
    :type n_neigh_station: int
    :param file_exis_riv: Description
    :type file_exis_riv: str
    :param file_surf_up: Description
    :type file_surf_up: str
    :param file_xy_surf: Description
    :type file_xy_surf: str
    :param file_nb_sous_bv: Description
    :type file_nb_sous_bv: str
    :param file_col_row_sous_bv: Description
    :type file_col_row_sous_bv: str
    """

    if flow_dirs_type.lower() == "marthe":
        ityp_dir=0
    elif flow_dirs_type.lower() == "arcgis":
        ityp_dir=1
    elif flow_dirs_type.lower() == "qgis":
        ityp_dir=2
    else:
        raise Exception("Unknown type of D8 flow directions.")
        
    if fflowdir is None:
        print("No flow direction data provided. \nCalculate flow dirction based on presence file (.topo or .permh).")
        fout_dir=os.path.abspath(os.path.join(os.path.dirname(fpresence), "ddr_dir_aval.d_ava"))
        ftopo = fpresence
        
    #    _calc_flow_directions(fpresence, ftopo, fout_dir, fout_topo, flisting, ityp_dir, eps_topo) 
        ds = calc_flow_directions(ftopo=ftopo, fpresence=fpresence, flow_dirs_type=flow_dirs_type, eps_topo=eps_topo)
        # write ds to grid data
        # FIXME by default max_layer = 1
        gm.write_marthe_grid(ds=ds, fileout=fout_dir, varname='direct_aval', title="Calculated flow direcions: type " + flow_dirs_type)
        
        fflowdir = fout_dir
    
    
    flisting = os.path.abspath(os.path.join(os.path.dirname(fpresence), "Cal_river_network.listing"))
    # print(flisting)

    _calc_riv_network(fpresence, fflowdir, ityp_dir, surf_riv, nperio_reach, n_neigh_station,
                       fexis_riv_in, fdrainage_surf_in, fxy_surf_in, fcol_row_sous_bv_in, 
                       fnb_sous_bv_out, fexis_riv_out, fdrainage_surf_out, friv_tree_out, 
                       fafflu_num_out, friv_reach_out, fhisto_out, fsous_bassin_out,flisting)
    
    