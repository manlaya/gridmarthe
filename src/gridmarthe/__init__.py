import numpy as np
import pandas as pd
try:
    import gridmarthe.lecsem as lecsem
except ImportError:
    pass

def get_grid(filename, variable):
    nu_zoomx = lecsem.modgridmarthe.scan_nu_zoomx(filename)
    dims, nbsteps = lecsem.modgridmarthe.scan_dim(filename, variable, nu_zoomx)
    nbtot = np.product(dims, axis=1).sum()
    return lecsem.modgridmarthe.read_grid(
        filename, variable, nbsteps, nbtot, nu_zoomx
    )

