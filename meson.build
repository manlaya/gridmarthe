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
    'src/gridmarthe/lecsem/lecsem.f90',
    'src/gridmarthe/lecsem/edsemigl.f90',
    'src/gridmarthe/lecsem/scan_grid.f90'
])
lecsem_install_dir = 'gridmarthe/lecsem/' # in python_install_dir

# ----- Get compiler and build options ------ #
fc = meson.get_compiler('fortran')
cc = meson.get_compiler('c')
deps = []

# Options de compilation Fortran
largs = []
if fc.get_id() == 'gcc'
  largs += ['-fdefault-real-8', '-fPIC', '-O3', '-ffree-line-length-none']
  if cc.version().version_compare('>=13.0')
    largs += ['-fallow-mismatch-argument', '-std=legacy']
  endif
  if host_machine.system() == 'windows'
    largs += ['-static', '-static-libgfortran', '-static-libgcc', '-lquadmath']
    quadmath_dep = fc.find_library('quadmath', required: false) # from `f2py --build-dir` meson.build generation
    # quadmath = declare_dependency(link_args : ['-lquadmath'])
    deps += [quadmath_dep] #,quadmath
  endif
elif fc.get_id() in ['llvm-flang', 'flang', 'flang-new']
  # TODO add options for llvm-flang for conda-forge
  largs += ['-std=legacy']
  add_project_link_arguments('-Wl,-rpath=/d/miniforge/envs/llvm/Library/bin/lld')
  # error('flang not yet supported')
# elif cc.get_id() in ['msvc', 'intel-llvm', 'intel', 'intel-llvm-cl', 'intel-cl']
else
  error('Build is recommended with GCC/gfortran')
endif

fortran_args = fc.get_supported_arguments(largs)

# ----- Get Python linked ------ #
py = import('python').find_installation(pure: false)
py_dep = py.dependency()
python_install_dir = py.get_install_dir()

deps += [py_dep]


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
  dependencies: deps,
  install: true,
  install_dir: python_install_dir / lecsem_install_dir,
  fortran_args : fortran_args,
  # override_options : ['fortran_std=none']
)

# -------- Install pypackage ----------- #
install_subdir('src/gridmarthe', install_dir : python_install_dir)
