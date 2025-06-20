from .base_exchange import BaseExchange
from typing import Dict


class MEXCExchange(BaseExchange):
    def __init__(self):
        super().__init__('mexc')

    async def get_spot_prices(self) -> Dict[str, Dict]:
        url = self.config['spot_url']
        data = await self.fetch_data(url)

        prices = {}
        for ticker in data:
            try:
                symbol = ticker['symbol']
                bid_price = float(ticker['bidPrice'])
                ask_price = float(ticker['askPrice'])

                if bid_price <= 0 or ask_price <= 0 or bid_price >= ask_price:
                    continue

                normalized = self.normalize_pair(symbol, 'spot')
                prices[normalized] = {
                    'exchange': self.name,
                    'bid': bid_price,
                    'ask': ask_price,
                    'bid_volume': float(ticker.get('bidQty', 0)),
                    'ask_volume': float(ticker.get('askQty', 0)),
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
        if 'data' in data:
            for ticker in data['data']:
                try:
                    symbol = ticker['symbol']
                    bid_price = float(ticker['bid1'])
                    ask_price = float(ticker['ask1'])

                    if bid_price <= 0 or ask_price <= 0 or bid_price >= ask_price:
                        continue

                    normalized = self.normalize_pair(symbol, 'futures')
                    prices[normalized] = {
                        'exchange': self.name,
                        'bid': bid_price,
                        'ask': ask_price,
                        'bid_volume': float(ticker.get('bid1Vol', 0)),
                        'ask_volume': float(ticker.get('ask1Vol', 0)),
                        'original': symbol,
                        'market_type': 'futures'
                    }
                except (KeyError, ValueError) as e:
                    continue
        return prices