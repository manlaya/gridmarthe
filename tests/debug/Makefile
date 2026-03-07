CPP=cpp
FC=gfortran
# PPFLAGS=-DPROJECT_VERSION=v8.0dev
PPFLAGS=
FFLAGS ?=-g -O0 -Wall -fdefault-real-8
# FFLAGS ?=-O3 -fdefault-real-8

# test netCDF lib
# INC := -I/usr/include
# LD_FLAGS := -L/usr/lib
# FFLAGS += -lnetcdff $(INC) $(LD_FLAGS)

SRCDIR = ../../src/gridmarthe/core/
SRC = \
	lecsem/lecsem.f90 \
	lecsem/edsemigl.f90 \
	utils/xy_dxdy.f90 \
	flowdirect/num_8_voisins.f90 \
	flowdirect/analy_topo.f90 \
	flowdirect/calc_direct_drainage.f90 \
	modgridmarthe.f90

# OBJ = $(SRC:.f90=.cpp.f90)
OBJ = $(SRC:.f90=.o)

VPATH = $(SRCDIR)  # tell make to look into that dir

PROG=readgrid.f90

.PHONY: all clean
all: test-read

# memo https://www.gnu.org/software/make/manual/html_node/Automatic-Variables.html
# https://www.gnu.org/software/make/manual/html_node/File-Name-Functions.html
# $@ : target, la cible qui doit être générée, $(@F) file $(@D) directory
# $< : premier prérequis
# $^ : tous les prérequis, sans doublons
# implicit rule to transform .f90 into .cpp.f90
# no cpp here
# %.cpp.f90: %.f90
# 	$(CPP) -P $(PPFLAGS) $< -o $@

%.o : %.f90
	$(FC) -c $< $(FFLAGS)

test-read: $(OBJ)
	$(FC) $(^F) $(PROG) -o $@ $(FFLAGS)

# https://stackoverflow.com/questions/6121094/how-do-i-run-a-program-with-commandline-arguments-using-gdb-within-a-bash-script
gdb: test-read
	gdb --ex='break modgridmarthe.f90:271' --args ./test-read

# mute with @ at beginning of command
.SILENT: clean
clean:
	@rm *.mod *.o test-* $(OBJ)
