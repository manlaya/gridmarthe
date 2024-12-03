Installation
------------

From conda
~~~~~~~~~~

If you are using conda (recommended installation process on Windows), you can 
install gridmarthe from conda-forge:

.. code-block:: bash
    
    conda install -c conda-forge gridmarthe


From the source
~~~~~~~~~~~~~~~

Get the sources:

.. code-block:: bash
    
    git clone https://gitlab.com/brgm/hydrogeological-modelling/marthe-tools/gridmarthe.git
    cd gridmarthe

Gridmarthe uses `Fortran` sources for efficient I/O operations on Marthe grid files.
These sources need to be compiled in order to use the `lecsem` module in `gridmarthe`.
The F90 sources are compiled with `f2py` (so make sure to have a compiler [`gfortran` 
for example], `make`, `python-numpy` and `python-charset_normalizer` installed on your system/python environment).
then, just use the Makefile provided to do the compilation process.

.. code-block:: bash
    
    make


Finally, you can install the package (in development mode if required):

.. code-block:: bash
    
    pip install [-e] .

At this point, the following command should not give any error:

.. code-block:: bash
    
    python3 -c "import gridmarthe"
