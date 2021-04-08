import os
import unittest

import pandas as pd
import numpy as np

from pymarthe.pestpp import MartheToPest


instruction_file_pestpp = open('data/instruction_file_pestpp', 'r').read().strip()
instruction_file_pest = open('data/instruction_file_pest', 'r').read().strip()
instruction_file_pestpp2 = open('data/instruction_file_pestpp2', 'r').read().strip()
instruction_file_pest2 = open('data/instruction_file_pest2', 'r').read().strip()
control_file_pestpp = open('data/control_file_pestpp', 'r').read().strip()
control_file_pest = open('data/control_file_pest', 'r').read().strip()
control_file_pestpp2 = open('data/control_file_pestpp2', 'r').read().strip()
control_file_pest2 = open('data/control_file_pest2', 'r').read().strip()

class BaseTest(unittest.TestCase):
    def tearDown(self):
        self.cleanOutput()
    
    def cleanOutput(self):
        if os.path.exists('data/test.out'):
            os.remove('data/test.out')

class TestMartheToPest(BaseTest):
    def setUp(self):
        self.cleanOutput()
        self.pest = MartheToPest.from_historiq_file('data/historiq.prn')
        df = pd.read_csv(
            'data/observations.csv',
            parse_dates=True,
            index_col=0
        )
        self.pest.register_obs_from_dataframe(df, 'Charge')
        self.pest.register_obs_from_dataframe(df, 'Débit_Rivi')
        self.pest.set_group('Charge','Piézo')
        self.pest.set_weight('Charge', 7.63136)
        self.pest.set_group('Débit_Rivi','Rivière')
        self.pest.set_weight('Débit_Rivi', 4.947392E-05)
    
    def test_shapes(self):
        for attr in ['dfObs', 'dfGroup', 'dfWeight', 'dfObsName']:
            self.assertSequenceEqual(getattr(self.pest, attr).shape, (6, 4))
    
    def test_obsname(self):
        self.assertEqual(
            self.pest.dfObsName.loc['1995-08-03', ('Débit_Rivi', 'E6397010')],
            '19950803_Débit_Rivi_E6397010'
        )

    def test_obsvalue(self):
        self.assertEqual(
            self.pest.dfObs.loc['1995-08-03', ('Débit_Rivi', 'E6397010')],
            0.93
        )

    def test_groupvalue(self):
        self.assertEqual(
            self.pest.dfGroup.loc['1995-08-03', ('Débit_Rivi', 'E6397010')],
            'Rivière'
        )

    def test_weightvalue(self):
        self.assertEqual(
            self.pest.dfWeight.loc['1995-08-03', ('Débit_Rivi', 'E6397010')],
            4.947392E-05
        )
    
    def test_write_to_instructionfile_pestpp(self):
        self.pest.convert_obsname('pestpp')
        self.pest.write_instruction_file('data/test.out')
        with open('data/test.out') as f:
            lines = f.read().strip()
            self.assertEqual(lines, instruction_file_pestpp)

    def test_write_to_instructionfile_pest(self):
        self.pest.convert_obsname('pest')
        self.pest.write_instruction_file('data/test.out')
        with open('data/test.out') as f:
            lines = f.read().strip()
            self.assertEqual(lines, instruction_file_pest)

    def test_write_to_controlfile_pestpp(self):
        self.pest.convert_obsname('pestpp')
        self.pest.write_pst_file('data/test.out')
        with open('data/test.out') as f:
            lines = f.read().strip()
            self.assertEqual(lines, control_file_pestpp)

    def test_write_to_controlfile_pest(self):
        self.pest.convert_obsname('pest')
        self.pest.write_pst_file('data/test.out')
        with open('data/test.out') as f:
            lines = f.read().strip()
            self.assertEqual(lines, control_file_pest)


class TestMartheToPest2(BaseTest):
    def setUp(self):
        self.cleanOutput()
        self.pest = MartheToPest.from_historiq_file('data/historiq.prn')
        df = pd.read_csv(
            'data/observations.csv',
            parse_dates=True,
            index_col=0
        )
        df.loc['1995-8-3', 'E6397010'] = np.nan
        df.loc['1995-8-4', 'E6397010'] = np.nan
        df.loc['1995-8-2', 'E6397030'] = 0.49
        df.loc['1995-8-1', '00464X0013/H1'] = 95.4852144875
        self.pest.register_obs_from_dataframe(df, 'Charge')
        self.pest.register_obs_from_dataframe(df, 'Débit_Rivi')

    def test_write_to_instructionfile_pestpp2(self):
        self.pest.convert_obsname('pestpp')
        self.pest.write_instruction_file('data/test.out')
        with open('data/test.out') as f:
            lines = f.read().strip()
            self.assertEqual(lines, instruction_file_pestpp2)

    def test_write_to_instructionfile_pest2(self):
        self.pest.convert_obsname('pest')
        self.pest.write_instruction_file('data/test.out')
        with open('data/test.out') as f:
            lines = f.read().strip()
            self.assertEqual(lines, instruction_file_pest2)

    def test_write_to_controlfile_pestpp2(self):
        self.pest.convert_obsname('pestpp')
        self.pest.write_pst_file('data/test.out')
        with open('data/test.out') as f:
            lines = f.read().strip()
            self.assertEqual(lines, control_file_pestpp2)

    def test_write_to_controlfile_pest2(self):
        self.pest.convert_obsname('pest')
        self.pest.write_pst_file('data/test.out')
        with open('data/test.out') as f:
            lines = f.read().strip()
            self.assertEqual(lines, control_file_pest2)

if __name__ == '__main__':
    unittest.main()