class MarketState(object):
    """
    This class models the state of an instrument in the market
    Attributes:
        bid: bid price
        ask: bid price
    """
    def __init__(self,bid,ask):
        self.bid=bid
        self.ask=ask

    def update_bid_ask(self,new_bid,new_ask):
        self.bid=new_bid
        self.ask=new_ask
