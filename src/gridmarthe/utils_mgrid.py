import numpy as np

def get_scale(da):
    """ Get unique values of dx, dy marthegrid.Dataset """
    dx = np.sort(np.unique(da['dx'].values))[::-1]
    dy = np.sort(np.unique(da['dx'].values))[::-1]
    return list(dx[~np.isnan(dx)]), list(dy[~np.isnan(dy)])


def find_nearest(array, value):
    # https://stackoverflow.com/questions/2566412/find-nearest-value-in-numpy-array
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx]


def search_zone(ds, i=None, j=None, x=None, y=None):
    """ search zone number in marthe grid,
    based on xy or ij (col, lig)
    """
    if x is not None:
        assert y is not None, 'if x is provided, y cannot be None'
        true_x = find_nearest(ds['x'].data, x)
        true_y = find_nearest(ds['y'].data, y)
        mask = (ds['x'] == true_x) & (ds['y'] == true_y)
        # mask = ds.sel(x=x, y=y, method='nearest') # possible uniquement si x,y sont des coordonnées/dim
        
    if i is not None:
        assert j is not None, 'if i is provided, j cannot be None'
        mask = (ds['col'] == i) & (ds['lig'] == j)

    # zone = ds.where(mask, drop=True)['zone'].data
    zone = ds.where(mask, drop=True)
    return zone