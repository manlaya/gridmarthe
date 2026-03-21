# --------------------------------- #
#           gridmarthe              #
#            Makefile               #
# --------------------------------- #
#####################################
#    ONLY FOR LINUX DEVELOP MODE    #
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
F90SRCDIR := $(MAINDIR)/src/gridmarthe/core

F90FILES  := $(F90SRCDIR)/lecsem/lecsem.f90 \
			 $(F90SRCDIR)/lecsem/edsemigl.f90 \
             $(F90SRCDIR)/utils/xy_dxdy.f90 \
			 $(F90SRCDIR)/flowdirect/analy_topo.f90 \
			 $(F90SRCDIR)/flowdirect/calc_direct_drainage.f90 \
			 $(F90SRCDIR)/flowdirect/num_8_voisins.f90 \
			 $(F90SRCDIR)/rivernetwork/Cal_reseau_hydro.f90 \
			 $(F90SRCDIR)/rivernetwork/Convert_Direct_Drain.f90 \
			 $(F90SRCDIR)/rivernetwork/Definit_Sous_Bassins.f90 \
			 $(F90SRCDIR)/rivernetwork/Dir_Drain_LigCol_Ava.f90 \
			 $(F90SRCDIR)/rivernetwork/Direct_Drain_Mai_Ava.f90 \
			 $(F90SRCDIR)/rivernetwork/Mai_Ava_Strahl_Surf_Drai.f90 \
			 $(F90SRCDIR)/rivernetwork/Mai_Exu_Surf_Drai.f90 \
			 $(F90SRCDIR)/rivernetwork/Verif_Surf_Stat_Hydro.f90 \
			 $(F90SRCDIR)/dessin/colle_segments.f90 \
			 $(F90SRCDIR)/modgridmarthe.f90
#######################

#Flags: Warning: flags significantly increase wall-clock and CPU time.
#Flags are primarily useful for initial check that code compiles correctly
F2PYOPT =--backend=meson --lower

# These flags are now only used when compiling shared library for testing
# NOT for install (editable or not): build opt are in meson.build
FFLAGS =
FFLAGS += -fdefault-real-8
# already O3 in f2py, change it here
# FFLAGS += -O2
# Position-Independent Code, si shared library, utile
FFLAGS += -fPIC
# FFLAGS += -shared  # => bug
FFLAGS += -ffree-line-length-none
# only gfortran > 12.0 :
FFLAGS +=-fallow-argument-mismatch
# legacy is not really necessary
# FFLAGS += -std=legacy

COMPILE = CC=$(CC) FC=$(FC) FFLAGS="$(FFLAGS)" $(F2PY) -c $(F90FILES) -m coremod $(F2PYOPT)

# ------------- Rules ------------- #

.PHONY: all doc clean requirements editable meson wheel sdist
all: clean editable

# only compile with f2py for develop purpose
lib: lecsem.so

doc:
	cd docs; $(MAKE) html

requirements:
	$(PY) -m pip install charset_normalizer numpy meson meson-python pytest

conda-req:
	mamba install charset-normalizer numpy meson meson-python pytest h5netcdf xarray pandas geopandas

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
editable:
	$(PY) -m pip install --no-build-isolation --no-deps \
		--config-settings=editable-verbose=true \
		--config-settings=setup-args='-Dpip_edit_mode=true' \
		--editable . \
		-vvv

meson:
	rm -rf build/ ; meson setup build; cd build; meson compile

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
