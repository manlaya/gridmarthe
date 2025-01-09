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

Full documentation can be founded at https://gridmarthe.readthedocs.io

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


MacOS:

```bash
brew install gcc gfortran
```


### From sources

`gridmarthe` use some Fortran modules which need
to be compiled before local installation.

#### Compilation and installation

Get the sources :

```bash
git clone https://gitlab.com/brgm/hydrogeological-modelling/marthe-tools/gridmarthe
cd gridmarthe
```

##### With pip (Unix-like OS)

On a Unix-like machine, with gfortran, ninja-build, python3, the project `Makefile` will compile Fortran sources and install
**in development mode** the package.

```bash
make
```

or, without the development mode :

```bash
pip install .
```

On a windows machine, it is possible to compile with gfortran
(mingw project https://mingw-w64.org/ or https://winlibs.com/#download-release ; or `choco install mingw`).
Neverless, the simpliest way is to use a conda environment (miniforge with mambalib is recommended) to install gcc/gfortran,
and install the project.

##### With conda (recommended on Windows)

It is also possible to install gridmarthe in a conda environment. An environment file is provided (example with mamba):

```bash
mamba env create -n gm -f environment.yml
mamba activate gm
pip install --no-deps .
```

Here, the development mode is *not* available (yet, with the meson build).
One can add the `-e` flag in pip command, or use `conda-build`:

```bash
mamba env create -n gm -f environment.yml
mamba activate gm
mamba install conda-build
make lib
conda develop src/
```


## Usage

Simple examples can be found in the 
[documentation](https://gridmarthe.readthedocs.io/en/stable/user_guide/index.html).


## License

This software is open-source and released under the GNU General Public License (v3+) [GNU/GPL-V3 Licensed](LICENSE).


## Authors and acknowledgment
J.P. Vergnes and A. Manlay


## References

<a id="1">[1]</a> 
Thiery, D. (2020). Guidelines for MARTHE v7.8 computer code for
hydro-systems modelling (English version) (Report BRGM/RP-69660-FR; p. 246 p.)
 <http://ficheinfoterre.brgm.fr/document/RP-69660-FR>


