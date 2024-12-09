# ---------------------------------------------------------------- #
# ---------------------- Gridmarthe build ------------------------ #
# ---------------------------------------------------------------- #
# https://numpy.org/doc/stable/f2py/buildtools/meson.html          #
# ---------------------------------------------------------------- #

project('gridmarthe', ['fortran', 'c'],
  version : '0.1.1',
  license: 'MIT',
  meson_version: '>=0.64.0',
  default_options : [
    'warning_level=1',
    'buildtype=release'
  ],
)

# add_languages('fortran')
# subdir('src/gridmarthe')

fortran_sources = files([
    'src/gridmarthe/martsem/lecsem.f90',
    'src/gridmarthe/martsem/edsemigl.f90',
    'src/gridmarthe/martsem/scan_grid.f90'
])

# ----- Get compiler and build options ------ #
fc = meson.get_compiler('fortran')
cc = meson.get_compiler('c')

# Options de compilation Fortran
# fortran_args = [
#     '-fdefault-real-8', '-fPIC', '-Wno-error', 
#     '-static', '-static-libgfortran', '-static-libgcc'
# ]

# TODO faire en fonction du compilateur et de la platform
fortran_args = fc.get_supported_arguments(['-fdefault-real-8', '-fPIC', '-O3', '-ffree-line-length-none'])

py = import('python').find_installation(pure: false)
py_dep = py.dependency()
python_install_dir = py.get_install_dir()

incdir_numpy = run_command(py,
  ['-c', 'import os; os.chdir(".."); import numpy; print(numpy.get_include())'],
  check : true
).stdout().strip()

# incdir_f2py = run_command(py,
#     ['-c', 'import os; os.chdir(".."); import numpy.f2py; print(numpy.f2py.get_include())'],
#     check : true
# ).stdout().strip()

# inc_np = include_directories(incdir_numpy, incdir_f2py)
inc_np = include_directories(incdir_numpy)
np_dep = declare_dependency(include_directories: inc_np)

incdir_f2py = incdir_numpy / '..' / '..' / 'f2py' / 'src'
inc_f2py = include_directories(incdir_f2py)
fortranobject_c = incdir_f2py / 'fortranobject.c'

# -------- Building interface ----------- #
lecsem_interface = custom_target('lecsemmodule.c',
  input : fortran_sources,
  output : ['lecsemmodule.c', 'lecsem-f2pywrappers.f', 'lecsem-f2pywrappers2.f90'],
  command : [py, '-m', 'numpy.f2py', '@INPUT@', '-m', 'lecsem', '--lower']
)


py.extension_module('lecsem',
  [
    fortran_sources,
    lecsem_interface,
    fortranobject_c
  ],
  include_directories: [inc_np,inc_f2py],
  dependencies: [py_dep],
  install: true,
  install_dir: python_install_dir / 'gridmarthe/martsem/',
  fortran_args : fortran_args,
  # dependencies : [fc],
  # override_options : ['fortran_std=none']
)

# -------- Install pypackage ----------- #
install_subdir('src/gridmarthe', install_dir : python_install_dir)
