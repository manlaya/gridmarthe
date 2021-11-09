"""
Read outputs
"""
import datetime
from io import StringIO
import os
import re
import shutil

import numpy as np
import pandas as pd
import pylab as plt

def date_parser(x):
    return datetime.datetime.strptime(x, '%d/%m/%Y')

def gen_glob(in_file):
    with open(in_file, encoding='ISO-8859-1') as f:
        for line in f:
            if line.strip():
                yield(line)
            else:
                break

def open_historiq(fname):
    """
    Read a "historiq.prn" file of MARTHE

    Parameters
    ----------
    fname : str
        Filename

    Returns
    -------
    DataFrame
        DataFrame containing the values of the input file fname
    """
    skiprow = [0]
    with open(fname, encoding='ISO-8859-1') as f:
        for _ in range(4):
            f.readline()
        line = f.readline()
        line = line.strip().split()
        if not re.findall('^[0-9]', line[0]):
            skiprow.append(3)
    df = pd.read_csv(
        fname, delim_whitespace=True,
        skiprows=skiprow, index_col=0,
        engine='python', parse_dates=True, date_parser=date_parser,
        header=[0, 1, 2], encoding='ISO-8859-1'
        )
    df.columns.names = ['Field', 'XY', 'Label']
    df.index.name = 'Date'
    return df

def open_histoclim(fname, **kwargs):
    """
    Read a "histoclim.prn" file of MARTHE

    Parameters
    ----------
    fname : str

    Returns
    -------
    DataFrame
        DataFrame containing the values of the input file fname
    """
    def chunk(s, n):
        for start in range(0, len(s), n):
            yield s[start:start+n]
    f = StringIO(''.join([line for line in gen_glob(fname)]), newline='\n')
    df = pd.read_csv(
        f,
        delim_whitespace=True,
        skiprows=3,
        index_col=0,
        header=None,
        engine='python',
        parse_dates=True,
        date_parser=date_parser,
        encoding='ISO-8859-1',
        **kwargs
    )
    with open(fname, encoding='ISO-8859-1') as f:
        for _ in range(3):
            line = f.readline()
    df.columns = [c.strip() for c in chunk(line.strip(), 16)][1:]
    return df

def open_histobil_debit(fname, **kwargs):
    """
    Read a "histobil_debit.prn" file of MARTHE
    If zone budgets are presents, only the global budget is readed

    Parameters
    ----------
    fname : str

    Returns
    -------
    pandas.DataFrame
    """
    f = StringIO(''.join([line for line in gen_glob(fname)]), newline='\n')
    df = pd.read_csv(
        f,
        delim_whitespace=True,
        skiprows=2,
        index_col=0,
        engine='python',
        parse_dates=True,
        date_parser=date_parser,
        encoding='ISO-8859-1',
        **kwargs
    )
    return df

def mv_results(dir_mod,  dir_res):
    """
    Create a directory for a simulation for transfering outputs

    Parameters
    ----------
    dir_mod : str
        model directory
    dir_res : str
        results directory
    """
    if not os.path.isdir(dir_res):
        os.makedirs(dir_res)
    else:
        ans = input('{0} already exists. Replace it ? (y/N)'.format(dir_res))
        if ans.lower() in ['', 'n', 'no', 'non']:
            return
    filenames = [
        'bilandeb.txt', 'chasim.out', 'debsim.out', 'histobil_debit.prn',
        'histobil_nap_cumu.prn', 'histobil_nap_pastp.prn', 'histobil_riv_dra_lac.prn',
        'histoclim.prn', 'historiq.out', 'historiq.prn', 'mart_ver.txt', 'marthe.txt',
        'converg.txt', 'rivsim.prn'
        ]
    for filename in filenames:
        mod_fichier = '{0}/{1}'.format(dir_mod, filename)
        res_fichier = '{0}/{1}'.format(dir_res, filename)
        if os.path.isfile(mod_fichier):
            shutil.copy(mod_fichier, res_fichier)

def concat_cloneades(dfsim, dir_obs, codes):
    """
    Concatenate a pandas.DataFrame from a .csv file of "clone ADES"
    with a dataframe of a historiq.prn from a MARTHE simulation.

    Only work with the "Charge" component

    Parameters
    ----------
    dfsim : pandas.DataFrame
        DataFrame of an historiq.prn
    dir_obs : str
        Name of the directories where lies the csv files of observations
    codes : list of int
        List of BSS code

    Return
    ------
    pandas.DataFrame
        Observation and simulation with codes BSS in columns 
    """
    dftot = []
    col_sim = dfsim.columns.get_level_values('Label')
    for code_bss in codes:
        dfobs = pd.read_csv(
            '{0}/{1}.csv'.format(dir_obs, code_bss.replace('/', '_')),
            parse_dates=True, index_col='date_mesure', sep=';',
            encoding='cp1252'
            )
        dfobs = dfobs['val_calc_ngf'].resample('D').mean()
        code_sim = col_sim[col_sim.str.contains(code_bss.split('/')[0])]
        assert len(code_sim) == 1
        dftot.append(
            build_obs_sim(
                dfobs,
                dfsim.loc[:, ('Charge', slice(None), code_sim)].squeeze(),
                code_bss
                )
            )
    return pd.concat(dftot, axis=1)

def concat_bdhydro2(dfsim, dir_obs, codes):
    """
    Concatenate a pandas.DataFrame from a .csv file of "clone ADES"
    with a dataframe of a historiq.prn from a MARTHE simulation.

    Only work with the "Débit_Riv" component

    Parameters
    ----------
    dfsim : pandas.DataFrame
        DataFrame of an historiq.prn
    dir_obs : str
        Name of the directories where lies the csv files of observations
    codes : list of int
        List of BSS code

    Return
    ------
    pandas.DataFrame
        Observation and simulation with codes BSS in columns 
    """
    dftot = []
    col_sim = dfsim.columns.get_level_values('Label')
    for code in codes:
        dfobs = pd.read_csv(
            '{0}/{1}.csv'.format(dir_obs, code), parse_dates=True,
            index_col='Date', sep=';', encoding='cp1252'
            )
        dfobs = dfobs.resample('D').mean()
        dfobs = dfobs.replace(-2, np.nan)
        dfobs = dfobs.dropna()
        code_sim = col_sim[col_sim.str.contains(code)]
        assert len(code_sim) == 1
        dftot.append(
            build_obs_sim(
                dfobs.squeeze(),
                dfsim.loc[:, ('Débit_Rivi', slice(None), code_sim)].squeeze(),
                code
                )
            )
    return pd.concat(dftot, axis=1)

def build_obs_sim(dfobs, dfsim, code):
    """
    Return a dataframe two columns "obs" and "sim" for the specified BSS code.
    Code needs to be available in dfobs and dfsim.

    Parameters
    ----------
    dfobs : pandas.DataFrame
    dfsim : pandas.DataFrame
    code : str

    Return
    ------
    pandas.DataFrame
    """
    assert len(dfobs.shape) == 1
    assert len(dfsim.shape) == 1
    df = pd.DataFrame(
        {'obs':dfobs, 'sim':dfsim}
    )
    df.columns = pd.MultiIndex.from_product(
        [[code], ['obs', 'sim']], names=['code', 'type']
        )
    return df

def plot_head(dftot, dir_fig, xp, codes):
    """
    Create figures with observed and simulated piezometric head for the 
    specific codes

    Parameters
    ----------
    dftot : pandas.DataFrame
        dftot is created with concat_cloneades
    dir_fig : str
        diretory in which figures go
    xp : str
        name to give to the simulation
    codes : list of str
    """
    if not os.path.isdir(dir_fig):
        os.makedirs(dir_fig)
    for code in codes:
        df = dftot.xs(level='code', key=code, axis=1)
        ax = df.plot(grid=True, legend=True, style=['b', 'r--'])
        ax.set_ylabel('m')
        ax.set_title('Charge {0} {1}'.format(xp, code))
        plt.savefig(
            '{0}/charges_{1}_{2}.png'.format(
                dir_fig, xp, code.replace('/', '_')),
                dpi=300
                )
        plt.close('all')

def plot_riverflow(dftot, dir_fig, xp, codes):
    """
    Create figures with observed and simulated river flows for the 
    specific codes

    Parameters
    ----------
    dftot : pandas.DataFrame
        dftot is created with concat_bdhydro2
    dir_fig : str
        diretory in which figures go
    xp : str
        name to give to the simulation
    codes : list of str
    """
    if not os.path.isdir(dir_fig):
        os.makedirs(dir_fig)
    for code in codes:
        df = dftot.xs(level='code', key=code, axis=1)
        ax = df.plot(grid=True, legend=True, style=['b', 'r--'])
        ax.set_ylabel('m3/s')
        ax.set_title('Débit Rivière {0} {1}'.format(xp, code))
        plt.savefig(
            '{0}/debits_rivi_{1}_{2}.png'.format(
            dir_fig, xp, code.replace('/', '_')),
            dpi=300
            )
        plt.close('all')




