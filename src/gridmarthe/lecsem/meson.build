lecsem_sources = files([
    './lecsem.f90',
    './edsemigl.f90',
    './scan_grid.f90'
])
lecsem_install_dir = 'gridmarthe/lecsem/'  # in python_install_dir

# -------- Building interface ----------- #
lecsem_interface = custom_target('lecsemmodule.c',
  input : lecsem_sources,
  output : ['lecsemmodule.c', 'lecsem-f2pywrappers.f', 'lecsem-f2pywrappers2.f90'],
  command : [py, '-m', 'numpy.f2py', '@INPUT@', '-m', 'lecsem', '--lower'],
  #install_dir: python_install_dir / lecsem_install_dir
)

py.extension_module('lecsem',
  [
    lecsem_sources,
    lecsem_interface,
    fortranobject_c
  ],
  include_directories: inc_dir,
  dependencies: deps,
  install: true,
  install_dir: python_install_dir / lecsem_install_dir,
  # fortran_args : fortran_args
)
