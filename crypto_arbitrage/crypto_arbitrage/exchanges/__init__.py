from .binance import BinanceExchange
from .bybit import BybitExchange
from .kucoin import KuCoinExchange
from .mexc import MEXCExchange
from .okx import OKXExchange
from .htx import HTXExchange
from .bitget import BitgetExchange
from .bingx import BingXExchange
from .gate import GateExchange
from .lbank import LBankExchange
from .coinw import CoinWExchange


def get_exchange(exchange_name: str):
    exchange_classes = {
        'binance': BinanceExchange,
        'bybit': BybitExchange,
        'kucoin': KuCoinExchange,
        'mexc': MEXCExchange,
        'okx': OKXExchange,
        'htx': HTXExchange,
        'bitget': BitgetExchange,
        'bingx': BingXExchange,
        'gate': GateExchange,
        'lbank': LBankExchange,
        'coinw': CoinWExchange
    }

    if exchange_name.lower() not in exchange_classes:
        raise ValueError(f"Unsupported exchange: {exchange_name}")

    return exchange_classes[exchange_name.lower()]()