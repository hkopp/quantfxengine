import unittest
import Queue
import threading

from quantfxengine.portfolio.portfolio import Portfolio
from quantfxengine.streaming.streaming import MockPriceStream
from quantfxengine.event.event import SignalEvent

class Test_Portfolio(unittest.TestCase):
    """
    Unit tests for the class Portfolio
    """
    def setUp(self):
        self.price_events=Queue.Queue()
        self.order_events=Queue.Queue()
        stoprequest=threading.Event()
        self.ticker=MockPriceStream(self.price_events,stoprequest)
        #bid=3, ask=4
        self.ticker.newprice(3,4)
#        self.ticker.stream_to_queue()
        self.pf=Portfolio(
                self.ticker, self.order_events,"EUR",
                1, 10000, 0.02)
        self.leverage_pf=Portfolio(
                self.ticker, self.order_events,"EUR",
                20, 10000, 0.02)

    def test_correct_init(self):
        self.assertEqual(self.pf.balance, self.pf.equity)
        self.assertEqual(self.pf.trade_units, 200)

    def test_risk_position_size(self):
        self.assertEqual(self.pf.calc_risk_position_size(), 200)
        self.assertEqual(self.leverage_pf.calc_risk_position_size(), 10)

    def test_add_new_position(self):
        self.pf.add_new_position('LONG',"EUR_USD", 100, 500, 4, 3)
        self.assertEqual(self.pf.positions["EUR_USD"].side, 'LONG')
        self.assertEqual(self.pf.positions["EUR_USD"].market, 'EUR_USD')
        self.assertEqual(self.pf.positions["EUR_USD"].units, 100)
        self.assertEqual(self.pf.positions["EUR_USD"].exposure, 500)
        self.assertEqual(self.pf.positions["EUR_USD"].avg_price, 4)
        self.assertEqual(self.pf.positions["EUR_USD"].cur_price, 3)

    def test_add_position_units(self):
        self.pf.add_new_position('LONG',"EUR_USD", 100, 500, 4, 3)
        self.pf.add_position_units("EUR_USD", 300, 500, 8, 4)
        self.assertEqual(self.pf.positions["EUR_USD"].side, 'LONG')
        self.assertEqual(self.pf.positions["EUR_USD"].market, 'EUR_USD')
        self.assertEqual(self.pf.positions["EUR_USD"].units, 400)
        self.assertEqual(self.pf.positions["EUR_USD"].exposure, 1000)
        self.assertEqual(self.pf.positions["EUR_USD"].avg_price, 7)
        self.assertEqual(self.pf.positions["EUR_USD"].cur_price, 4)

    def test_remove_position_units(self):
        self.pf.add_new_position('LONG',"EUR_USD", 100, 500, 4, 3)
        self.pf.remove_position_units("EUR_USD", 50, 2)
        self.assertEqual(self.pf.positions["EUR_USD"].side, 'LONG')
        self.assertEqual(self.pf.positions["EUR_USD"].units, 50)
        self.assertEqual(self.pf.positions["EUR_USD"].exposure, 450)
        self.assertEqual(self.pf.balance, 9950)

    def test_close_position(self):
        self.pf.add_new_position('LONG',"EUR_USD", 100, 500, 4, 3)
        self.pf.close_position("EUR_USD", 2)
        self.assertEqual(self.pf.balance, 9500)

    def test_execute_signal_new_position(self):
        buyevent = SignalEvent("EUR_USD",'market','LONG')
        self.pf.execute_signal_event(buyevent)
        self.assertEqual(self.pf.positions["EUR_USD"].side, 'LONG')
        self.assertEqual(self.pf.positions["EUR_USD"].market, 'EUR_USD')
        self.assertEqual(self.pf.positions["EUR_USD"].units, 200)
        self.assertEqual(self.pf.positions["EUR_USD"].exposure, 200)
        self.assertEqual(self.pf.positions["EUR_USD"].avg_price, 4)
        self.assertEqual(self.pf.positions["EUR_USD"].cur_price, 3)
        #Portfolio with leverage
        self.leverage_pf.execute_signal_event(buyevent)
        self.assertEqual(self.leverage_pf.positions["EUR_USD"].side, 'LONG')
        self.assertEqual(self.leverage_pf.positions["EUR_USD"].market, 'EUR_USD')
        self.assertEqual(self.leverage_pf.positions["EUR_USD"].units, 10)
        self.assertEqual(self.leverage_pf.positions["EUR_USD"].exposure, 200)
        self.assertEqual(self.leverage_pf.positions["EUR_USD"].avg_price, 4)
        self.assertEqual(self.leverage_pf.positions["EUR_USD"].cur_price, 3)

    def test_execute_signal_add_to_position(self):
        buyevent = SignalEvent("EUR_USD",'market','LONG')
        self.pf.execute_signal_event(buyevent)
        buyevent = SignalEvent("EUR_USD",'market','LONG')
        self.pf.execute_signal_event(buyevent)
        self.assertEqual(self.pf.positions["EUR_USD"].side, 'LONG')
        self.assertEqual(self.pf.positions["EUR_USD"].market, 'EUR_USD')
        self.assertEqual(self.pf.positions["EUR_USD"].units, 400)
        self.assertEqual(self.pf.positions["EUR_USD"].exposure, 400)

    def test_execute_signal_remove_from_position(self):
        self.ticker.newprice(2,4)
        buyevent = SignalEvent("EUR_USD",'market','LONG')
        self.pf.execute_signal_event(buyevent)
        self.pf.execute_signal_event(buyevent)
        sellevent = SignalEvent("EUR_USD",'market','SHORT')
        self.pf.execute_signal_event(sellevent)
        self.assertEqual(self.pf.positions["EUR_USD"].side, 'LONG')
        self.assertEqual(self.pf.positions["EUR_USD"].market, 'EUR_USD')
        self.assertEqual(self.pf.positions["EUR_USD"].units, 200)
        self.assertEqual(self.pf.positions["EUR_USD"].exposure, 200)
        self.assertEqual(self.pf.balance, 9800)

    def test_execute_signal_remove_position(self):
        buyevent = SignalEvent("EUR_USD",'market','LONG')
        self.pf.execute_signal_event(buyevent)
        self.ticker.newprice(4,5)
        sellevent = SignalEvent("EUR_USD",'market','SHORT')
        self.pf.execute_signal_event(sellevent)
        self.assertNotIn('EUR_USD', self.pf.positions.keys())

    def test_execute_signal_invert_position(self):
        self.ticker.newprice(2,4)
        buyevent = SignalEvent("EUR_USD",'market','LONG')
        self.pf.execute_signal_event(buyevent)
        sellevent = SignalEvent("EUR_USD",'market','SHORT')
        self.pf.execute_signal_event(sellevent)
        self.pf.execute_signal_event(sellevent)
        self.assertEqual(self.pf.positions["EUR_USD"].side, 'SHORT')
        self.assertEqual(self.pf.positions["EUR_USD"].market, 'EUR_USD')
        self.assertEqual(self.pf.positions["EUR_USD"].units, 200)
        self.assertEqual(self.pf.positions["EUR_USD"].exposure, 200)
        self.assertEqual(self.pf.balance, 9800)


if __name__ == 'main':
    unittest.main()
