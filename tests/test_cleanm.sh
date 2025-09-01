#!/bin/bash

cleanmgrid -h
cleanmgrid data/grid_wrong_attrs.hsubs -l 1 -g 3
if [[ $? -ne 0 ]]; then
    echo "Test for cleanmgrid script failed"
    exit 1
fi
