# gridmarthe changelog

## [Unreleased]

## Added

- grid creation (from xy bounds or shape)
- ugrid export for GIS visualization

## Changed
- dates argument in `gridmarthe.load_marthe_grid` is renamed `times` to be
consistent with `time` dimension

## Fixed
- read int/float in times file (pastp)
- compute geometry with other variable names


## [0.4.0] - 2026-05-27

### Added

* add: drainage direction computation from legacy fortran sources
* add: river network computation from legacy fortran sources [#7](https://gitlab.com/brgm/hydrogeological-modelling/marthe-tools/gridmarthe/-/issues/7)
* add: `drop_time` argument to `gridmarthe.load_marthe_grid` to drop dummy time dimension
  when reading parameter grids.

### Changed

* change: drop support for python 3.10. Minimal requirement is now python 3.11
* change: default to `varname=None` when writing a marthe grid file (and guess first non dim variable)
* change: use integer as default dummy time dimension for parameters grid, instead of '1850-01-01' fake date.
* refact: code refactoring/reorganization with new fortran subroutines

### Fixed

* add/fix: reading grid with bad metadata (variable name, number of grids/layers) is now possible with fortran core module (fix_metada subroutine)
* fix: reading single grid output, even without metada (`read_shallow` parameter)
1st non dimension/coord variable will be selected. add `.lower()` security for user's variable
* fix: using `load_marthe_grid` with a Path object [#14](https://gitlab.com/brgm/hydrogeological-modelling/marthe-tools/gridmarthe/-/issues/14)
* fix: bad return array with `get_active_mask` [#13](https://gitlab.com/brgm/hydrogeological-modelling/marthe-tools/gridmarthe/-/issues/13)
* fix: order of y coordinates in stack coords [#11](https://gitlab.com/brgm/hydrogeological-modelling/marthe-tools/gridmarthe/-/issues/11)
* fix: cleanmgrid script [#10](https://gitlab.com/brgm/hydrogeological-modelling/marthe-tools/gridmarthe/-/issues/10) [#15](https://gitlab.com/brgm/hydrogeological-modelling/marthe-tools/gridmarthe/-/issues/15) [#17](https://gitlab.com/brgm/hydrogeological-modelling/marthe-tools/gridmarthe/-/issues/17)
* fix: ncmart script [#9](https://gitlab.com/brgm/hydrogeological-modelling/marthe-tools/gridmarthe/-/issues/9)
* fix: netcdf attrs conflict with missing value [#16](https://gitlab.com/brgm/hydrogeological-modelling/marthe-tools/gridmarthe/-/issues/16)


## [0.3.0] - 2025-12-09

### Added

* add: beta support for vtk export, based on [vtkwriters](https://gitlab.com/brgm/geomodelling/io/vtkwriters) from ComPass code python ecosystem
* add: support for reading/plotting velocity field : `gm.read_velocity`, `gm.plot_veloc_quiver`
* add: beta support for cross section
* add: options to `ncmart` script:
    - `--dump` (`-H`) to mimic `ncdump -H` command (netcdf CLI tools).
    - `--attrs` (`-a`) to add global attributes
    - treat input if already in netcdf fmt (modify it, with scale factor or attrs, to 2D, etc)

### Changed

* change: attributes in netcdf to be more CF-Conventions compliant:
    - add crs attributes using `pyrpoj.CRS().to_cf()` for QGIS view compatibilty --> add argument `epsg` in `gm.load_grid_marthe`
    - add `compress` attribute for zone [https://cfconventions.org](https://cfconventions.org/Data/cf-conventions/cf-conventions-1.11/cf-conventions.html#reduced-horizontal-grid),
    - fix attributes for coordinates x,y,z / add argument `full_3d` to set z attributes
    - force attributes for x,y,z to be kept when `gm.assign_coords`

### Fixed

* fix: cleanmgrid with conda [#8](https://gitlab.com/brgm/hydrogeological-modelling/marthe-tools/gridmarthe/-/issues/8)


## [0.2.0] - Unreleased

### Changed

* `nanval` argument in `load_marthe_grid` is rename to `nan_value` as in `write_marthe_grid`
* `keepligcol` argument in `load_marthe_grid` is rename to `add_col_row` to be more coherent with `add_id_grid`

### Fixed

* error when writing grid with time slice (cf. [issue #3](https://gitlab.com/brgm/hydrogeological-modelling/marthe-tools/gridmarthe/-/issues/3))
* fix: REVERT change from 0.1.3 : zone index is NOT reset (as in 0.1.2 and previous versions).
  when the `drop_nan` option is used in `load_grid_marthe()`.
  A new variable 'izone' store the reset form.
  See [issue #4](https://gitlab.com/brgm/hydrogeological-modelling/marthe-tools/gridmarthe/-/issues/4)

### Removed

* `xr.Dataset.mart` class accessor is removed. It will be included as wrapper in future marthe python library.


## [0.1.3] - 2025-09-02

### Added

* add geometry functions (`get_mask_array`, `compute_geometry`)
* add reprojection functions (still experimental)
* add `martshp` script to easily convert a marthe grid file into a shp/gpkg file in command line
* add automatic tests

### Changed

* change: rename function to write raster: `to_raster()` instead of `write_raster_from_da()`
* change: zone index is reset when the `drop_nan` option is used in `load_grid_marthe()`. A new
  variable 'zone_all' store the old index for the `reset_geometry()` method
* code refactoring (lecsem module and global organization)

### Fixed

* minor fixes in plot method


## [0.1.2] - 2025-01-09

* Change build to meson
* fix scripts 'ncmart' and 'cleanmgrid' paths
* update write method


## [0.1.1] - 2024-11-03.

* first release as a stand alone package


## [0.0.1] - Unreleased

Unreleased, internal dev at BRGM - 2021-2024

* Use fortran sources from Marthe with f2py to read grids, single layer, homogeneous grids (1st version from JP Vergnes)
* Extend to multilayer, nested grid (A Manlay)
* Python wrappers for easy read operations (AM)
* Add write method in Fortran sources, scan var and wrappers (AM)
* Add command line scripts, and some derived treatments (surface layer, rescale, etc.)
