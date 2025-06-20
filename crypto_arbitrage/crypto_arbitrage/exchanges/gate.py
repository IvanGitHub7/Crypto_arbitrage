from .base_exchange import BaseExchange
from typing import Dict


class GateExchange(BaseExchange):
    def __init__(self):
        super().__init__('gate')

    async def get_spot_prices(self) -> Dict[str, Dict]:
        url = self.config['spot_url']
        data = await self.fetch_data(url)

        prices = {}
        for ticker in data:
            try:
                symbol = ticker['currency_pair']
                bid_price = float(ticker['highest_bid'])
                ask_price = float(ticker['lowest_ask'])

                if bid_price <= 0 or ask_price <= 0 or bid_price >= ask_price:
                    continue

                normalized = self.normalize_pair(symbol, 'spot')
                prices[normalized] = {
                    'exchange': self.name,
                    'bid': bid_price,
                    'ask': ask_price,
                    'bid_volume': 0,
                    'ask_volume': 0,
                    'original': symbol,
                    'market_type': 'spot'
                }
            except (KeyError, ValueError) as e:
                continue
        return prices

    async def get_futures_prices(self) -> Dict[str, Dict]:
        url = self.config['futures_url']
        data = await self.fetch_data(url)

        prices = {}
        for ticker in data:
            try:
                symbol = ticker['contract']
                bid_price = float(ticker['bid1_price'])
                ask_price = float(ticker['ask1_price'])

                if bid_price <= 0 or ask_price <= 0 or bid_price >= ask_price:
                    continue

                normalized = self.normalize_pair(symbol, 'futures')
                prices[normalized] = {
                    'exchange': self.name,
                    'bid': bid_price,
                    'ask': ask_price,
                    'bid_volume': float(ticker.get('bid1_size', 0)),
                    'ask_volume': float(ticker.get('ask1_size', 0)),
                    'original': symbol,
                    'market_type': 'futures'
                }
            except (KeyError, ValueError) as e:
                continue
        return prices