Gridmarthe in a nutshell
------------------------

.. warning::
    This section is under construction !

``gridmarthe`` is a python library which allows users to read/write efficiently Marthe Grids (v9, v8, constant_data, etc.)
for any MARTHE variable.

With the ``gridmarthe`` API, data are stored in a `xarray dataset <https://docs.xarray.dev/en/stable/generated/xarray.Dataset.html#xarray.Dataset>`_,
and can be manage with `xarray <https://docs.xarray.dev/en/stable/>`_ (or `numpy <https://numpy.org/doc/stable/>`_)
functions as with "utils" functions provided by ``gridmarthe``.

The package also install a command line tool, ``ncmart`` to convert Marthe Grid to netCDF format.
Help can be found with ``ncmart -h``.

Tutorials are available in the :ref:`userguide` section.