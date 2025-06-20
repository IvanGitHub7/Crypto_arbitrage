from .base_exchange import BaseExchange
from typing import Dict


class HTXExchange(BaseExchange):
    def __init__(self):
        super().__init__('htx')

    async def get_spot_prices(self) -> Dict[str, Dict]:
        url = self.config['spot_url']
        data = await self.fetch_data(url)

        prices = {}
        if 'data' in data:
            for ticker in data['data']:
                try:
                    symbol = ticker['symbol']
                    bid_price = float(ticker['bid'])
                    ask_price = float(ticker['ask'])

                    if bid_price <= 0 or ask_price <= 0 or bid_price >= ask_price:
                        continue

                    normalized = self.normalize_pair(symbol, 'spot')
                    prices[normalized] = {
                        'exchange': self.name,
                        'bid': bid_price,
                        'ask': ask_price,
                        'bid_volume': float(ticker.get('bidSize', 0)),
                        'ask_volume': float(ticker.get('askSize', 0)),
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
        if 'tick' in data:
            for ticker in data['tick']:
                try:
                    symbol = ticker['symbol']
                    bid_price = float(ticker['bid'][0])
                    ask_price = float(ticker['ask'][0])

                    if bid_price <= 0 or ask_price <= 0 or bid_price >= ask_price:
                        continue

                    normalized = self.normalize_pair(symbol, 'futures')
                    prices[normalized] = {
                        'exchange': self.name,
                        'bid': bid_price,
                        'ask': ask_price,
                        'bid_volume': float(ticker.get('bidVol', [0])[0]),
                        'ask_volume': float(ticker.get('askVol', [0])[0]),
                        'original': symbol,
                        'market_type': 'futures'
                    }
                except (KeyError, ValueError) as e:
                    continue
        return prices