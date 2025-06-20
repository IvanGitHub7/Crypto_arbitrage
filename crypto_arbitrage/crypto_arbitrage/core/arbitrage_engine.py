import asyncio
import aiohttp
import ccxt.async_support as ccxt
from typing import List, Dict, Optional


class ArbitrageEngine:
    def __init__(self):
        self.exchanges_config = self._load_exchanges_config()
        self.active_exchanges = {}
        self.analysis_types = {
            'spot_spot': True,
            'spot_futures': False,
            'futures_futures': False
        }

    def _load_exchanges_config(self):
        """Конфигурация поддерживаемых бирж"""
        return {
            'Binance': {
                'ccxt_name': 'binance',
                'fee': {'spot': 0.075, 'futures': 0.04}
            },
            'KuCoin': {
                'ccxt_name': 'kucoin',
                'fee': {'spot': 0.08, 'futures': 0.06}
            },
            'Bybit': {
                'ccxt_name': 'bybit',
                'fee': {'spot': 0.06, 'futures': 0.06}
            },
            'Mexc': {
                'ccxt_name': 'mexc',
                'fee': {'spot': 0.2, 'futures': 0.06}
            },
            'Okx': {
                'ccxt_name': 'okx',
                'fee': {'spot': 0.08, 'futures': 0.05}
            },
            'Htx': {
                'ccxt_name': 'htx',
                'fee': {'spot': 0.2, 'futures': 0.05}
            },
            'Bitget': {
                'ccxt_name': 'bitget',
                'fee': {'spot': 0.1, 'futures': 0.06}
            },
            'Bingx': {
                'ccxt_name': 'bingx',
                'fee': {'spot': 0.04, 'futures': 0.04}
            },
            'Gate': {
                'ccxt_name': 'gate',
                'fee': {'spot': 0.075, 'futures': 0.04}
            },
            'Lbank': {
                'ccxt_name': 'lbank',
                'fee': {'spot': 0.08, 'futures': 0.08}
            },
            'Coinw': {
                'ccxt_name': 'coinw',
                'fee': {'spot': 0.2, 'futures': 0.2}
            }
        }

    def set_exchanges(self, exchange_names: List[str]):
        """Активация выбранных бирж"""
        self.active_exchanges = {
            name: config
            for name, config in self.exchanges_config.items()
            if name in exchange_names
        }

    def set_analysis_types(self, spot_spot: bool, spot_futures: bool, futures_futures: bool):
        """Установка типов анализа"""
        self.analysis_types = {
            'spot_spot': spot_spot,
            'spot_futures': spot_futures,
            'futures_futures': futures_futures
        }

    async def _find_opportunities(self, all_prices: Dict, min_profit: float, max_profit: float, investment: float) -> \
    List[Dict]:
        """Поиск арбитражных возможностей с подробным логгированием"""
        opportunities = []
        total_checked = 0
        profitable_pairs = 0

        for symbol, prices in all_prices.items():
            if len(prices) < 2:
                continue

            for i in range(len(prices)):
                for j in range(len(prices)):
                    if i == j:
                        continue

                    buy = prices[i]
                    sell = prices[j]
                    total_checked += 1

                    # Логируем проверяемую пару
                    print(f"\nChecking pair: {symbol}")
                    print(f"Buy: {buy['exchange']} {buy['market_type']} {buy['bid']}")
                    print(f"Sell: {sell['exchange']} {sell['market_type']} {sell['ask']}")

                    if not self._valid_arbitrage_pair(buy, sell):
                        print("Skipped - invalid pair type")
                        continue

                    spread = sell['ask'] - buy['bid']
                    if spread <= 0:
                        print(f"Skipped - negative spread: {spread}")
                        continue

                    spread_percent = (spread / buy['bid']) * 100
                    print(f"Raw spread: {spread_percent:.4f}%")

                    if not (min_profit <= spread_percent <= max_profit):
                        print(f"Skipped - spread {spread_percent:.2f}% not in range {min_profit}-{max_profit}%")
                        continue

                    buy_fee = self.active_exchanges[buy['exchange']]['fee'][buy['market_type']]
                    sell_fee = self.active_exchanges[sell['exchange']]['fee'][sell['market_type']]

                    coins = investment / buy['bid']
                    revenue = coins * sell['ask']
                    fee_amount = (investment * buy_fee / 100) + (revenue * sell_fee / 100)
                    profit = revenue - investment - fee_amount

                    print(f"After fees: {profit:.2f} profit ({profit / investment * 100:.2f}%)")

                    if profit > 0:
                        profitable_pairs += 1
                        opportunities.append({
                            'symbol': f"{symbol}/USDT",
                            'buy_exchange': buy['exchange'],
                            'sell_exchange': sell['exchange'],
                            'buy_market_type': buy['market_type'],
                            'sell_market_type': sell['market_type'],
                            'buy_price': buy['bid'],
                            'sell_price': sell['ask'],
                            'spread_percent': spread_percent,
                            'profit_amount': profit,
                            'investment': investment
                        })

        print(f"\nTotal pairs checked: {total_checked}")
        print(f"Profitable opportunities found: {profitable_pairs}")
        return sorted(opportunities, key=lambda x: -x['spread_percent'])

    async def _fetch_all_prices(self) -> Dict:
        """Получение цен со всех бирж"""
        all_prices = {}

        for name, config in self.active_exchanges.items():
            if 'instance' not in config:
                continue

            if self.analysis_types['spot_spot'] or self.analysis_types['spot_futures']:
                spot_prices = await self._fetch_ccxt_prices(name, 'spot')
                self._merge_prices(all_prices, spot_prices)

            if self.analysis_types['spot_futures'] or self.analysis_types['futures_futures']:
                futures_prices = await self._fetch_ccxt_prices(name, 'futures')
                self._merge_prices(all_prices, futures_prices)

        return all_prices

    async def _fetch_ccxt_prices(self, exchange_name: str, market_type: str) -> Dict:
        """Логируем процесс загрузки цен"""
        logger.log(f"\nFetching {market_type} prices from {exchange_name}...")
        try:
            tickers = await self.active_exchanges[exchange_name]['instance'].fetch_tickers()
            logger.log(f"Received {len(tickers)} tickers")

            prices = {}
            for symbol, ticker in list(tickers.items())[:10]:  # Логируем первые 10
                bid = ticker.get('bid')
                ask = ticker.get('ask')
                logger.log(f"{symbol}: bid={bid}, ask={ask}")

                if self._valid_prices(bid, ask):
                    normalized = self._normalize_symbol(symbol, market_type)
                    prices[normalized] = {
                        'exchange': exchange_name,
                        'bid': bid,
                        'ask': ask,
                        'market_type': market_type,
                        'original': symbol
                    }

            logger.log(f"Valid prices found: {len(prices)}")
            return prices
        except Exception as e:
            logger.log(f"Error fetching prices: {str(e)}")
            return {}

    def _merge_prices(self, all_prices: Dict, new_prices: Dict):
        """Объединение цен в общий словарь"""
        for symbol, data in new_prices.items():
            if symbol not in all_prices:
                all_prices[symbol] = []
            all_prices[symbol].append(data)

    async def _find_opportunities(self, all_prices: Dict, min_profit: float, max_profit: float, investment: float) -> \
    List[Dict]:
        """Упрощенный и более агрессивный поиск арбитража"""
        opportunities = []

        for symbol, prices in all_prices.items():
            if len(prices) < 2:
                continue

            # Находим лучшую цену покупки (минимальную)
            best_buy = min(prices, key=lambda x: x['bid'])

            # Находим лучшую цену продажи (максимальную)
            best_sell = max(prices, key=lambda x: x['ask'])

            # Проверяем, что это разные биржи
            if best_buy['exchange'] == best_sell['exchange']:
                continue

            spread = best_sell['ask'] - best_buy['bid']
            spread_percent = (spread / best_buy['bid']) * 100

            # Временно убираем проверку на min_profit для теста
            if spread_percent <= 0:
                continue

            # Расчет прибыли без учета комиссий для теста
            profit = (investment / best_buy['bid']) * best_sell['ask'] - investment

            opportunities.append({
                'symbol': f"{symbol}/USDT",
                'buy_exchange': best_buy['exchange'],
                'sell_exchange': best_sell['exchange'],
                'buy_market_type': best_buy['market_type'],
                'sell_market_type': best_sell['market_type'],
                'buy_price': best_buy['bid'],
                'sell_price': best_sell['ask'],
                'spread_percent': spread_percent,
                'profit_amount': profit,
                'investment': investment
            })

        return sorted(opportunities, key=lambda x: -x['spread_percent'])

    def _valid_arbitrage_pair(self, buy: Dict, sell: Dict) -> bool:
        """Упрощенная проверка валидности арбитражной пары"""
        # Основное правило - покупаем дешевле, чем продаем
        if buy['bid'] >= sell['ask']:
            return False

        # Проверяем разрешенные типы арбитража
        if buy['market_type'] == 'spot' and sell['market_type'] == 'spot':
            return self.analysis_types['spot_spot']
        if buy['market_type'] == 'spot' and sell['market_type'] == 'futures':
            return self.analysis_types['spot_futures']
        if buy['market_type'] == 'futures' and sell['market_type'] == 'futures':
            return self.analysis_types['futures_futures']

        return False

    def _valid_prices(self, bid: float, ask: float) -> bool:
        """Проверка валидности цен"""
        return bid and ask and bid > 0 and ask > 0 and bid < ask

    def _is_futures_symbol(self, symbol: str) -> bool:
        """Проверка фьючерсного символа"""
        return any(x in symbol for x in ['/USDT:USDT', '/USDT', 'PERP'])

    def _normalize_symbol(self, symbol: str, market_type: str) -> str:
        """Нормализация названия символа"""
        symbol = symbol.upper()
        if market_type == 'futures':
            for suffix in ['PERP', 'USDT:USDT', 'USDT']:
                if symbol.endswith(suffix):
                    symbol = symbol[:-len(suffix)]
                    break
        return symbol.replace('/', '')

    async def _close_exchanges(self):
        """Закрытие соединений с биржами"""
        for config in self.active_exchanges.values():
            if 'instance' in config:
                await config['instance'].close()