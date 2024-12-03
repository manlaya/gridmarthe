# --------------------------------- #
#           gridmarthe              #
#            Makefile               #
# --------------------------------- #

FC := gfortran
CC := gcc

# editable
PIPFLAGS ?= #-e

#Flags: Warning: flags significantly increase wall-clock and CPU time.
#Flags are primarily useful for initial check that code compiles correctly
F2PYFLAGS :=
F2PYOPT := --backend=meson --lower

###### SOURCES ########
MAINDIR := $(shell pwd)
F90SRCDIR := $(MAINDIR)/src/gridmarthe/lecsem
F90FILES := lecsem.f90 edsemigl.f90 scan_grid.f90
#######################

# OS Spec
ifeq ($(OS), Windows_NT)
    # FC := mingw32
    # on windows, python use a specific version of MSC.
    # Distutils link the appropriate msvcrXX.dll automatically whereas f2py does not.
    # It need to bee linked manually : http://scipy.github.io/old-wiki/pages/F2PY_Windows.html
    # help: https://stackoverflow.com/questions/20092983/version-of-msvcrxx-dll-that-my-python-interpereter-compiles-with
    # MSV = $(shell python -c "import sys, platform, re; vers=re.search('v\.[0-9]{4}', platform.python_compiler()).group(0);print(vers.strip('v.'))")
    # F2PYOPT :=--compiler=mingw32 --fcompiler=gnu95 --backend=distutils -lmsvcr$(MSV)
    # edit, on windows, just use distutils in setup.py ; will not work after py3.12 (distutils deprecation)...
    F2PYFLAGS +=-fdefault-real-8 -fPIC -Wno-error -static -static-libgfortran -static-libgcc
    PY := python
    F2PY = $(PY) -m numpy.f2py
    COMPILE = $(PY) setup.py build_ext --inplace --compiler=mingw32 --fcompiler=gnu95 -f
else
    # FC := gfortran
    F2PYFLAGS +=-static -fdefault-real-8
    PY := python3
    F2PY = $(PY) -m numpy.f2py
    COMPILE = CC=$(CC) FC=$(FC) FFLAGS="$(F2PYFLAGS)" $(F2PY) -c $(F90FILES) -m lecsem $(F2PYOPT)
endif


# ---- Rules ---- #

.PHONY: all docs clean requirements
all: install


docs:
	echo "TODO: make a doc"


# install: requirements lecsem.pyf lecsem.so
install: requirements lecsem.so
	# $(PY) -m pip install $(PIPFLAGS) .

requirements:
	$(PY) -m pip install charset_normalizer numpy #==1.26 #--user

lecsem.pyf:
	cd $(F90SRCDIR); echo "******** Generating signature ********"; \
	$(F2PY) $(F90FILES) -m lecsem -h $@ $(F2PYOPT)

lecsem.so:
	cd $(F90SRCDIR); echo "******** Building F2PY Library ********"; \
	$(COMPILE)
	cd $(MAINDIR)
    # use of `cd` and not $(F90SRCDIR)/lecsem, even if not a good practice in Makefile, 
    # because meson/f2py does not allow path separator in files.
	# FC="$(FC)" FFLAGS="$(F2PYFLAGS)" python -m numpy.f2py -c lecsem.pyf lecsem.f90 edsemigl.f90 scan_grid.f90 -m lecsem --backend=meson --lower

clean:
	cd $(F90SRCDIR); \
	rm -f *.so *.dll *.pyd *.o *.mod *.c *pywrappers*
	cd $(MAINDIR)

