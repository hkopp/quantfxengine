import requests
import json
import csv
import time

from quantfxengine.event.event import TickEvent


class StreamingForexPrices(object):
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

    def connect_to_stream(self):
        try:
            s = requests.Session()
            url = "https://" + self.domain + "/v1/prices"
            headers = {'Authorization' : 'Bearer ' + self.access_token}
            params = {'instruments' : self.instruments, 'accountId' : self.account_id}
            req = requests.Request('GET', url, headers=headers, params=params)
            pre = req.prepare()
            resp = s.send(pre, stream=True, verify=False)
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
                    tev = TickEvent(instrument, time, bid, ask)
                    self.events_queue.put(tev)


class StreamingPricesFromFile(object):
    """
    A class for reading in csv-files and backtesting.
    The csv-file has to be in the form
    instrument,timestamp,bid,ask
    """
    def __init__(self, csv_file, events_queue, stoprequest):
        self.csv_file=csv_file
        self.events_queue = events_queue
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
