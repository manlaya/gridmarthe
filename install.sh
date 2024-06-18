#! /bin/bash

PACKAGEDIR=$PWD

# create venv
# python3 -m venv ./.venv/gm
# source ./.venv/gm/bin/activate

# compile Fortran module
pip install charset_normalizer numpy --user
cd src/gridmarthe/lecsem

if [[ $OSTYPE = "linux-gnu" ]]; then
    f2py -c lecsem.f90 edsemigl.f90 scan_grid.f90 -m lecsem
elif [[ $OSTYPE = "msys" ]]; then
    echo "Warning! on windows machine, gfortran (mingw) path need to be in %PATH%"
    python setup.py build_ext --inplace --compiler=mingw32 --fcompiler=gnu95 -f
else
    echo "Compilation supported by this script can only be performed on GNU/Linux or Windows"
    exit 1
fi

# install python package
cd $PACKAGEDIR
pip install -e .
