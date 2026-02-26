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
    """ Calculate river network based on the presence file (.topog or .permh) or flow directions.
    
    Parameters
    ----------
    fpresence: str
        A path to presence of surface domain file (.topog or .permh).
        If .permh file is passed, permeability values are set to 0 or 9999 outside of the domain.
        If .topog file is passed, all altitude values should be positive (> 0).
        
    fflowdir: str, optional
        A path to flow directions file (.d_ava).
        If None (by default) is passed, flow directions are calculated based on the presence file.
        
    flow_dirs_type: str, optional
        Type of D8 flow directions, e.g. ``marthe`` or ``ArcGis`` or ``Qgis``.
        
        By default, it is ``marthe``.
        
        If ``marthe`` is passed: 
            1001 -- North,     1002 -- East,      1003 -- South,     1004 -- West
            1005 -- Northeast, 1006 -- Southeast, 1007 -- Southwest, 1008 -- Northwest
            9999 -- for any grid cell adjacent to the edge of the domain. 

        If ``ArcGis`` is passed: 
            1 -- East,  2 -- Southeast,  4 -- South,  8 -- Southwest
            16 -- West, 32 -- Northwest, 64 -- North, 128 -- Northeast
            0 -- for any grid cell adjacent to the edge of the domain.         

        If ``Qgis`` is passed: 
            1 -- East,  2 -- Northeast,  3 -- North,  4 -- Northwest
            5 -- West,  6 -- Southwest,  7 -- South,  8 -- Southeast
            0 -- for any grid cell adjacent to the edge of the domain.
            
    eps_topo: float, optional
        FIXME: Correction d'altitude unitaire (?), a positif float value.
        By default, it is 0.1. Any negatif value will be replace by 0.1.
        
    surf_riv: float, optional
        A threshold of drainage area of a grid cell to determine if the grid cell is a river cell.
        By default, it is 30.0 km^2.
        
    nperio_reach: int, optional
        FIXME: Périodicité des numéros de tronçons (?).
        By default, it is 1.
        
    n_neigh_station: int, optional
        FIXME: Nombre de mailles voisines pour opti. surfaces stations Hydro. Utilisé uniquement pour définir le fichier historique.
        By default, it is 1.
        
    fexis_riv_in: str, optional
        A path to river indicator file (.riv). 
        If " " (by default) is passed, river indicator will be calculated.
        
    fdrainage_surf_in: str, optional
        A path to drainage area file (.surf, .sur). 
        If " " (by default) is passed, it is set as " ", drainage areas will be calculated using ``surf_riv``.
    
    fxy_surf_in: str, optional
        FIXME: A path to the list file of stations Hydro avec la Surface (.prn, .txt). 
        It is used to Calcul et correction des surfaces des Stations Hydrométriques (FICH_HISTORIQ) à partir des surfaces drainées.
        If " " (by default) is passed, no correction is performed.
    
    fcol_row_sous_bv_in: str, optional
        A path to column and row of sub-basin outlet file (.prn, .txt). 
        It is used to calculate sub-basin number of marthe grid.
        If " " (by default) is passed, no sub-basin number is calculated.
    
    fnb_sous_bv_out: str, optional
        A path to calculated sub-basin number file (.num_bv).
        If " " (by default) is passed, the file is not created.
    
    fexis_riv_out: str, optional
        A path to calculated river indicator file (.riv).
        If " " (by default) is passed, no file is created.
    
    fdrainage_surf_out: str, optional
        A path to calculated drainage area file (.surf, .sur).
        If " " (by default) is passed, no file is created.
    
    friv_tree_out: str, optional
        A path to calculated river tree file (.arb_r). 
        If " " (by default) is passed, no file is created.
    
    fafflu_num_out: str, optional
        A path to calculated number of tributaries file (.aff_r). 
        If " " (by default) is passed, no file is created.
    
    friv_reach_out: str, optional
        A path to calculated river reach number file (.trc_r). 
        If " " (by default) is passed, no file is created.
    
    fhisto_out: str, optional
        A path to corrected historic file (.prn). 
        If " " (by default) is passed, no file is created.
    
    fsous_bassin_out: str, optional
        A path to sub-basin mask file (.prn).
        If " " (by default) is passed, no file is created.
        
    Returns
    -------
    None. 
    A listing file (Cal_river_network.listing) is created in the same directory as the presence file, 
    which contains all information about the river network calculation results.
    
    Example:
    --------
        >>> import gridmarthe as pm
        ... pm.calc_river_network(fpresence="./tests/data/craie_npc.topog", 
        ...            n_neigh_station = 2, 
        ...            fafflu_num_out = "./tests/data/afflu_num_out.aff_r",
        ...            friv_reach_out = "./tests/data/riv_reach_out.trc_r"
        ...            )
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
        print("No flow directions data provided. Calculate flow directions based on the presence file (.topog or .permh).")
        fout_dir=os.path.abspath(os.path.join(os.path.dirname(fpresence), "ddr_dir_aval.d_ava"))
        ftopo = fpresence
        
    #    _calc_flow_directions(fpresence, ftopo, fout_dir, fout_topo, flisting, ityp_dir, eps_topo) 
        ds = calc_flow_directions(ftopo=ftopo, fpresence=fpresence, flow_dirs_type=flow_dirs_type, eps_topo=eps_topo)
        # write ds to grid data
        gm.write_marthe_grid(ds=ds, fileout=fout_dir, varname='direct_aval', title="Calculated flow direcions: type " + flow_dirs_type)
        
        fflowdir = fout_dir
    
    
    flisting = os.path.abspath(os.path.join(os.path.dirname(fpresence), "Cal_river_network.listing"))
    # print(flisting)

    _calc_riv_network(fpresence, fflowdir, ityp_dir, surf_riv, nperio_reach, n_neigh_station,
                       fexis_riv_in, fdrainage_surf_in, fxy_surf_in, fcol_row_sous_bv_in, 
                       fnb_sous_bv_out, fexis_riv_out, fdrainage_surf_out, friv_tree_out, 
                       fafflu_num_out, friv_reach_out, fhisto_out, fsous_bassin_out,flisting)
    
    