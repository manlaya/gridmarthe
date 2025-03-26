#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import gridmarthe as gm


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    
    import os;os.chdir('./tests')
    print(gm.lecsem.__doc__)
    print(gm.lecsem.modgridmarthe.__doc__)
    
    xfiles = [
        ('hallue', './data/chasim_hallue.out', 'CHARGE'),
        # ('hallue', './data/chasim_hallue_multilay.out', 'CHARGE'),
        # ('hallue', './data/chasim_hallue_2fields.out', 'CHARGE'),
        # ('mart-npc', './data/chasim_npc_gig_1_layer.out', 'CHARGE'),
        # ('mart-npc', './data/chasim_npc_gig.out', 'CHARGE'),
        ('mart-npc2', './data/craie_npc.permh', 'PERMEAB')
                                        
    ]
    
    date_range = {
        'hallue'  : pd.DatetimeIndex(gm.read_dates_from_pastp('./data/hallue.pastp')['Date']),
        'mart-npc': pd.date_range('2020-12-01', '2020-12-31', freq='M'),# fake dates for testing
        'mart-npc2': None,# fake dates for testing
    }

    for modele, filename, varname in xfiles:
        # modele, filename = xfiles[-1] # testing
        # modele, filename = xfiles[1] # testing
        dates = date_range[modele]
        
        ds = gm.load_marthe_grid(
            filename,
            varname,
            dates,
            # xyfactor=1000,
            # ajouter les unités si besoin
            # idealement, ajouter la réf du model, la projection
            model_attrs={'projection': 'epsg:27572', "references": "Manlay et al., 2023"}
        )
        
        masque = ds[varname.lower()].where(ds[varname.lower()] != 9999.).dropna(dim='zone') # drop nan_val
        ds = ds.sel(zone=masque['zone'])

        # if "z" in ds.keys():
        #     first_lay = gm.get_min_layer(ds.isel(time=0))
        #     gm.plot_outcrop(ds, engine='xr')
        #     # plot_outcrop(ds, varname='permeab', nanval=0., engine='xr')

        #     # dsbis = gm.assign_coords(ds)
        #     # dsbis['charge'].plot.pcolormesh(x='x', y='y', row='z', col='time')
        #     # Pour les gigognes, la grille irrégulière créée rend discontinu le graphique
        #     # soit interpol, soit geopandas --> polyg.
        #     # dsbis['charge'].sel(z=[6,9]).plot.pcolormesh(x='x', y='y', row='z', col='time')
        #     plt.show()
        #     plt.close()
