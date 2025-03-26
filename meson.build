# ---------------------------------------------------------------- #
# ---------------------- Gridmarthe build ------------------------ #
# ---------------------------------------------------------------- #
# https://numpy.org/doc/stable/f2py/buildtools/meson.html          #
# ---------------------------------------------------------------- #

project('gridmarthe', ['fortran', 'c'],
  version : run_command('meson_get_version.py').stdout().strip(),
  license: 'GNU/GPL-V3',
  meson_version: '>=0.64.0',
  default_options : [
    'warning_level=1',
    'buildtype=release'
  ],
)

# add_languages('fortran')

# ----- Get compiler and build options ------ #
fc = meson.get_compiler('fortran')
cc = meson.get_compiler('c')
deps = []
inc_dir = []

# Options de compilation Fortran
fargs = []  # compile args
largs = []  # arg de link

if fc.get_id() == 'gcc'
  
  fargs += ['-fdefault-real-8']
  fargs += ['-O2', '-ffree-line-length-none']
  
  if cc.version().version_compare('>=13.0')
    fargs += ['-fallow-argument-mismatch', '-std=legacy']
  endif
  
  if host_machine.system() == 'windows'
    fargs += ['-fPIC', '-Wno-error']
    
    if not get_option('condabuild')
        largs += ['-static', '-static-libgfortran', '-static-libgcc', '-static-libquadmath']
    endif
    
    quadmath_dep = fc.find_library('quadmath', required: false) # from `f2py --build-dir` meson.build generation
    quadmath = declare_dependency(link_args : ['-lquadmath'])
    deps += [quadmath_dep,quadmath]
  else
      # fargs += ['-fPIC', '-shared'] # not really necessary here
  endif

elif fc.get_id() in ['llvm-flang', 'flang', 'flang-new']
  # TODO add options for llvm-flang for conda-forge
  fargs += ['-fdefault-real-8', '-ffree-form']
  
elif cc.get_id() in ['intel-llvm', 'intel', 'intel-llvm-cl', 'intel-cl']
  fargs += ['-real-size 64', '-stand f95']

else
  # 'msvc' ?
  error('Build is recommended with GCC/gfortran')

endif


fortran_args = fc.get_supported_arguments(fargs)
link_args = fc.get_supported_arguments(largs)
add_project_arguments(fortran_args, language: 'fortran')
add_project_link_arguments(link_args, language: 'fortran')

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

inc_dir += [inc_np,inc_f2py]


# --------   Compile sources   --------- #
subdir('src/gridmarthe/lecsem')
# subdir('src/gridmarthe/rivermod/draindir')
# subdir('src/gridmarthe/rivermod/rivernet')
# -------- Install pypackage ----------- #
install_subdir('src/gridmarthe', install_dir : python_install_dir)
