import unittest
import threading
import Queue
import os

from quantfxengine.streaming.streaming import *

class Test_StreamingForexPrices(unittest.TestCase):
    """
    Unit tests for the class StreamingForexPrices
    """
    pass


class Test_StreamingPricesFromFile(unittest.TestCase):
    """
    Unit tests for the class StreamingPricesFromFile
    """
    def test_correct_read(self):
        """
        test if it reads the correct values from a correct file
        """
        events=Queue.Queue()
        stoprequest=threading.Event()
        filename = os.path.join(os.path.dirname(__file__), 'test.csv')
        #reference the relative path
        Stream=StreamingPricesFromFile(filename,events,stoprequest)
        Stream.stream_to_queue()
        event=events.get()
        self.assertIsInstance(event, TickEvent)
        self.assertEqual(event.instrument, 'EUR_USD')
        self.assertEqual(event.time, '2015-02-14T10:30:00.649678Z')
        self.assertEqual(event.bid, 1.24029)
        self.assertEqual(event.ask, 1.24042)
        stoprequest.set()

if __name__ == '__main__':
    unittest.main()
