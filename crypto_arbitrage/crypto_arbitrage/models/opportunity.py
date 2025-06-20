from dataclasses import dataclass
from typing import Optional


@dataclass
class ArbitrageOpportunity:
    symbol: str
    buy_exchange: str
    sell_exchange: str
    buy_price: float
    sell_price: float
    buy_market_type: str
    sell_market_type: str
    spread_percent: float
    profit_amount: float
    investment: float
    buy_volume: Optional[float] = None
    sell_volume: Optional[float] = None
    buy_fee: Optional[float] = None
    sell_fee: Optional[float] = None

    def to_dict(self) -> dict:
        return {
            'symbol': self.symbol,
            'buy_exchange': self.buy_exchange,
            'sell_exchange': self.sell_exchange,
            'buy_price': self.buy_price,
            'sell_price': self.sell_price,
            'buy_market_type': self.buy_market_type,
            'sell_market_type': self.sell_market_type,
            'spread_percent': self.spread_percent,
            'profit_amount': self.profit_amount,
            'investment': self.investment,
            'buy_volume': self.buy_volume,
            'sell_volume': self.sell_volume,
            'buy_fee': self.buy_fee,
            'sell_fee': self.sell_fee
        }