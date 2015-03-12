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

    def __str__(self):
        return "type: "+ str(self.type)+ \
            ", instrument: "+ str(self.instrument)+ \
            ", time: "+ str(self.time)+ \
            ", bid: "+ str(self.bid)+ \
            ", ask: "+ str(self.ask)

    def __repr__(self):
        return "type: "+ str(self.type)+ \
            ", instrument: "+ str(self.instrument)+ \
            ", time: "+ str(self.time)+ \
            ", bid: "+ str(self.bid)+ \
            ", ask: "+ str(self.ask)


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

    def __str__(self):
        return "type: "+ str(self.type)+ \
            ", instrument: "+ str(self.instrument)+ \
            ", order_type: "+ str(self.order_type)+ \
            ", side: "+ str(self.side)

    def __repr__(self):
        return "type: "+ str(self.type)+ \
            ", instrument: "+ str(self.instrument)+ \
            ", order_type: "+ str(self.order_type)+ \
            ", side: "+ str(self.side)

class OrderEvent(Event):
    """
    Events for buy or sell orders which should be executed
    Attributes:
        instrument: e.g. "EUR_USD"
        units: How much we want to buy/sell
        order_type: 'market' or 'limit'
        side: 'buy' or 'sell'
    """
    def __init__(self, instrument, units, order_type, side):
        self.type = 'ORDER'
        self.instrument = instrument
        self.units = units
        self.order_type = order_type
        self.side = side

    def __str__(self):
        return "type: "+ str(self.type)+ \
            ", instrument: "+ str(self.instrument)+ \
            ", units: "+ str(self.units)+ \
            ", order_type: "+ str(self.order_type)+ \
            ", side: "+ str(self.side)

    def __repr__(self):
        return "type: "+ str(self.type)+ \
            ", instrument: "+ str(self.instrument)+ \
            ", units: "+ str(self.units)+ \
            ", order_type: "+ str(self.order_type)+ \
            ", side: "+ str(self.side)


class FillEvent(Event):
    """
    This event signals that an order has been filled.
    Attributes:
        instrument: e.g. "EUR_USD"
        units: How much we have bought/sold
        side: 'LONG' or 'SHORT'
        price: the price for which the instrument was bought/sold
    """
    def __init__(self, instrument, units, side, price):
        self.type = 'FILL'
        self.instrument = instrument
        self.units = units
        self.side = side
        self.price = price

    def __str__(self):
        return "type: "+ str(self.type)+ \
            ", instrument: "+ str(self.instrument)+ \
            ", units: "+ str(self.units)+ \
            ", side: "+ str(self.side)+ \
            ", price: "+ str(self.price)

    def __repr__(self):
        return "type: "+ str(self.type)+ \
            ", instrument: "+ str(self.instrument)+ \
            ", units: "+ str(self.units)+ \
            ", side: "+ str(self.side)+ \
            ", price: "+ str(self.price)
