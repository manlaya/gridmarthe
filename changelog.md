<!-- gridmarthe changelog -->

v0.4.0
------

<!-- Released on 202X-XX-XX -->

* add: drainage direction computation from legacy fortran sources
* fix: reading single grid output, even without metada (`read_shallow` parameter)
* change: default to `varname=None` when writing a marthe grid file.
1st non dimension/coord variable will be selected.
add `.lower()` security for user's variable


v0.3.0
------

Released on 2025-12-09

* add: beta support for vtk export, based on [vtkwriters](https://gitlab.com/brgm/geomodelling/io/vtkwriters) from ComPass code python ecosystem
* add: support for reading/plotting velocity field : `gm.read_velocity`, `gm.plot_veloc_quiver`
* add: beta support for cross section
* change: attributes in netcdf to be more CF-Conventions compliant:
    - add crs attributes using `pyrpoj.CRS().to_cf()` for QGIS view compatibilty --> add argument `epsg` in `gm.load_grid_marthe`
    - add `compress` attribute for zone [https://cfconventions.org](https://cfconventions.org/Data/cf-conventions/cf-conventions-1.11/cf-conventions.html#reduced-horizontal-grid),
    - fix attributes for coordinates x,y,z / add argument `full_3d` to set z attributes
    - force attributes for x,y,z to be kept when `gm.assign_coords`
* add: options to `ncmart` script:
    - `--dump` (`-H`) to mimic `ncdump -H` command (netcdf CLI tools).
    - `--attrs` (`-a`) to add global attributes
    - treat input if already in netcdf fmt (modify it, with scale factor or attrs, to 2D, etc)


v0.2.0
------

<!-- Released on 2025-XX-XX -->
Unreleased - dev version.

* fix: error when writing grid with time slice (cf. [issue #3](https://gitlab.com/brgm/hydrogeological-modelling/marthe-tools/gridmarthe/-/issues/3))
* fix: REVERT change from 0.1.3 : zone index is NOT reset (as in 0.1.2 and previous versions).
    when the `drop_nan` option is used in `load_grid_marthe()`.
    A new variable 'izone' store the reset form.
    See [issue #4](https://gitlab.com/brgm/hydrogeological-modelling/marthe-tools/gridmarthe/-/issues/4)
* change: `nanval` argument in `load_marthe_grid` is rename to `nan_value` as in `write_marthe_grid`
* change: `keepligcol` argument in `load_marthe_grid` is rename to `add_col_row` to be more coherent with `add_id_grid`
* change: `xr.Dataset.mart` class accessor is removed. It will be included as wrapper in future marthe python library.


v0.1.3
------

Released on 2025-09-02

* minor fixes in plot method
* add geometry functions (`get_mask_array`, `compute_geometry`)
* add reprojection functions (still experimental)
* add `martshp` script to easily convert a marthe grid file into a shp/gpkg file in command line
* change: rename function to write raster: `to_raster()` instead of `write_raster_from_da()`
* change: zone index is reset when the `drop_nan` option is used in `load_grid_marthe()`. A new
  variable 'zone_all' store the old index for the `reset_geometry()` method
* code refactoring (lecsem module and global organization)
* add automatic tests


v0.1.2
------

Released on 2025-01-09

* Change build to meson
* fix scripts 'ncmart' and 'cleanmgrid' paths
* update write method


v0.1.1
------

Released on 2024-11-03.

* first release as a stand alone package


v0.0.1
------

Unreleased - 2021-2024

* Use fortran sources from Marthe with f2py to read grids, single layer, homogeneous grids (1st version from JP Vergnes)
* Extend to multilayer, nested grid (A Manlay)
* Python wrappers for easy read operations (AM)
* Add write method in Fortran sources, scan var and wrappers (AM)
* Add command line scripts, and some derived treatments (surface layer, rescale, etc.)
