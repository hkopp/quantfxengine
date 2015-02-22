import random

from quantfxengine.event.event import SignalEvent


class TestRandomStrategy(object):
    def __init__(self, instrument, events):
        self.instrument = instrument
        self.events = events
        self.ticks = 0
        random.seed(5)

    def calculate_signals(self, event):
        if event.type == 'TICK':
            self.ticks += 1
            if self.ticks % 5 == 0:
                side = random.choice(["buy", "sell"])
                order = SignalEvent(
                    self.instrument, "market", side
                )
                self.events.put(order)
