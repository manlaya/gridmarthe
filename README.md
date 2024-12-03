# Gridmarthe

Python project for (fast) Gridmarthe operations.

*THIS IS A BETA VERSION, improvements and documentation are needed.*


## gridmarthe in a nutshell

Full support of gridmarthe read operations by wrapping MARTHE fortran read/write modules,
allowing fast reading of marthe grid file (v9, v8, constant_data, etc.), for any variable.
Recent developpment also allow writting MartheGrid_v9.0 file.

In python, gridmarthe files are loaded using numpy and xarray libraries.

Some "utils" functions are also provided (plot_nested_grid, interp, etc.).

MARTHE is a hydrogeological modelling code developped at BRGM, French Geological Survey [[1]](#1).


## Installation

gridmarthe use Fortran module (partly from marthe source code, plus some specific developpement) which need
to be compiled before local installation.

### Compilation

On a linux machine, with gfortran, ninja-build, python3, numpy, meson, meson-python and charset_normalizer:

```bash
cd src/gridmarthe/lecsem
f2py -c lecsem.f90 edsemigl.f90 scan_grid.f90 -m lecsem --fcompiler=gfortran
```

On a windows machine, with gitbash, gfortran (mingw project https://mingw-w64.org/ ou https://winlibs.com/#download-release),
python (v3), numpy (version < 2.0) and charset_normalizer:

```bash
cd src/gridmarthe/lecsem
python setup.py build_ext --inplace --compiler=mingw32 --fcompiler=gnu95 -f
```



### pip install

Install the python package (optionnaly in developper/editable mode), back at package root directory:

```
pip install [-e] .
```

## Usage

A simple example can be found as a
[notebook](example/gm_example.ipynb).


## License
[GNU/GPL-V3 Licensed](LICENSE)

## Authors and acknowledgment
J.P. Vergnes and A. Manlay


## References

<a id="1">[1]</a> 
Thiery, D. (2020). Guidelines for MARTHE v7.8 computer code for
hydro-systems modelling (English version) (Report BRGM/RP-69660-FR; p. 246 p.)
 <http://ficheinfoterre.brgm.fr/document/RP-69660-FR>


