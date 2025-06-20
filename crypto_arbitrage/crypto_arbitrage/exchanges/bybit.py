from .base_exchange import BaseExchange
from typing import Dict


class BybitExchange(BaseExchange):
    def __init__(self):
        super().__init__('bybit')

    async def get_spot_prices(self) -> Dict[str, Dict]:
        url = self.config['spot_url']
        data = await self.fetch_data(url)

        prices = {}
        if 'result' in data and 'list' in data['result']:
            for ticker in data['result']['list']:
                try:
                    symbol = ticker['symbol']
                    bid_price = float(ticker['bid1Price'])
                    ask_price = float(ticker['ask1Price'])

                    if bid_price <= 0 or ask_price <= 0 or bid_price >= ask_price:
                        continue

                    normalized = self.normalize_pair(symbol, 'spot')
                    prices[normalized] = {
                        'exchange': self.name,
                        'bid': bid_price,
                        'ask': ask_price,
                        'bid_volume': float(ticker.get('bid1Size', 0)),
                        'ask_volume': float(ticker.get('ask1Size', 0)),
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
        if 'result' in data and 'list' in data['result']:
            for ticker in data['result']['list']:
                try:
                    symbol = ticker['symbol']
                    bid_price = float(ticker['bid1Price'])
                    ask_price = float(ticker['ask1Price'])

                    if bid_price <= 0 or ask_price <= 0 or bid_price >= ask_price:
                        continue

                    normalized = self.normalize_pair(symbol, 'futures')
                    prices[normalized] = {
                        'exchange': self.name,
                        'bid': bid_price,
                        'ask': ask_price,
                        'bid_volume': float(ticker.get('bid1Size', 0)),
                        'ask_volume': float(ticker.get('ask1Size', 0)),
                        'original': symbol,
                        'market_type': 'futures'
                    }
                except (KeyError, ValueError) as e:
                    continue
        return prices