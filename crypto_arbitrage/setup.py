from setuptools import setup, find_packages

setup(
    name="crypto_arbitrage",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'aiohttp',
        'PyQt6',
        'ccxt',
    ],
)