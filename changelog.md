v0.1.3
------

Released on 2025-XX-XX

* add geometry functions (get_mask_array, compute_geometry)
* add reprojection functions (still experimental)
* add `martshp` script to easily convert a marthe grid file into a shp/gpkg file in command line
* code refactoring (lecsem module and global organization)
* minor fixes in plot method
* change: zone index is reset when the `drop_nan` option is used in `load_grid_marthe()`
* change: rename function to write raster: `to_raster()` instead of `write_raster_from_da()` 


v0.1.2
------

Released on 2025-01-09

* Change build to meson
* fix scripts 'ncmart' and 'cleanmgrid' paths
* update write method


v0.1.1
------

Released on 2024-11-03.

* first release
