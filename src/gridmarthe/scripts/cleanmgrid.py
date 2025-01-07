#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# objectif, lire l'ensemble des fichiers maillés et les corriger.
# sinon, a minima le permh

import os, sys, re, shutil
from pathlib import Path


MARTGRID_FILES = {
    # ext: VARIABLE_NAME
    'topog' : 'H_TOPOGR',
    'hsubs' : 'H_SUBSTRAT',
    'permh' : 'PERMEAB',
    'perm_r': 'PERM_LIT_RIVI',
    'anisv' : 'ANISO_VERTI',
    'anish' : 'ANISO_HORIZ',
    'emmli' : 'EMMAG_LIBR',
    'emmca' : 'EMMAG_CAPT',
    'idebo' : 'IND_DEBORD',
    'charg' : 'CHARGE',
    'debit' : 'DEBIT', 
    'aff_r' : 'AFFLU_RIVI',
    'flo_r' : 'DEBIT_RIVI',
    'fon_r' : 'FOND_RIVI',
    'hau_r' : 'HAUTEU_RIVI',
    'lar_r' : 'LARG_RIVI',
    'lon_r' : 'LONG_RIVI',
    'trc_r' : 'TRONC_RIVI',
    'qext_r': 'Q_EXTER_RIVI',
    'd_ava' : 'DIRECT_AVAL',# Q_AMONT_RIVI, EPAI_LIT_RIV, RUGOS_RIVI, PENTE_RIVI
    'meteo' : 'ZONE_METEO',
    'zonep' : 'ZONE_SOL',
    'zgeom' : 'ZONE_GEOM',
    'zoneg2': 'ZONE_2',
    'zoneg3': 'ZONE_3',
    # 'ZONE_CULTUR'
}

def print_help():
    msg = """ Usage: 
    `cleanmgrid PATH_TO_RMA`
    
    PATH_TO_RMA can be a relative path, need to end with '.rma'

    Only works for marthe grid v9.0 (a check is performed and <v9 are skipped)
    """
    print(msg)

def fread(file:str):
    with open(file, 'r', encoding='ISO-8859-1') as f:
        content = f.read()
    return content

def scan_vers_semi(str_semi):
    if re.search(r'Marthe_Grid.*Version=9\.0', str_semi):
        version = 9.0
    elif re.search(r'Semis.*8\.0', str_semi):
        version = 8.0
    else:
        print('Unknown Marthe Grid version.')
        version = 9999.
    return version

def parse_geom(layer_str:str):
    layers = re.findall(r'Cou=\s*(\d+);', layer_str)
    ngrid  = re.findall(r'(\d+)=Nombre.*[g|G]igognes', layer_str)[0]
    # nlay = max(map(int, layers))
    return layers, ngrid

def read_rma(frma):
    rma = fread(frma)
    files = re.finditer('(.*)  =\s+[A-z]', rma)
    files = [ x.group(1).strip().replace('=', '') for x in files]
    files = [ x for x in files if len(x) > 0]
    return files

def read_files_from_rma(frma):
    
    # root = os.path.dirname(frma)
    root = os.getcwd()
    files = read_rma(frma)
    
    # get all gridded files
    res = []
    for fgrid in files:
        # files[fgrid] = re.findall(r'(.*\.[A-z]*) *=.*Perméabilité', rma)[0],
        kind = os.path.splitext(fgrid)[-1].replace('.', '')
        if kind in MARTGRID_FILES.keys():
            res.append((kind, fgrid, MARTGRID_FILES.get(kind)))
    
    # get layers, ngrid infos
    layer =  [x for x in files if x.endswith('layer')][0]
    layer =  fread("{}/{}".format(root, layer))
    layers, ngrid = parse_geom(layer)
    return res, layers, ngrid

def insert_str(string, index, insert_str):
    return string[:index] + insert_str + string[index:]

def search_index(string, pattern):
    # get research start, match end, research pattern and result
    idx = [(m.start(0), m.end(1), m.group(0).replace(m.group(1), ''), m.group(1)) for m in re.finditer(pattern, string)]
    return idx

def clean_grid_str(string: str, pattern: str, fillvalue: str|list, test=lambda x: len(x) < 1):
    """ Search for a pattern and replace with a unique or varying value
    if match satisfy a custom test
    """
    matches = search_index(string, pattern)
    new_str = string
    
    if len(matches) == 0:
        # nothing to clean // or bug with regex :)
        return new_str

    if isinstance(fillvalue, list):
        if len(fillvalue) != len(matches):
            raise ValueError('Length for fillvalue and match differs. Cannot replace with fillvalues')

    if test(matches[0][-1]):
        if isinstance(fillvalue, list):
            # sub one by one
            for match, fill in zip(matches, fillvalue):
                before = new_str[:match[0]]
                after = new_str[match[0]:]
                after = re.sub(pattern, '{}{}'.format(match[2], str(fill)), after, count=1)
                new_str = before + after
        else:
            # unique value, sub all at once
            new_str = re.sub(pattern, '{}{}'.format(matches[0][2], fillvalue), new_str)
    return new_str

def write_res(string, fname):
    with open(f'{str(fname)}', 'w', encoding='ISO-8859-1') as f:
        f.write(string)
    return 0

def parse_args():
    if len(sys.argv) < 2:
        print('cleanmgrid NO argument were passed')
        print_help()
        sys.exit(1)
    frma  = sys.argv[1]
    if frma in ['h', '-h', '--help'] or not frma.endswith('rma'):
        print_help()
        sys.exit(1)
    return frma

def main():
    frma = parse_args()
    # root = os.path.dirname(frma) # edit no, if not ./MONMODEL.rma but MONMODEL.rma, dirname is '' so /bakup => not allowed in linux non root
    root = os.getcwd()
    os.makedirs('{}/bakup'.format(root), exist_ok=True)
    files, layers, ngrid = read_files_from_rma(frma)
    for ext, file, key in files:
        fpath = Path(root, file)
        grid = fread(fpath)
        version = scan_vers_semi(grid)
        if version != 9.0:
            continue
        grid = clean_grid_str(grid, r'\nField=(.?)', key, test=lambda x: len(x) < 1 )
        grid = clean_grid_str(grid, pattern=r'\nLayer=([0-9]*)'  , fillvalue=layers * (int(ngrid)+1)   , test=lambda x: int(x) == 0)
        grid = clean_grid_str(grid, pattern=r'Max_Layer=([0-9]*)', fillvalue=str(max(map(int, layers))), test=lambda x: int(x) == 0)
        # grid = clean_grid_str(grid, pattern=r'Nest_grid=([0-9]*)', fillvalue=list(range(int(ngrid)+1)) , test=lambda x: int(x) == 0) # in multilayer not good, miss repetition of layers
        x = [item for item in list(range(int(ngrid)+1)) for _ in range(max(map(int,layers)))] # equiv of np.repeat
        grid = clean_grid_str(grid, pattern=r'Nest_grid=([0-9]*)', fillvalue=x, test=lambda x: int(x) == 0)
        grid = clean_grid_str(grid, pattern=r'Max_NestG=([0-9]*)', fillvalue=ngrid                     , test=lambda x: int(x) == 0)
        grid = clean_grid_str(grid, pattern=r'Time=([0-9]*\.[0-9]*E[|\-|\+][0-9]*)', fillvalue='0', test=lambda x: float(x) != 0)
        shutil.copy(fpath, Path(root, 'bakup', file))
        write_res(grid, fpath)
    return 0


if __name__ == '__main__':
    
    status = main()
    sys.exit(status)
