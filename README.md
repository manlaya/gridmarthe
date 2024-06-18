# Gridmarthe

Python project for (fast) Gridmarthe operations.
A brand new "operasem" in other words :)


## gridmarthe in a nutshell

Full support of gridmarthe read operations by wrapping MARTHE fortran read/write module,
allowing fast reading of marthe grid file (v9, v8, constant_data, etc.), for any variable.
Recent developpment also allow writting MartheGrid_v9.0 file.

In python, gridmarthe files are loaded using numpy and xarray libraries.

Some "utils" functions are also provided (plot_nested_grid, interp, etc.).


## Installation

gridmarthe use Fortran module (partly from marthe source code, plus some specific developpement) which need
to be compiled before local installation.

### Compilation

On a linux machine, with gfortran, python3, numpy and charset_normalizer:

```bash
cd src/gridmarthe
f2py -c lecsem.f90 edsemigl.f90 scan_grid.f90 -m lecsem --fcompiler=gfortran
```

On a windows machine, with gitbash and gfortran (mingw project https://mingw-w64.org/)
```bash
cd src/gridmarthe
python setup.py build_ext --inplace --compiler=mingw32 --fcompiler=gnu95 -f
```

TODO: meson compilation at `pip install .`

### pip install

Install the python package (optionnaly in developper/editable mode)

```
pip install [-e] .
```

## Usage
TODO

## Contributing
TODO

## License
[MIT Licensed](LICENSE)

## Authors and acknowledgment
Created by JP Vergnes,
developped by JP Vergnes and A. Manlay
