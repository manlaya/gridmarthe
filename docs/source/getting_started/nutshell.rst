Gridmarthe in a nutshell
------------------------

.. warning::
    This section is under construction !

``gridmarthe`` allow users to read/write efficiently Marthe Grids (v9, v8, constant_data, etc.)
with python, for any MARTHE variable.

With the ``gridmarthe`` API, data are stored in a `xarray dataset <https://docs.xarray.dev/en/stable/generated/xarray.Dataset.html#xarray.Dataset>`_,
and can be manage with `xarray <https://docs.xarray.dev/en/stable/>`_ functions (or `numpy <https://numpy.org/doc/stable/>`_).
Specific treatments/functions are also provided by `gridmarthe`.

The package also install different command line tools: `ncmart` to convert Marthe Grid to netCDF format,
`martshp` to convert in shapefile/geopackage, `cleanmgrid` to fix marthe grid format.

Tutorials are available in the :ref:`userguide` section.