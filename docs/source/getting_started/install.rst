Installation
------------

From pip
~~~~~~~~

``gridmarthe`` is available on `PyPi <https://pypi.org/project/gridmarthe/>`_
and can be installed with:

.. code-block:: bash
    
    pip install gridmarthe
    # or with all optional dependencies
    pip install gridmarthe[opt]


From conda-forge (with conda or mamba)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``gridmarthe`` is also available in the `conda-forge <https://anaconda.org/conda-forge/gridmarthe>`_ channel.
Conda users can install it with:

.. code-block:: bash
    
    conda install gridmarthe
    # or, with mamba
    mamba install gridmarthe

It is also possible to search for available versions:

.. code-block:: bash

    mamba search gridmarthe --channel conda-forge



From the source
~~~~~~~~~~~~~~~

Get the sources:

.. code-block:: bash
    
    git clone https://gitlab.com/brgm/hydrogeological-modelling/marthe-tools/gridmarthe.git
    cd gridmarthe

Gridmarthe uses `Fortran` sources for efficient I/O operations on Marthe grid files.
These sources need to be compiled in order to use the `lecsem` module in ``gridmarthe``.
The F90 sources are compiled with ``f2py`` (so make sure to have a compiler [``gfortran`` 
for example] and ``make`` installed on your system/python environment).


With pip
^^^^^^^^

Then, for **developper mode** (ie *with editable flag*) just use the Makefile provided to do
the compilation process and python installation.

.. code-block:: bash
    
    make requirements
    make


Or, for a standard installation (*without editable flag*):

.. code-block:: bash
    
    pip install .


With conda (recommended on windows)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Alternatively, you can use a conda environment. For example with miniforge/mamba installed:

.. code-block:: bash
    
    mamba env create -n gm -f environment.yml
    mamba activate gm
    make

This will install the library using pip editable mode, but with dependencies
installed from conda-forge.

Alternatively, you can use `conda-build`:

.. code-block:: bash

    mamba env create -n gm -f environment.yml
    mamba activate gm
    mamba install conda-build
    # Compile fortran shared lib and python bindings
    make lib
    # add develop path
    conda develop src/


Verification
~~~~~~~~~~~~

At this point, the following command should not give any error:

.. code-block:: bash
    
    python3 -c "import gridmarthe"
