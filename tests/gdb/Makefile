CPP=cpp
FC=gfortran
# PPFLAGS=-DPROJECT_VERSION=v8.0dev
PPFLAGS=-traditional -Wcomment -DENGLISH
FFLAGS ?=-g -O0 -Wall -fdefault-real-8 -ffixed-line-length-none
# FFLAGS ?=-O3 -fdefault-real-8

# CLI define, e.g: make; make gdb BREAK=modgridmarthe-cpp.f90:428
BREAK ?= 'modgridmarthe-cpp.f90:271'

# test netCDF lib
# INC := -I/usr/include
# LD_FLAGS := -L/usr/lib
# FFLAGS += -lnetcdff $(INC) $(LD_FLAGS)

SRCDIR = ../../src/gridmarthe/core/
SRC  := \
	lecsem/lecsem.f90 \
	lecsem/edsemigl.f90 \
	utils/xy_dxdy.f90 \
	utils/adsuff.f90 \
	utils/colle_segments.f90 \
	flowdirect/num_8_voisins.f90 \
	flowdirect/analy_topo.f90 \
	flowdirect/calc_direct_drainage.f90 \
	rivernetwork/cal_reseau_hydro.f90 \
	rivernetwork/convert_direct_drain.f90 \
	rivernetwork/definit_sous_bassins.f90 \
	rivernetwork/dir_drain_ligcol_ava.f90 \
	rivernetwork/direct_drain_mai_ava.f90 \
	rivernetwork/mai_ava_strahl_surf_drai.f90 \
	rivernetwork/mai_exu_surf_drai.f90 \
	rivernetwork/verif_surf_stat_hydro.f90 \
	modgridmarthe.f90

# OBJ = $(SRC:.f90=.o)
# OBJ := $(notdir $(SRC:.f90=.o))
OBJ = $(SRC:.f90=-cpp.f90)

VPATH = $(SRCDIR)  # tell make to look into that dir

MAIN=readgrid.f90
PROG=greader

.PHONY: all clean
all: $(PROG)

# memo https://www.gnu.org/software/make/manual/html_node/Automatic-Variables.html
# https://www.gnu.org/software/make/manual/html_node/File-Name-Functions.html
# $@ : target, la cible qui doit être générée, $(@F) file $(@D) directory
# $< : premier prérequis
# $^ : tous les prérequis, sans doublons
# implicit rule to transform .f90 into -cpp.f90
%-cpp.f90: %.f90
	$(CPP) -P $(PPFLAGS) $< -o $(@F)

%.o : %-cpp.f90
	$(FC) -c $< $(FFLAGS)

$(PROG): $(OBJ)
	$(FC) $(^F) $(MAIN) -o $@ $(FFLAGS)

# https://stackoverflow.com/questions/6121094/how-do-i-run-a-program-with-commandline-arguments-using-gdb-within-a-bash-script
gdb: $(PROG)
	gdb --ex='break $(BREAK)' --args $(PROG)

# mute with @ at beginning of command
.SILENT: clean
clean:
	@rm *.mod *.o *-cpp.f90 test-*
