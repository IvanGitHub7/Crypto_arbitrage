from .base_exchange import BaseExchange
from typing import Dict


class LBankExchange(BaseExchange):
    def __init__(self):
        super().__init__('lbank')

    async def get_spot_prices(self) -> Dict[str, Dict]:
        url = self.config['spot_url']
        data = await self.fetch_data(url)

        prices = {}
        for ticker in data:
            try:
                symbol = ticker['symbol']
                ticker_data = ticker['ticker']
                bid_price = float(ticker_data['bid'])
                ask_price = float(ticker_data['ask'])

                if bid_price <= 0 or ask_price <= 0 or bid_price >= ask_price:
                    continue

                normalized = self.normalize_pair(symbol, 'spot')
                prices[normalized] = {
                    'exchange': self.name,
                    'bid': bid_price,
                    'ask': ask_price,
                    'bid_volume': float(ticker_data.get('bidVol', 0)),
                    'ask_volume': float(ticker_data.get('askVol', 0)),
                    'original': symbol,
                    'market_type': 'spot'
                }
            except (KeyError, ValueError) as e:
                continue
        return prices

    async def get_futures_prices(self) -> Dict[str, Dict]:
        # LBank не поддерживает фьючерсы через API
        return {}