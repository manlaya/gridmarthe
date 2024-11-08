
import gridmarthe as gm

inputs = './data/craie_npc.permh', "PERMEAB"


toto = gm.load_marthe_grid(*inputs)
toto = gm.load_marthe_grid(*inputs, dropna=True)
toto = gm.load_marthe_grid(*inputs, dropna=True, nanval=0.)
toto = gm.load_marthe_grid(inputs[0], varname=None)
toto = gm.load_marthe_grid(inputs[0], varname='all')
toto = gm.load_marthe_grid(*inputs, keepligcol=True)
toto = gm.load_marthe_grid(*inputs, add_id_grid=True)

print(toto.attrs)

# for pymarthe compat'
# to recarray
# df=  toto.to_dataframe()
# df.to_records()

toto2 = toto.mart.assign_coords()
toto3 = toto.mart.to_recarray()


# import matplotlib.pyplot as plt
# toto2.permeab.sel(z=6).isel(time=0).plot.pcolormesh()
# plt.show()


