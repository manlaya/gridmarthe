import numpy as np

def _datetime64_to_float(zdates, origin='1970-01-01T00:00:00'):
    # Memo: here, origin should be defined from pastp (time since timestep 0)
    idate = (zdates - np.datetime64(origin)) / np.timedelta64(1, 's')
    idate = np.where(idate < 0., 0., idate) # fake dates from load_marthe_grid will be set to 0, meaning timestep -9999. (eg used in parameters grids)
    return idate

def _is_sorted(a):
    return np.all(a[:-1] <= a[1:])


def _get_scale(da):
    """ Get unique values of dx, dy marthegrid.Dataset """
    dx = np.sort(np.unique(da['dx'].values))[::-1]
    dy = np.sort(np.unique(da['dx'].values))[::-1]
    return list(dx[~np.isnan(dx)]), list(dy[~np.isnan(dy)])


def _find_nearest(array, value):
    # https://stackoverflow.com/questions/2566412/find-nearest-value-in-numpy-array
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx]


def _nearest_node(node, nodes):
    """ Get nearest value in an array of tuple, i.e closest euclidiant distance of XY in an array of XYs"""
    # https://codereview.stackexchange.com/questions/28207/finding-the-closest-point-to-a-list-of-points
    nodes = np.asarray(nodes)
    dist_2 = np.sum((nodes - node)**2, axis=1)
    return np.argmin(dist_2)

