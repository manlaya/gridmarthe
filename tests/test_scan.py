
import numpy as np
from gridmarthe import lecsem
# inputs = './data/craie_npc.permh', "PERMEAB"
inputs = './data/craie_npc.permh', "KKKK"
xfile = inputs[0]
varname = inputs[1]

var = lecsem.modgridmarthe.scan_typevar(inputs[0])
var = np.char.strip(np.char.decode(var, 'utf-8'))
var = var[var != '']
# var[0]
print(var)
len(var)

varname = var[0]
nu_zoomx = lecsem.modgridmarthe.scan_nu_zoomx(xfile) # scan nb of nested grids (gig)
dims, nbsteps = lecsem.modgridmarthe.scan_dim(xfile, varname, nu_zoomx)
np.prod(dims, axis=1).sum()

