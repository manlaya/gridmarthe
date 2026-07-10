#!/bin/bash

# CLI interface to convert MartheGrid to netCDF
# Usage: `ncmart PATH_CHASIM PATH_PASTP [-o output] [-v varname]`

# ncmart -h
ncmart ./data/chasim_hallue.out ./data/hallue.pastp -o tmp_outputs/hallue.nc -x 1000
# ncmart ./data/chasim_hallue.out ./data/hallue.pastp -o nc/hallue.nc -x 1000 -v all
if [[ $? -ne 0 ]]; then
    echo "Test for ncmart script failed"
    exit 1
fi
