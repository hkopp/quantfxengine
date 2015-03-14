import logging
from copy import deepcopy
from abc import ABCMeta, abstractmethod

from quantfxengine.event.event import OrderEvent, FillEvent
from quantfxengine.portfolio.position import Position

class AbstractPortfolio(object):
    """
    This is an abstract portfolio to provide a common interface for
    other risk management modules
    Methods:
        execute_signal_event(self, signal_event):
            Takes in a SignalEvent and perhaps outputs OrderEvents
        execute_tick_event(self, tick_event):
            Takes in a TickEvent and adjusts positions, closes some,
            if necessary
        execute_fill_event(self, fill_event):
            Takes in a FillEvent and adjusts positions
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def execute_signal_event(self,signal_event):
        raise NotImplementedError("Need to implement "\
                "execute_signal_event")

    @abstractmethod
    def execute_tick_event(self,tick_event):
        raise NotImplementedError("Need to implement "\
                "execute_tick_event")

    @abstractmethod
    def execute_fill_event(self,fill_event):
        raise NotImplementedError("Need to implement "\
                "execute_fill_event")

class Portfolio(AbstractPortfolio):
    """
    This class models a portfolio
    Attributes:
        ticker: An AbstractPriceStream
        events: Queue for communication
        base: Base currency
        leverage: leverage
        equity: equity
        balance: balance
        risk_per_trade: risk we want to have per trade
        trade_units: how much units we trade
        positions: a dictionary of positions
    """
    def __init__(
        self, ticker, events, base="EUR", leverage=20,
        equity=100000.0, risk_per_trade=0.02
    ):
        self.ticker = ticker
        self.events = events
        self.base = base
        self.leverage = leverage
        self.equity = equity
        self.balance = deepcopy(self.equity)
        self.risk_per_trade = risk_per_trade
        self.trade_units = self.calc_risk_position_size()
        self.positions = {}
        self.logger = logging.getLogger(__name__)

    def calc_risk_position_size(self):
        return self.equity * self.risk_per_trade / self.leverage

    def add_new_position(
        self, side, market, units, exposure,
        add_price, remove_price
    ):
        ps = Position(
            side, market, units, exposure,
            add_price, remove_price
        )
        self.positions[market] = ps

    def add_position_units(
        self, market, units, exposure, 
        add_price, remove_price
    ):
        if market not in self.positions:
            return False
        else:
            ps = self.positions[market]
            new_total_units = ps.units + units
            new_total_cost = ps.avg_price*ps.units + add_price*units
            ps.exposure += exposure
            ps.avg_price = new_total_cost/new_total_units
            ps.units = new_total_units
            ps.update_position_price(remove_price)
            return True

    def remove_position_units(
        self, market, units, remove_price
    ):
        if market not in self.positions:
            return False
        else:
            ps = self.positions[market]
            ps.units -= units
            exposure = float(units)
            ps.exposure -= exposure
            ps.update_position_price(remove_price)
            pnl = ps.calculate_pips() * exposure / remove_price 
            self.balance += pnl
            return True

    def close_position(
        self, market, remove_price
    ):
        if market not in self.positions:
            return False
        else:
            ps = self.positions[market]
            ps.update_position_price(remove_price)
            pnl = ps.calculate_pips() * ps.exposure / remove_price 
            self.balance += pnl
            del[self.positions[market]]
            return True

    def execute_close_all_positions(self):
        """
        This function sends OrderEvents to close all open positions
        """
        for instrument in self.positions.keys():
            pos = self.positions[instrument]
            remove_price = self.ticker.cur_prices[pos.market].bid
            units = pos.units
            if pos.side == "SHORT":
                order = OrderEvent(pos.market, units, "market", "buy")
            else:
                order = OrderEvent(pos.market, units, "market", "sell")
            self.events.put(order)

    def execute_signal_event(self, signal_event):
        side = signal_event.side
        market = signal_event.instrument
        units = int(self.trade_units)

        order = OrderEvent(market, units, "market", side)
        self.events.put(order)

    def execute_tick_event(self,tick_event):
        if tick_event.instrument in self.positions:
            pos=self.positions[tick_event.instrument]
            if pos.side == 'LONG':
                pos.update_position_price(pos.units*tick_event.bid)
            else:
                pos.update_position_price(pos.units*tick_event.ask)

    def execute_fill_event(self,fill_event):
        side = fill_event.side
        market = fill_event.instrument
        units = fill_event.units
        price = fill_event.price

        # Check side for correct bid/ask prices
        add_price = self.ticker.cur_prices[market].ask
        remove_price = self.ticker.cur_prices[market].bid
        exposure = float(units) * self.leverage

        # If there is no position, create one
        if market not in self.positions:
            if side == "LONG":
                self.add_new_position(
                    side, market, units, exposure,
                    price, remove_price
                )
            else:
                self.add_new_position(
                    "SHORT", market, units, exposure,
                    price, add_price
                )

        # If a position exists add or remove units
        else:
            ps = self.positions[market]
            # Check if the sides equal
            if side == ps.side:
                # Add to the position
                if side == "LONG":
                    self.add_position_units(
                        market, units, exposure,
                        price, remove_price
                    )
                else:
                    self.add_position_units(
                        market, units, exposure,
                        price, add_price
                    )
            else:
                # Check if the units close out the position
                if units == ps.units:
                    # Close the position
                    self.close_position(market, price)
                elif units < ps.units:
                    # Remove from the position
                    self.remove_position_units(
                        market, units, price
                    )
                else: # units > ps.units
                    # Close the position and add a new one with
                    # additional units of opposite side
                    new_units = units - ps.units
                    self.close_position(market, price)
                    
                    new_exposure = float(new_units) * self.leverage
                    if ps.side == "LONG":
                        new_side = "SHORT"
                        self.add_new_position(
                            new_side, market, new_units, 
                            new_exposure, price, add_price
                        )
                    else:
                        new_side = "LONG"
                        self.add_new_position(
                            new_side, market, new_units, 
                            new_exposure, price, remove_price
                        )
        self.logger.info("Balance: %0.2f" % self.balance)
