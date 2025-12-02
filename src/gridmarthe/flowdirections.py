import os
from .functions import _calc_flow_directions

def calc_flow_directions(
    ftopo: str,
    fpresence: str = None,
    flow_dirs_type: str = "marthe",
    eps_topo: float = 0.1
):
    """ Calculate flow dirction based on topography
    
    Parameters
    ----------
    ftopo: str
        A path to topography file (.topo)
        
    fpresence: str, optional
        A path to presence of area surface file. 
        If None (by default) is passed, it is set as the topography file path.
        
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
        Correction d'altitude unitaire (?), a positif float value. 
        By default, it is 0.1. Any negatif value will be replace by 0.1
        
    Returns
    -------
        
    """
    if fpresence is None:
        fpresence = ftopo
        
    fout_dir=os.path.abspath(os.path.join(os.path.dirname(ftopo), "ddr_dir_aval.d_ava"))
    fout_topo=os.path.abspath(os.path.join(os.path.dirname(ftopo), "ddr_topo_corr.topop"))
    flisting=os.path.abspath(os.path.join(os.path.dirname(ftopo), "ddr_calc_flow_direction.listing"))
    
    if flow_dirs_type.lower() == "marthe":
        ityp_direct=0
    elif flow_dirs_type.lower() == "arcgis":
        ityp_direct=1
    elif flow_dirs_type.lower() == "qgis":
        ityp_direct=2
    else:
        raise Exception("Unknown type of D8 flow directions.")

    if (eps_topo <= 0.):
        eps_topo = 0.1

    _calc_flow_directions(fpresence, ftopo, fout_dir, fout_topo, flisting, ityp_direct, eps_topo)  
    