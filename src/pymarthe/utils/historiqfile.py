import pandas as pd
import re
import datetime

date_parser = lambda x: datetime.datetime.strptime(x, '%d/%m/%Y')

def read_historiq_file(fname):
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
