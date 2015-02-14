import Queue
import threading
import time

from execution import Execution, MockExecution
from settings import STREAM_DOMAIN, API_DOMAIN, ACCESS_TOKEN, ACCOUNT_ID, BACKTEST, BACKTESTFILE
from strategy import TestRandomStrategy
from streaming import StreamingForexPrices, StreamingPricesFromFile


def trade(events, strategy, execution):
    """
    Carries out an infinite while loop that polls the
    events queue and directs each event to either the
    strategy component of the execution handler.
    """
    while True:
        try:
            event = events.get(True,0.5)
            #block and wait a half second if queue is empty
        except Queue.Empty:
            pass
        else:
            if event is not None:
                if event.type == 'TICK':
                    strategy.calculate_signals(event)
                elif event.type == 'ORDER':
                    print "Executing order!"
                    execution.execute_order(event)


if __name__ == "__main__":
    heartbeat = 0.5    # Half a second between polling
    events = Queue.Queue()

    # Trade 10000 units of EUR/USD
    instrument = "EUR_USD"
    units = 10000

    if BACKTEST:
        # Create the price streaming class
        prices = StreamingPricesFromFile(
            BACKTESTFILE, events
        )
        # Create the mock execution handler
        execution = MockExecution()
    else:
        # Create the OANDA market price streaming class
        # making sure to provide authentication commands
        prices = StreamingForexPrices(
            STREAM_DOMAIN, ACCESS_TOKEN, ACCOUNT_ID,
            instrument, events
        )
        # Create the execution handler making sure to
        # provide authentication commands
        execution = Execution(API_DOMAIN, ACCESS_TOKEN, ACCOUNT_ID)

    # Create the strategy/signal generator, passing the
    # instrument, quantity of units and the events queue
    strategy = TestRandomStrategy(instrument, units, events)

    # Create two separate threads: One for the trading loop
    # and another for the market price streaming class
    trade_thread = threading.Thread(target=trade, args=(events, strategy, execution))
    price_thread = threading.Thread(target=prices.stream_to_queue, args=[])

    # Start both threads
    trade_thread.start()
    price_thread.start()
