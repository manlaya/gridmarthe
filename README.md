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

On a linux machine, with gfortran, python3, numpy (version < 2.0) and charset_normalizer:

```bash
cd src/gridmarthe/lecsem
f2py -c lecsem.f90 edsemigl.f90 scan_grid.f90 -m lecsem --fcompiler=gfortran
```

On a windows machine, with gitbash, gfortran (mingw project https://mingw-w64.org/ ou https://winlibs.com/#download-release),
make, microsoft visual C++ V14, 
python (v3), numpy (version < 2.0) and charset_normalizer:

```bash
cd src/gridmarthe/lecsem
python setup.py build_ext --inplace --compiler=mingw32 --fcompiler=gnu95 -f
```
TODO: adapter le setup.py pour windows et numpy>=2.0 (sans distutils)
TODO: meson compilation at `pip install .`

### pip install

Install the python package (optionnaly in developper/editable mode), back at package root directory:

```
pip install [-e] .
```

## Usage

A simple example can be found as a
[notebook](example/gm_example.ipynb).


## License
[MIT Licensed](LICENSE)

## Authors and acknowledgment
J.P. Vergnes and A. Manlay
