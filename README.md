# Gridmarthe

Python project for (fast) Marthe grid operations.
MARTHE is a hydrogeological modelling code developped at BRGM, French Geological Survey [[1]](#1),
and is available at https://www.brgm.fr/en/software/marthe-modelling-software-groundwater-flows


**THIS IS A BETA VERSION, under development.**


## gridmarthe in a nutshell

`gridmarthe` allow users to read/write efficiently Marthe Grids (v9, v8, constant_data, etc.)
for any MARTHE variable.

With the `gridmarthe` API, data are stored in a `xarray` dataset, and can be manage with
`xarray` (or `numpy`) functions as with "utils" functions provided by `gridmarthe`.

The package also install a command line tool, `ncmart` to convert Marthe Grid to netCDF format.
Help can be found with `ncmart -h`.



## Installation

### From pip


On pip, `gridmarthe` is available for GNU/Linux, macOS and Windows for python >=3.10.
Users can install it with:

```
pip install gridmarthe
```

For GNU/Linux and MacOS, the package needs gfotran/gcc to run.

Linux, example with debian/ubuntu:
```bash
sudo apt install gcc gfortran
```

```

MacOS:

```bash
brew install gcc gfortran
```

### From conda-forge

not yet, see : https://github.com/conda-forge/staged-recipes/pull/28277


### From sources

`gridmarthe` use some Fortran modules which need
to be compiled before local installation.

#### Compilation and installation

Get the sources :

```bash
git clone https://gitlab.com/brgm/hydrogeological-modelling/marthe-tools/gridmarthe
cd gridmarthe
```

##### Unix-like OS

On a Unix-like machine, with gfortran, ninja-build, python3, the project `Makefile` will compile Fortran sources and install
**in development mode** the package.

```bash
make
```

or, without the development mode :

```bash
pip install .
```

##### Windows

On a windows machine, it is possible to compile gfortran (mingw project https://mingw-w64.org/ or https://winlibs.com/#download-release).
Neverless, the simpliest way is to use a conda environment (miniforge with mambalib is recommended) to install gcc/gfortran,
and install the project :

```bash
mamba env create -n gm -f environment.yml
mamba activate gm
pip install --no-deps .
```

Here, the development mode is *not* available (yet, with the meson build).


For now, to install in development mode, with *Windows/conda*, you can also compile manually :
```bash
mamba env create -n gm -f environment.yml
mamba activate gm
cd src/gridmarthe/lecsem
f2py -c lecsem.f90 edsemigl.f90 scan_grid.f90 -m lecsem --backend=meson --lower
cd ../../../
conda develop .
```


## Usage

Simple examples can be found as 
[notebook](https://gridmarthe.readthedocs.io/en/stable/user_guide/index.html).


## License

[GNU/GPL-V3 Licensed](LICENSE)


## Authors and acknowledgment
J.P. Vergnes and A. Manlay


## References

<a id="1">[1]</a> 
Thiery, D. (2020). Guidelines for MARTHE v7.8 computer code for
hydro-systems modelling (English version) (Report BRGM/RP-69660-FR; p. 246 p.)
 <http://ficheinfoterre.brgm.fr/document/RP-69660-FR>


