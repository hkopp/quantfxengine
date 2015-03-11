import requests
import json
import csv
import time
from abc import ABCMeta, abstractmethod #abstract base classes

from quantfxengine.streaming.marketstate import MarketState
from quantfxengine.event.event import TickEvent

class AbstractPriceStream(object):
    """
    This is an abstract class to provide an interface for Streaming
    Prices.
    For creation we need a Queue.Queue() of events and a request to
    stop threading.Event()
    Attributes:
        cur_prices: a hashlist, indexed by instruments
            where each entry is a marketstate(hopefully the current
            one)
        stream_to_queue(): which throws price events into the queue
            of events
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(
        self, events_queue, stoprequest
    ):
        self.events_queue = events_queue
        self.stoprequest = stoprequest
        self.cur_prices = {}

    @abstractmethod
    def stream_to_queue(self):
        raise NotImplementedError()


class StreamingForexPrices_OANDA(AbstractPriceStream):
    """
    A class to connect to the broker and stream prices
    """
    def __init__(
        self, domain, access_token,
        account_id, instruments, events_queue,
        stoprequest
    ):
        self.domain = domain
        self.access_token = access_token
        self.account_id = account_id
        self.instruments = instruments
        self.events_queue = events_queue
        self.stoprequest = stoprequest
        #set up current market state per instrument
        self.cur_prices = {}
        for instr in instruments:
            self.cur_prices[instr]=MarketState(None,None)

    def connect_to_stream(self):
        try:
            s = requests.Session()
            url = "https://" + self.domain + "/v1/prices"
            headers = {'Authorization' : 'Bearer ' + str(self.access_token)}
            params = {'instruments' : ','.join(self.instruments), 'accountId' : self.account_id}
            req = requests.Request('GET', url, headers=headers, params=params)
            pre = req.prepare()
            resp = s.send(pre, stream=True, verify=True)
            return resp
        except Exception as e:
            s.close()
            print "Caught exception when connecting to stream\n" + str(e)

    def stream_to_queue(self):
        response = self.connect_to_stream()
        if response.status_code != 200:
            return
        for line in response.iter_lines(1):
            # check if we have received a stoprequest
            if self.stoprequest.isSet():
                print("Closing Session")
                response.close()
                break
            if line:
                try:
                    msg = json.loads(line)
                except Exception as e:
                    print "Caught exception when converting message into json\n" + str(e)
                    return
                if msg.has_key("instrument") or msg.has_key("tick"):
                    print msg
                    instrument = msg["tick"]["instrument"]
                    time = msg["tick"]["time"]
                    bid = msg["tick"]["bid"]
                    ask = msg["tick"]["ask"]
                    self.cur_prices[instrument].update_bid_ask(bid,ask)
                    tev = TickEvent(instrument, time, bid, ask)
                    self.events_queue.put(tev)


class StreamingPricesFromFile(AbstractPriceStream):
    """
    A class for reading in csv-files and backtesting.
    The csv-file has to be in the form
    instrument,timestamp,bid,ask
    """
    def __init__(self, csv_file, events_queue, stoprequest):
        self.csv_file=csv_file
        self.events_queue = events_queue
        self.cur_prices = {}
        self.stoprequest = stoprequest

    def stream_to_queue(self):
        #check if file exists
        try:
            f=open(self.csv_file, 'rb')
            f.close()
        except Exception as e:
            print("Caught exception while opening backtesting file\n" + str(e))
            return

        #open file and read from it
        file=open(self.csv_file, 'rb')
        try:
            for row in csv.reader(file ,delimiter=','):
                # check if we have received a stoprequest
                if self.stoprequest.isSet():
                    break
                instrument, timestamp, bid, ask = row
                #update cur_prices if it exists for this instrument, else create it
                bid = float(bid)
                ask = float(ask)
                if instrument in self.cur_prices:
                    self.cur_prices[instrument].update_bid_ask(bid,ask)
                else:
                    self.cur_prices[instrument] = MarketState(bid,ask)
                print("instrument = "+str(instrument)+" "
                    "timestamp = "+str(timestamp)+" "
                    "bid = "+str(bid)+" "
                    "ask = "+str(ask)
                )
                tev = TickEvent(instrument, timestamp, bid, ask)
                self.events_queue.put(tev)
                time.sleep(.05)
                #do not flood the queue
        except Exception as e:
            print("Caught exception while reading from backtesting file\n" + str(e))
            return
        finally:
            file.close()


class MockPriceStream(AbstractPriceStream):
    """
    This class is useful for unittesting. It mocks a stream of prices.
    newprice(new_ask, new_bid) sets a new price stream_to_queue()
    pushes this new price into the event_queue
    """
    def __init__(self, events_queue, stoprequest):
        self.events_queue = events_queue
        self.stoprequest = stoprequest
        self.cur_prices = {"EUR_USD" : MarketState(None,None)}

    def newprice(self, new_bid, new_ask):
        self.cur_prices["EUR_USD"].update_bid_ask(new_bid, new_ask)

    def stream_to_queue(self):
        tev = TickEvent("EUR_USD", time, bid, ask)
        self.events_queue.put(tev)
