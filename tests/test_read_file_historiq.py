import unittest

import pymarthe as prt

class TestReadHistoriq(unittest.TestCase):
    def setUp(self):
        self.df = prt.read_historiq_file(
            'data/historiq.prn'
        )
    def test_index_size(self):
        self.assertEqual(self.df.index.size, 6)

    def test_column_size(self):
        self.assertEqual(self.df.columns.size, 5)

    def test_level_names(self):
        self.assertEqual(
            self.df.columns.names,
            ['Field', 'XY', 'Label']
        )

    def test_level_keys(self):
        self.assertEqual(
            list(self.df.columns.levels[0]), ['#_Date', 'Charge', 'Débit_Rivi']
        )
        self.assertEqual(
            list(self.df.columns.levels[2]),
            ['#_<Date>', '00464X0013/H1', '00471X0010/H1', 'E6397010', 'E6397030']
        )
        
class TestReadHistoriqGigogne(TestReadHistoriq):
    def setUp(self):
        self.df = prt.read_historiq_file(
            'data/historiq_gigogne.prn'
        )

if __name__ == '__main__':
    unittest.main()