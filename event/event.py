class Event(object):
    pass


class TickEvent(Event):
    """
    Events with prices
        Attributes:
        instrument: e.g. EUR_USD
        time: timestamp from price
        bid: Bid price
        ask: Ask price
    """
    def __init__(self, instrument, time, bid, ask):
        self.type = 'TICK'
        self.instrument = instrument
        self.time = time
        self.bid = bid
        self.ask = ask

class SignalEvent(Event):
    """
    Events for good trading opportunities if they fit in our risk
    management
    Attributes
        instrument: e.g. EUR_USD
        order_type: 'market' or 'limit'
        side: 'LONG' or 'SHORT'
    """
    def __init__(self, instrument, order_type, side):
        self.type = 'SIGNAL'
        self.instrument = instrument
        self.order_type = order_type
        self.side = side

class OrderEvent(Event):
    """
    Events for buy or sell orders which should be executed
    Attributes:
        instrument: e.g. "EUR_USD"
        units: How much we want to buy/sell
        order_type: 'market' or 'limit'
        side: 'LONG' or 'SHORT'
    """
    def __init__(self, instrument, units, order_type, side):
        self.type = 'ORDER'
        self.instrument = instrument
        self.units = units
        self.order_type = order_type
        self.side = side
