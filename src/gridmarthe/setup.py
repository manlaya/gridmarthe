# python .\setup.py build_ext --inplace --compiler=mingw32 --fcompiler=gnu95 -f
from numpy.distutils.core import Extension, setup

if __name__ == "__main__":
    setup(
        name="lecsem",
        ext_modules=[
            Extension("lecsem",
                      ["scan_grid.f90", "lecsem.f90"],
                      extra_compile_args=["-fdefault-real-8", "-fPIC"],
                      extra_link_args=["-static", "-static-libgfortran", "-static-libgcc"]
                      )
        ]
    )