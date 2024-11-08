#!/bin/bash

# CLI interface to convert MartheGrid to netCDF
# Usage: `ncmart PATH_CHASIM PATH_PASTP [-o output] [-v varname]`

# ncmart -h
# ncmart ./data/chasim_hallue.out ./data/hallue.pastp
# ncmart ./data/chasim_hallue.out ./data/hallue.pastp -o hallue.nc
ncmart ./data/chasim_hallue.out ./data/hallue.pastp -o nc/hallue.nc
