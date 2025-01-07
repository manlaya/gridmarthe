Installation
------------

From pip
~~~~~~~~

`gridmarthe` is available on PyPi and can be installed with:

.. code-block:: bash
    
    pip install gridmarthe


From conda-forge (with conda or mamba)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Not yet available.


From the source
~~~~~~~~~~~~~~~

Get the sources:

.. code-block:: bash
    
    git clone https://gitlab.com/brgm/hydrogeological-modelling/marthe-tools/gridmarthe.git
    cd gridmarthe

Gridmarthe uses `Fortran` sources for efficient I/O operations on Marthe grid files.
These sources need to be compiled in order to use the `lecsem` module in `gridmarthe`.
The F90 sources are compiled with `f2py` (so make sure to have a compiler [`gfortran` 
for example] and `make` installed on your system/python environment).

Then, for **developper mode** (ie *with editable flag*) just use the Makefile provided to do the compilation process and python installation.

.. code-block:: bash
    
    make


Or, for a standard installation (*not with editable flag*):

.. code-block:: bash
    
    pip install .

Alternatively, you can use a conda environment. For example with miniforge/mamba installed:

.. code-block:: bash
    
    mamba env create -n gm -f environment.yml
    mamba activate gm
    pip install --no-deps .

or with developper mode in conda:

.. code-block:: bash

    mamba env create -n gm -f environment.yml
    mamba activate gm
    cd src/gridmarthe/lecsem
    f2py -c lecsem.f90 edsemigl.f90 scan_grid.f90 -m lecsem --backend=meson --lower
    cd ../../../
    conda develop .


At this point, the following command should not give any error:

.. code-block:: bash
    
    python3 -c "import gridmarthe"
