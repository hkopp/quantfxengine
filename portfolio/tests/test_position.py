import unittest
from quantfxengine.portfolio.portfolio import Position

class Test_Position(unittest.TestCase):
    """
    Unit tests for the class Position
    """
    def setUp(self):
        self.lpos = Position('LONG','EUR_USD', 10000, 0.25, 2, 4)
        self.spos = Position('SHORT','EUR_USD', 10000, 0.25, 2, 4)

    def test_correct_profit(self):
        self.assertEqual(self.lpos.profit_base, 0.125)
        self.assertEqual(self.spos.profit_base, -0.125)

    def test_correct_profit_perc(self):
        self.assertEqual(self.lpos.profit_perc, 50)
        self.assertEqual(self.spos.profit_perc, -50)

    def test_correct_update(self):
        """
        test if prices update correctly
        """
        self.lpos.update_position_price(1)
        self.assertEqual(self.lpos.cur_price, 1)
        self.spos.update_position_price(1)
        self.assertEqual(self.spos.cur_price, 1)
        #now profit should have been adjusted
        self.assertEqual(self.lpos.profit_base, -0.25)
        self.assertEqual(self.spos.profit_base, 0.25)
        self.assertEqual(self.lpos.profit_perc, -100)
        self.assertEqual(self.spos.profit_perc, 100)

if __name__ == '__main__':
    unittest.main()
