import gridmarthe as gm


ds = gm.load_marthe_grid(
    'Jordan_aquifers.out', 
    'all', 
    fpastp='Jordan_aquifers.pastp',
    drop_nan=True
)
