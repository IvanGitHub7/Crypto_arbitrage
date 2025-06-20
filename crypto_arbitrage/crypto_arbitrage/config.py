import os
from typing import Dict, Any, List


class Config:
    # Общие настройки
    REQUEST_TIMEOUT = 30
    MAX_CONCURRENT_REQUESTS = 10
    RETRY_COUNT = 3
    RETRY_DELAY = 1.0
    MIN_PROFIT_PERCENT = 0.5
    MAX_PROFIT_PERCENT = 10.0
    DEFAULT_INVESTMENT = 1000.0

    # Настройки кэша
    CACHE_ENABLED = True
    CACHE_TTL = 300  # 5 минут в секундах

    # Настройки бирж
    ENABLED_EXCHANGES: List[str] = [
        'binance',
        'bybit',
        'kucoin',
        'mexc',
        'okx',
        'htx',
        'bitget',
        'bingx',
        'gate',
        'lbank',
        'coinw'
    ]

    EXCHANGE_CONFIGS: Dict[str, Dict[str, Any]] = {
        'binance': {
            'spot_url': 'https://api.binance.com/api/v3/ticker/bookTicker',
            'futures_url': 'https://fapi.binance.com/fapi/v1/ticker/bookTicker',
            'fee': {'spot': 0.075, 'futures': 0.04},
            'rate_limit': 10,
            'ccxt_name': 'binance',
            'enabled': True
        },
        'bybit': {
            'spot_url': 'https://api.bybit.com/v5/market/tickers?category=spot',
            'futures_url': 'https://api.bybit.com/v5/market/tickers?category=linear',
            'fee': {'spot': 0.06, 'futures': 0.06},
            'rate_limit': 5,
            'ccxt_name': 'bybit',
            'enabled': True
        },
        'kucoin': {
            'spot_url': 'https://api.kucoin.com/api/v1/market/allTickers',
            'futures_url': 'https://api-futures.kucoin.com/api/v1/ticker',
            'fee': {'spot': 0.08, 'futures': 0.06},
            'rate_limit': 5,
            'ccxt_name': 'kucoin',
            'enabled': True
        },
        'mexc': {
            'spot_url': 'https://api.mexc.com/api/v3/ticker/bookTicker',
            'futures_url': 'https://contract.mexc.com/api/v1/contract/ticker',
            'fee': {'spot': 0.2, 'futures': 0.06},
            'rate_limit': 5,
            'ccxt_name': 'mexc',
            'enabled': True
        },
        'okx': {
            'spot_url': 'https://www.okx.com/api/v5/market/tickers?instType=SPOT',
            'futures_url': 'https://www.okx.com/api/v5/market/tickers?instType=FUTURES',
            'fee': {'spot': 0.08, 'futures': 0.05},
            'rate_limit': 5,
            'ccxt_name': 'okx',
            'enabled': True
        },
        'htx': {
            'spot_url': 'https://api.huobi.pro/market/tickers',
            'futures_url': 'https://api.htx.com/market/tickers',
            'fee': {'spot': 0.2, 'futures': 0.05},
            'rate_limit': 5,
            'ccxt_name': 'htx',
            'enabled': True
        },
        'bitget': {
            'spot_url': 'https://api.bitget.com/api/spot/v1/market/tickers',
            'futures_url': 'https://api.bitget.com/api/mix/v1/market/tickers?productType=UMCBL',
            'fee': {'spot': 0.1, 'futures': 0.06},
            'rate_limit': 5,
            'ccxt_name': 'bitget',
            'enabled': True
        },
        'bingx': {
            'spot_url': 'https://open-api.bingx.com/openApi/spot/v1/ticker/24hr',
            'futures_url': 'https://open-api.bingx.com/openApi/swap/v2/quote/ticker',
            'fee': {'spot': 0.04, 'futures': 0.04},
            'rate_limit': 5,
            'ccxt_name': 'bingx',
            'enabled': True
        },
        'gate': {
            'spot_url': 'https://api.gateio.ws/api/v4/spot/tickers',
            'futures_url': 'https://api.gateio.ws/api/v4/futures/usdt/tickers',
            'fee': {'spot': 0.2, 'futures': 0.05},
            'rate_limit': 5,
            'ccxt_name': 'gateio',
            'enabled': True
        },
        'lbank': {
            'spot_url': 'https://api.lbkex.com/v1/ticker.do?symbol=all',
            'futures_url': None,
            'fee': {'spot': 0.08, 'futures': 0.08},
            'rate_limit': 5,
            'ccxt_name': None,
            'enabled': True
        },
        'coinw': {
            'spot_url': 'https://api.coinw.com/api/v1/public?command=returnTicker',
            'futures_url': None,
            'fee': {'spot': 0.2, 'futures': 0.2},
            'rate_limit': 5,
            'ccxt_name': None,
            'enabled': True
        }
    }

    @classmethod
    def get_enabled_exchanges(cls) -> List[str]:
        return [name for name in cls.ENABLED_EXCHANGES
                if cls.EXCHANGE_CONFIGS.get(name, {}).get('enabled', False)]

    @classmethod
    def get_exchange_config(cls, exchange_name: str) -> Dict[str, Any]:
        return cls.EXCHANGE_CONFIGS.get(exchange_name.lower(), {})


config = Config()