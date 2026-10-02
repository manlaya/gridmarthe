# --------------------------------- #
#           gridmarthe              #
#            Makefile               #
# --------------------------------- #
#####################################
#    ONLY FOR LINUX DEVELOP MODE    #
#####################################

# Use one shell for all commands - avoid the overhead of spawning a new shell
# for each command in targets. Also avoid the need for ";" or "&&" to chain
# commands (e.g. "cd dir/ && make").
# .ONESHELL:
# .SHELLFLAGS := -c
# Memo: prefer && to ; for cross platform (; not recognized by Windows)

# Default compilers, can be overridden by environment variables
# or by passing them to make: `make FC=flang CC=clang LD=lld`
FC := gfortran
CC := gcc
LD := ld
CPP := cpp

ifeq ($(OS), Windows_NT)
    PY := python
else
    PY := python3
endif

PIP := $(PY) -m pip
# switch to uv backend if present
ifneq (, $(shell which uv))
	PIP := uv pip
endif

F2PY = $(PY) -m numpy.f2py

###### SOURCES ########
# only for "lib" target, legacy build system without meson.build
MAINDIR := $(shell pwd)
F90SRCDIR := src/gridmarthe/core
# VPATH := $(F90SRCDIR)
F90FILES := \
	$(F90SRCDIR)/lecsem/lecsem.f90 \
	$(F90SRCDIR)/lecsem/edsemigl.f90 \
	$(F90SRCDIR)/utils/xy_dxdy.f90 \
	$(F90SRCDIR)/utils/adsuff.f90 \
	$(F90SRCDIR)/utils/colle_segments.f90 \
	$(F90SRCDIR)/flowdirect/analy_topo.f90 \
	$(F90SRCDIR)/flowdirect/calc_direct_drainage.f90 \
	$(F90SRCDIR)/flowdirect/num_8_voisins.f90 \
	$(F90SRCDIR)/rivernetwork/cal_reseau_hydro.f90 \
	$(F90SRCDIR)/rivernetwork/convert_direct_drain.f90 \
	$(F90SRCDIR)/rivernetwork/definit_sous_bassins.f90 \
	$(F90SRCDIR)/rivernetwork/dir_drain_ligcol_ava.f90 \
	$(F90SRCDIR)/rivernetwork/direct_drain_mai_ava.f90 \
	$(F90SRCDIR)/rivernetwork/mai_ava_strahl_surf_drai.f90 \
	$(F90SRCDIR)/rivernetwork/mai_exu_surf_drai.f90 \
	$(F90SRCDIR)/rivernetwork/verif_surf_stat_hydro.f90 \
	$(F90SRCDIR)/modgridmarthe.f90

F90PP = $(F90FILES:.f90=-cpp.f90)
#######################

#Flags: Warning: flags significantly increase wall-clock and CPU time.
#Flags are primarily useful for initial check that code compiles correctly
F2PYOPT :=--backend=meson --lower

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

PPFLAGS=-traditional -Wcomment -DENGLISH

COMPILE = CC=$(CC) FC=$(FC) FFLAGS="$(FFLAGS)" $(F2PY) -c $(patsubst $(F90SRCDIR)/%,%,$(F90PP)) -m coremod $(F2PYOPT)
ifeq ($(OS), Windows_NT)
	COMPILE = $(F2PY) -c $(patsubst $(F90SRCDIR)/%,%,$(F90PP)) -m coremod $(F2PYOPT)
endif
# memo with signature file:
# FC="$(FC)" FFLAGS="$(FFLAGS)" python -m numpy.f2py -c lecsem.pyf lecsem.f90 edsemigl.f90 scan_grid.f90 -m lecsem --backend=meson --lower

# ------------- Rules ------------- #

.PHONY: doc hook clean requirements editable meson wheel sdist
all: clean editable

# implicit rule for preproc
%-cpp.f90: %.f90
	$(CPP) -P $(PPFLAGS) $< -o $@

doc:
	cd docs; $(MAKE) html

hook:
	cat tools/hooks/check_uncommitted_test_data.sh >> .git/hooks/pre-commit

requirements:
	$(PIP) install charset_normalizer numpy meson meson-python pytest
	$(PIP) install -r pyproject.toml --extra dev  # --all-extras

conda-req:
	mamba install charset-normalizer numpy meson meson-python pytest h5netcdf xarray pandas geopandas

# legacy f2py CLI - Only for Linux (keep ";" here, because of "CC=")
# use of `cd` and not $(F90SRCDIR)/lecsem, because meson/f2py does not allow
# path separator in files
coremod.pyf: $(F90PP)
	cd "$(F90SRCDIR)" ; @echo "******** Generating signature ********" ; \
	$(F2PY) $^ -m coremod -h $@ $(F2PYOPT)

coremod.so: $(F90PP)
	cd "$(F90SRCDIR)" ; @echo "******** Building F2PY Library ********" ; \
 	$(COMPILE)

# only compile lib for develop purpose
lib: $(F90SRC)
	rm -rf build
	meson setup build -Dbuild_only_lib=true --prefix=$(MAINDIR)
	meson compile -C build
	meson install -C build
# memo: in install: --destdir=../ -> conflict with prefix
# which is required in linux, otherwise default is /usr/local

# meson editable for dev/testing
editable: requirements
	$(PIP) install --no-build-isolation --no-deps \
		--config-settings=editable-verbose=true \
		--config-settings=setup-args='-Dpip_edit_mode=true' \
		--editable . \
		-vvv

conda-dev: lib
	conda develop src

meson:
	rm -rf build/
	meson setup build
	cd build && meson compile

wheel:
	$(PIP) install build
	$(PY) -m build -w

sdist:
	$(PIP) install build
	$(PY) -m build -s

clean:
	rm -rf build/ builddir/ dist/
	cd $(F90SRCDIR) && \
	rm -f *.so *.o *.mod *.c *-cpp.f90 **/*-cpp.f90 *pywrappers* *.lib *.dll *.dll.a *.pyd
