import Queue
import threading
import time

from quantfxengine.execution.execution import ExecutionAtOANDA, MockExecution
from quantfxengine.portfolio.portfolio import Portfolio
from quantfxengine.settings import *
from quantfxengine.strategy.strategy import TestRandomStrategy
from quantfxengine.streaming.streaming import *


def trade(events, strategy, portfolio, execution, stoprequest):
    """
    Carries out an infinite while loop that polls the events queue and
    directs each event to either the strategy component, the execution
    handler or the portfolio.
    """
    while not stoprequest.isSet():
        try:
            event = events.get(True,0.5)
            #block and wait a half second if queue is empty
        except Queue.Empty:
            pass
        else:
            if event is not None:
                if event.type == 'TICK':
                    strategy.calculate_signals(event)
                    portfolio.execute_tick_event(event)
                elif event.type == 'SIGNAL':
                    print("recv new order signal:", event)
                    portfolio.execute_signal_event(event)
                elif event.type == 'ORDER':
                    print "Executing order!"
                    execution.execute_order(event)
                elif event.type == 'FILL':
                    print("recv new fill event:", event)
                    portfolio.execute_fill_event(event)
    #execute remaining events
    while not events.empty():
        event = events.get()
        if event is not None:
            if event.type == 'FILL':
                #throw everything away except fillevents
                print("recv new fill event:", event.side,
                        event_units)
                portfolio.execute_fill_order(event)
            else:
                pass
    #close all positions
    print "Closing all positions"
    portfolio.close_all_positions()
    #and execute the resulting order and fill events
    while not events.empty():
        event = events.get()
        if event is not None:
            if event.type == 'ORDER':
                print "Executing order!"
                execution.execute_order(event)
            elif event.type == 'Fill':
                print("recv new fill event:", event.side,
                        event_units)
                portfolio.execute_fill_order(event)

if __name__ == "__main__":
    events = Queue.Queue() # Queue for communication between threads
    stoprequest = threading.Event() # For stopping the threads

    # Trade UNITS units of INSTRUMENTS
    instruments = INSTRUMENTS
    units = UNITS

    if BACKTEST:
        # Create the price streaming class
        prices = StreamingPricesFromFile(
            BACKTESTFILE, events, stoprequest
        )
        # Create the mock execution handler
        execution = MockExecution(events, prices)
    else:
        # Create the OANDA market price streaming class
        # making sure to provide authentication commands
        prices = StreamingForexPrices_OANDA(
            STREAM_DOMAIN, ACCESS_TOKEN, ACCOUNT_ID,
            instruments, events, stoprequest
        )
        # Create the execution handler making sure to
        # provide authentication commands
        execution = ExecutionAtOANDA(API_DOMAIN, ACCESS_TOKEN, ACCOUNT_ID, events)

    # Create the strategy/signal generator, passing the
    # instrument, quantity of units and the events queue
    strategy = TestRandomStrategy(events)

    # Create the portfolio object that will be used to
    # compare the OANDA positions with the local, to
    # ensure backtesting integrity.
    portfolio = Portfolio(prices, events, equity=units)

    # Create two separate threads: One for the trading loop
    # and another for the market price streaming class
    trade_thread = threading.Thread(target=trade, args=(events,
        strategy, portfolio, execution, stoprequest))
    price_thread = threading.Thread(target=prices.stream_to_queue,
        args=[])

    # Start both threads
    trade_thread.start()
    price_thread.start()

    # say to the threads if i have pressed ctrl+c
    try:
        while trade_thread.is_alive():
            trade_thread.join(10)
    except (KeyboardInterrupt, SystemExit):
        print("Sending stop request to threads")
        stoprequest.set()
        print("Waiting for threads to terminate")
