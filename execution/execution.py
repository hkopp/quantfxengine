import httplib
import urllib
import Queue
import json

from abc import ABCMeta, abstractmethod
from quantfxengine.event.event import FillEvent
from quantfxengine.streaming.streaming import StreamingPricesFromFile

class AbstractExecution(object):
    """
    An abstract class to abstract execution for different Brokers.
    Methods:
        execute_order(order_event): takes an order_event and executes
            it
    Attributes:
        event_queue: An event queue where we put FillEvents for
            successfull orders
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def execute_order(self,order_event):
        raise NotImplementedError("Need to implement execute_order!")

class ExecutionAtOANDA(AbstractExecution):
    def __init__(self, domain, access_token, account_id, event_queue):
        self.domain = domain
        self.access_token = access_token
        self.account_id = account_id
        self.conn = self.obtain_connection()
        self.event_queue = event_queue

    def obtain_connection(self):
        return httplib.HTTPSConnection(self.domain)

    def execute_order(self, order_event):
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": "Bearer " + self.access_token
        }
        params = urllib.urlencode({
            "instrument" : order_event.instrument,
            "units" : order_event.units,
            "type" : order_event.order_type,
            "side" : order_event.side
        })
        self.conn.request(
            "POST",
            "/v1/accounts/%s/orders" % str(self.account_id),
            params, headers
        )
        response = self.conn.getresponse().read()
        if response:
            try:
                msg = json.loads(response)
            except Exception as e:
                print "Caught exception when converting message to json\n" + str(e)
                return
            if msg.has_key("price") and ( msg.has_key("tradeOpened") or msg.has_key("tradeClosed") ):
                print msg
                instrument = msg["instrument"]
                price = msg["price"]
                if msg["tradeOpened"].has_key("units"):
                    units = msg["tradeOpened"]["units"]
                    side = msg["tradeOpened"]["side"]
                    if side == "buy":
                        fevent = FillEvent(instrument, units, "LONG", price)
                    elif side == "sell":
                        fevent = FillEvent(instrument, units, "SHORT", price)
                    else:
                        raise ValueError("side should be 'buy' or 'sell' "\
                                "but is %s", side)
                    self.event_queue.put(fevent)
                else:
                    for close in msg["tradesClosed"]:
                        units = close["units"]
                        side = close["side"]
                        if side == "buy":
                            fevent = FillEvent(instrument, units, "LONG", price)
                        elif side == "sell":
                            fevent = FillEvent(instrument, units, "SHORT", price)
                        else:
                            raise ValueError("side should be 'buy' or 'sell' "\
                                "but is %s", side)
                        self.event_queue.put(fevent)

class MockExecution(AbstractExecution):
    """
    A mock execution object which does not trade externally
    Very useful for backtesting purposes
    """
    def __init__(self, event_queue, ticker):
        self.event_queue = event_queue
        self.ticker = ticker
    def execute_order(self, order_event):
        instrument = order_event.instrument
        units = order_event.units
        order_type = order_event.order_type
        side = order_event.side
        print("Would have executed: ", order_event)
        if side == "buy":
            price = self.ticker.cur_prices[instrument].ask
            fevent = FillEvent(instrument, units, "LONG", price)
        elif side == "sell":
            price = self.ticker.cur_prices[instrument].bid
            fevent = FillEvent(instrument, units, "SHORT", price)
        else:
            raise ValueError("side should be 'buy' or 'sell' "\
                    "but is %s", side)
        self.event_queue.put(fevent)
