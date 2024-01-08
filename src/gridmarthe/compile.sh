# windows
# f2py -c lecsem.f90 scan_grid.f90 -m lecsem --compiler=mingw32 # --fcompiler=gnu95 -f
# non sous windows, utiliser le setup de JPV, avec
# python setup.py build_ext --inplace --compiler=mingw32 --fcompiler=gnu95 -f

# linux
# mémo 2023 : attention à installer numpy via pip et non apt python3-numpy (la version est trop ancienne <= 2021)
f2py -c lecsem.f90 scan_grid.f90 -m lecsem #--fcompiler=gfortran --f90flags="-static -O2"