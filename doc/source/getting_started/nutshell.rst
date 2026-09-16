Gridmarthe in a nutshell
------------------------

.. warning::
    This section is under construction !

Objective
~~~~~~~~~

*gridmarthe* allow users to read/write efficiently Marthe Grids (v9, v8, constant_data, etc.)
with python, for any MARTHE variable.

With the *gridmarthe* API, data are stored in a `xarray dataset <https://docs.xarray.dev/en/stable/generated/xarray.Dataset.html#xarray.Dataset>`_,
and can be manage with `xarray <https://docs.xarray.dev/en/stable/>`_ functions (or `numpy <https://numpy.org/doc/stable/>`_).
Specific treatments/functions are also provided by `gridmarthe`.

The package also install different command line tools: ``ncmart`` to convert Marthe Grid to netCDF format,
``martshp`` to convert in shapefile/geopackage, ``cleanmgrid`` to fix marthe grid format.

Tutorials are available in the :ref:`userguide` section.


Grid convention
~~~~~~~~~~~~~~~

Grids are stored as a 2 dimension matrix, composed of a 1D spatial vector and a time dimension.
This means that the spatial domain is flatten in grid, and each point is associated
with a index, a x coordinate, a y coordinate, eventually a z coordinate (number of layer
in most cases), and dx,dy values.

Still, as Marthe meshes are always parallelepiped, the array stored by *gridmarthe* 
does *not* necessarily follow the `ugrid convention <https://ugrid-conventions.github.io/ugrid-conventions/>`_.
This may be an evolution for future version if required.

The x, and y coordinates are the center of cell. Dx, Dy are the dimension of the cell.

