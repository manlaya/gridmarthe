import pandas as pd
import datetime
import numpy as np
from collections import defaultdict
import pymarthe as prt

class MartheToPest(object):
    """
    MartheToPest object for generated pest++ instruction and control files.
    """
    obs_prefix = 'O'
    def __init__(self, dfSim, obsname_fmt='pestpp'):
        """
        A PestPP object generated from a simulation dataframe built from 
        a MARTHE historiq file. The simulation dataframe needs to have a 
        panda.DatetimeIndex index.

        Parameters
        ----------
        dfSim: pandas.DataFrame
            Corresponds to a historiq file from MARTHE
        obsname_fmt : str, default 'pestpp'
            Format of the observation name in the pest control file. The default format
            "pestpp" names the observation as DATE_field_LABEL. The format "pest" names
            the observation sequentially Obs1, Obs2... ObsN if N observations are available
        """
        dfSim = dfSim.droplevel(level='XY', axis=1)
        dfSim = dfSim.drop(dfSim.columns[0], axis=1)
        self.dfSim = dfSim
        self.dfObs = dfSim.copy()
        self.dfObs.loc[:,:] = 0
        self.dfWeight = dfSim.copy()
        self.dfWeight.loc[:,:] = 1
        self.dfGroup = dfSim.copy()
        self.dfGroup.loc[:,:] = 'default_grp'
        self.obsname_fmt = obsname_fmt
        
    def _reindex_dataframe(self, df, field):
        df = df.reindex(
            index=self.dfSim.index,
            columns=self.dfSim.xs(level='Field', key=field, axis=1).columns
        )
        return df

    def _format_obsname_to_pestpp(self):
        dfObsName = self.dfObs.copy()
        obs_name = ['_'.join([C, L]) for C, L in self.dfSim.columns]
        for date, _ in self.dfSim.iterrows():
            date_obs_name = np.array(
                [
                    '_'.join([datetime.datetime.strftime(date, '%Y%m%d'), o])
                    for o in obs_name 
                ]
            )
            dfObsName.loc[date, :] = date_obs_name
        dfObsName[self.dfObs.isna()] = 'w'
        self.obsname_fmt = 'pestpp'
        return dfObsName

    def _format_obsname_to_pest(self):
        data = self.dfObs.values.flatten()
        data = np.where(np.isnan(data), 0, 1)
        data = np.cumsum(data)
        data = data.reshape(self.dfObs.shape)
        data = np.where(self.dfObs.isna(), np.nan, data)
        dfObsName = self.dfObs.copy()
        dfObsName.iloc[:,:] = data
        dfObsName = dfObsName.where(
            dfObsName.isna(),
            self.obs_prefix + dfObsName.astype('Int64').astype('str')
        )
        dfObsName.iloc[dfObsName.isna()] = 'w'
        self.obsname_fmt = 'pest'
        return dfObsName

    @classmethod
    def from_historiq_file(cls, fname, obsname_fmt='pestpp'):
        """
        Build a PestPP instance from a MARTHE historiq.prn file

        Parameters
        ----------
        fname: str
            Historiq.prn file path.
        obsname_fmt : str, default 'pestpp'
            Format of the observation name in the pest control file. The default format
            "pestpp" names the observation as DATE_field_LABEL. The format "pest" names
            the observation sequentially Obs1, Obs2... ObsN if N observations are available
        
        Returns
        -------
        PestPP instance
        """
        dfSim = prt.read_historiq_file(fname)
        return cls(dfSim, obsname_fmt)

    def register_obs_from_dataframe(self, df, field):
        """
        Populate the dfObs dataframe with observations for the 
        specified field of the historiq.prn file

        Parameters
        ----------
        df : pandas.DataFrame
            DataFrame of observations with labeled columns and DatetimeIndex index
        field : str
            Field name to populate in the dfObs dataframe.
        """
        df = self._reindex_dataframe(df, field)
        self.dfObs.loc[:, (field, slice(None))] = df.values
        self.dfWeight[self.dfObs.isna()] = np.nan
        self.dfGroup[self.dfObs.isna()] = np.nan
        if self.obsname_fmt == 'pest':
            self.dfObsName = self._format_obsname_to_pest()
        elif self.obsname_fmt == 'pestpp':
            self.dfObsName = self._format_obsname_to_pestpp()
    
    def convert_obsname(self, fmt):
        """
        Convert observation names from the current format specified
        by the obsname_fmt attribute to the fmt format. If the osbname_fmt attribute
        is already set to fmt, nothing appends.

        Paramters
        ---------
        fmt : str
            take only the value 'pest' or 'pestpp'
        """
        if self.obsname_fmt == 'pest' and fmt == 'pestpp':
            self.dfObsName = self._format_obsname_to_pestpp()
        elif self.obsname_fmt == 'pestpp' and fmt == 'pest':
            self.dfObsName = self._format_obsname_to_pest()

    def set_group(self, field, group):
        """
        Set group to the speficified field of the simulation

        Parameters
        ----------
        field : str
            Field name
        group : str
            Group name
        """
        df = self.dfGroup.loc[:, (field, slice(None))].copy()
        df.iloc[~df.isna()] =  group
        self.dfGroup.loc[:, (field, slice(None))] = df

    def set_weight(self, field, weight):
        """
        Set weight to the speficified field of the simulation

        Parameters
        ----------
        field : str
            Field name
        weight : int, float
            Weight 
        """
        df = self.dfWeight.loc[:, (field, slice(None))].copy()
        df.iloc[~df.isna()] = weight
        self.dfWeight.loc[:, (field, slice(None))] = df

    def write_instruction_file(self, fname_ins):
        """
        Export an instruction file

        Parameters
        ----------
        fname_ins : str
            File path of the instruction file to be written.
        """
        with open(fname_ins, 'w') as f:
            f.write('pif %\n')
            f.write('%<Date>%\n')
            nbl = 1
            for _, row in self.dfObsName.iterrows():
                values = row.unique()
                if len(values) == 1 and values[0] == 'w':
                    nbl += 1
                else:
                    temp = []
                    for i in row[::-1]:
                        if i != 'w':
                            temp.append('!' + i + '!')
                        else:
                            if temp:
                                temp.append(i)
                    date_obs_name = ' '.join(temp[::-1])
                    f.write(
                        'l{0} !dum! w {1}\n'.format(nbl, date_obs_name)
                    )
                    nbl = 1
    
    def write_pst_file(self, fname_pst):
        """
        Export the * observation group and * observation data
        paragraphs of a pst control file

        Parameters
        ----------
        fname_pst : str
            File path of a pst control file to be written
        """
        df = defaultdict()
        mask = ~self.dfObs.isna()
        for attr, key  in zip(
            ['dfObsName', 'dfObs', 'dfWeight', 'dfGroup'],
            ['Name', 'Value', 'Weight', 'Group']
        ):
            data = getattr(self, attr)[mask]
            data = pd.melt(data.T)['value']
            df[key] = data[~data.isna()]
        df = pd.DataFrame(df)
        with open(fname_pst, 'w') as f:
            f.write('* observation group\n')
            groups = df['Group'].unique()
            for group in groups:
                f.write(' ' + group + '\n')
            f.write('* observation data\n')
            max_len_name = df['Name'].str.len().max()
            max_len_group = df['Group'].str.len().max()
            if self.obsname_fmt == 'pest':
                try:
                    assert max_len_name <= 20
                except AssertionError:
                    print("Format PEST : nom d'observation > à 20 caractères")
                try:
                    assert max_len_group <= 12
                except AssertionError:
                    print("Format PEST : nom de groupe > à 12 caractères")
            formats = {
                'Name': '{:<%ds}' % max_len_name,
                'Value': '{:<20.8}',
                'Weight': '{:<20.8}',
                'Group': '{:<%ds}' % max_len_group
            }
            formatters = {k: v.format for k, v in formats.items()}
            df.to_string(
                f,
                formatters=formatters,
                header=None,
                index=None,
            )
            f.close()
