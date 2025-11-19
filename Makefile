# --------------------------------- #
#           gridmarthe              #
#            Makefile               #
# --------------------------------- #
#####################################
#    ONLY FOR LINUX DEVELOP MODE    #
#        OR CONDA SRC INSTALL       #
#####################################

FC := gfortran
CC := gcc

ifeq ($(OS), Windows_NT)
    PY := python
else
    PY := python3
endif

F2PY = $(PY) -m numpy.f2py

###### SOURCES ########
MAINDIR := $(shell pwd)
F90SRCDIR := $(MAINDIR)/src/gridmarthe/lecsem
F90FILES  := lecsem.f90 edsemigl.f90 scan_grid.f90
#######################

# editable
PIPFLAGS ?= -e
#Flags: Warning: flags significantly increase wall-clock and CPU time.
#Flags are primarily useful for initial check that code compiles correctly
F2PYOPT =--backend=meson --lower

# These flags are now only used when compiling shared library
# NOT for install (editable or not): build opt are in meson.build
FFLAGS = 
FFLAGS += -fdefault-real-8
# already O3 in f2py, change it here
# FFLAGS += -O2 
# Position-Independent Code, si shared library, utile
FFLAGS +=-fPIC -shared
FFLAGS += -ffree-line-length-none
# only gfortran > 12.0
FFLAGS +=-fallow-argument-mismatch
# legacy is not really necessary ?
FFLAGS += -std=legacy


COMPILE = CC=$(CC) FC=$(FC) FFLAGS="$(FFLAGS)" $(F2PY) -c $(F90FILES) -m lecsem $(F2PYOPT)


# ------------- Rules ------------- #

.PHONY: all docs clean requirements wheel
# all: clean install bakup_pyproj
all: clean editable

# only compile with f2py for develop purpose
lib: lecsem.so


doc:
	cd docs; $(MAKE) html

# deprecated
# setuptools: pyproject.toml
# 	cp pyproject.toml pyproject.bak ; sed -i '16s/# //' pyproject.toml ; sed -i '17s/^/# /' pyproject.toml
#     # change to setuptools for editable version
# 
# bakup_pyproj: pyproject.toml
# 	mv pyproject.bak pyproject.toml
#     # format pyproject.{toml,bak} non accepté par make ?

requirements:
	$(PY) -m pip install charset_normalizer numpy meson meson-python

#install: requirements lecsem.so setuptools bakup_pyproj
#	$(PY) -m pip install $(PIPFLAGS) . -vvv

lecsem.pyf:
	cd $(F90SRCDIR); echo "******** Generating signature ********"; \
	$(F2PY) $(F90FILES) -m lecsem -h $@ $(F2PYOPT)

lecsem.so:
	cd $(F90SRCDIR); echo "******** Building F2PY Library ********"; \
	$(COMPILE)
	
# use of `cd` and not $(F90SRCDIR)/lecsem, even if not a good practice in Makefile, 
# because meson/f2py does not allow path separator in files.
# FC="$(FC)" FFLAGS="$(FFLAGS)" python -m numpy.f2py -c lecsem.pyf lecsem.f90 edsemigl.f90 scan_grid.f90 -m lecsem --backend=meson --lower

# meson editable for dev/testing
editable: #requirements
	$(PY) -m pip install --no-build-isolation \
		--config-settings=editable-verbose=true \
		--config-settings=setup-args='-Dpip_edit_mode=true' \
		--editable . \
		-vvv

wheel:
	$(PY) -m pip install build
	$(PY) -m build -w

sdist:
	$(PY) -m pip install build
	$(PY) -m build -s

clean:
	cd $(F90SRCDIR); \
	rm -f *.so *.o *.mod *.c *pywrappers* *.dll *.pyd ; \
	cd $(MAINDIR)

