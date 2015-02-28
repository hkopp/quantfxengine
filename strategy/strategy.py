import random

from quantfxengine.event.event import SignalEvent


class TestRandomStrategy(object):
    def __init__(self, events):
        self.events = events
        self.ticks = 0
        random.seed(5)

    def calculate_signals(self, event):
        if event.type == 'TICK':
            self.ticks += 1
            if self.ticks % 5 == 0:
                side = random.choice(["LONG", "SHORT"])
                order = SignalEvent(
                    event.instrument, "market", side
                )
                self.events.put(order)
