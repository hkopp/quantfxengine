import unittest

from quantfxengine.streaming.marketstate import MarketState

class Test_MarketState(unittest.TestCase):
    """
    Unit tests for the class MarketState
    """
    def setUp(self):
        self.ms = MarketState(1.24010, 1.24000)

    def test_correct_init(self):
        self.assertEqual(self.ms.bid, 1.24010)
        self.assertEqual(self.ms.ask, 1.24000)

    def test_correct_update(self):
        self.ms.update_bid_ask(1.24020, 1.24010)
        self.assertEqual(self.ms.bid, 1.24020)
        self.assertEqual(self.ms.ask, 1.24010)

if __name__ == 'main':
    unittest.main()
