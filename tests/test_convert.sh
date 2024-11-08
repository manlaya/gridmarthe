#!/bin/bash

# CLI interface to convert MartheGrid to netCDF
# Usage: `chasim2nc PATH_CHASIM PATH_PASTP [-o output] [-v varname]`

# chasim2nc -h
# chasim2nc ./data/chasim_hallue.out ./data/hallue.pastp
# chasim2nc ./data/chasim_hallue.out ./data/hallue.pastp -o hallue.nc
chasim2nc ./data/chasim_hallue.out ./data/hallue.pastp -o nc/hallue.nc
