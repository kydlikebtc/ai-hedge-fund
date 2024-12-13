import os
import logging
import pandas as pd
import aiohttp
from datetime import datetime
from typing import Dict, Any, List, Tuple

from src.providers.mock_provider import MockCryptoProvider
from src.providers.crypto_market_provider import CryptoMarketProvider


class CMCClient:
    """CoinMarketCap API client."""

    def __init__(self):
        self.api_key = os.getenv('COINMARKETCAP_API_KEY')
        if not self.api_key:
            raise ValueError("COINMARKETCAP_API_KEY environment variable not set")
        self.base_url = "https://pro-api.coinmarketcap.com/v1"
        self.headers = {
            'X-CMC_PRO_API_KEY': self.api_key,
            'Accept': 'application/json'
        }

    async def _make_request(self, endpoint: str, params: Dict = None) -> Dict[str, Any]:
        """Make an async request to the CoinMarketCap API."""
        url = f"{self.base_url}/{endpoint}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers, params=params) as response:
                if response.status != 200:
                    raise Exception(f"API request failed: {await response.text()}")
                return await response.json()

    async def get_market_data(self, symbol: str) -> Dict[str, Any]:
        """Get current market data for a cryptocurrency."""
        endpoint = "cryptocurrency/quotes/latest"
        params = {'symbol': symbol, 'convert': 'USD'}
        return await self._make_request(endpoint, params)

    async def get_historical_prices(self, symbol: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get historical price data for a cryptocurrency."""
        endpoint = "cryptocurrency/quotes/historical"
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        params = {
            'symbol': symbol,
            'time_start': start.strftime("%Y-%m-%dT00:00:00Z"),
            'time_end': end.strftime("%Y-%m-%dT23:59:59Z"),
            'convert': 'USD'
        }
        return await self._make_request(endpoint, params)

    async def get_available_cryptocurrencies(self) -> Dict[str, Any]:
        """Get list of available cryptocurrencies."""
        endpoint = "cryptocurrency/map"
        params = {'limit': 100, 'sort': 'cmc_rank'}
        return await self._make_request(endpoint, params)


async def get_market_data(symbol: str) -> Dict[str, Any]:
    """Get current market data for a cryptocurrency."""
    try:
        if os.getenv('COINMARKETCAP_API_KEY'):
            provider = CryptoMarketProvider()
        else:
            logging.info("Using mock provider for market data")
            provider = MockCryptoProvider()

        return await provider.get_market_data(symbol)
    except Exception as e:
        raise Exception(f"Failed to get market data: {str(e)}")


async def get_price_data(symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    """Get historical price data for a cryptocurrency."""
    try:
        if os.getenv('COINMARKETCAP_API_KEY'):
            provider = CryptoMarketProvider()
        else:
            logging.info("Using mock provider for price data")
            provider = MockCryptoProvider()

        prices = await provider.get_price_data(symbol, start_date, end_date)
        return prices_to_df(prices)
    except Exception as e:
        raise Exception(f"Failed to get price data: {str(e)}")


def prices_to_df(price_data: Dict[str, Any]) -> pd.DataFrame:
    """Convert price data to DataFrame format."""
    try:
        if not isinstance(price_data, dict):
            raise ValueError("Price data must be a dictionary")

        if isinstance(price_data, dict) and 'price_data' in price_data:
            df = price_data['price_data']
            if isinstance(df, pd.DataFrame):
                return df.copy()

        if isinstance(price_data, dict) and 'data' in price_data:
            symbol_data = list(price_data['data'].values())[0]
            if 'quotes' in symbol_data:
                quotes = symbol_data['quotes']
                rows = []
                for quote in quotes:
                    usd_data = quote['quote']['USD']
                    row = {
                        'timestamp': quote['timestamp'],
                        'open': usd_data['open'],
                        'high': usd_data['high'],
                        'low': usd_data['low'],
                        'close': usd_data['close'],
                        'volume': usd_data['volume']
                    }
                    rows.append(row)
                df = pd.DataFrame(rows)
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df.set_index('timestamp', inplace=True)
                df.sort_index(inplace=True)
                return df

        raise ValueError("Unsupported price data format")
    except Exception as e:
        raise Exception(f"Error converting prices to DataFrame: {str(e)}")


async def get_supported_cryptocurrencies() -> List[Dict[str, str]]:
    """Get list of supported cryptocurrencies."""
    try:
        if os.getenv('COINMARKETCAP_API_KEY'):
            provider = CryptoMarketProvider()
        else:
            logging.info("Using mock provider for cryptocurrency list")
            provider = MockCryptoProvider()

        cryptos = await provider.get_supported_cryptocurrencies()
        return [
            {"symbol": symbol, "name": name}
            for symbol, name in cryptos.items()
        ]
    except Exception as e:
        raise Exception(f"Failed to get supported cryptocurrencies: {str(e)}")


def calculate_confidence_level(df: pd.DataFrame) -> float:
    """Calculate confidence level based on technical indicators."""
    try:
        rsi = calculate_rsi(df)
        macd_line, signal_line = calculate_macd(df)
        return float(rsi.iloc[-1])
    except Exception as e:
        raise Exception(f"Error calculating confidence level: {str(e)}")


def calculate_macd(df: pd.DataFrame, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9) -> Tuple[pd.Series, pd.Series]:
    """Calculate MACD (Moving Average Convergence Divergence)."""
    try:
        fast_ema = df['close'].ewm(span=fast_period, adjust=False).mean()
        slow_ema = df['close'].ewm(span=slow_period, adjust=False).mean()
        macd_line = fast_ema - slow_ema
        signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
        return macd_line, signal_line
    except Exception as e:
        raise Exception(f"Error calculating MACD: {str(e)}")


def calculate_rsi(df: pd.DataFrame, periods: int = 14) -> pd.Series:
    """Calculate RSI (Relative Strength Index)."""
    try:
        close_delta = df['close'].diff()
        gains = close_delta.where(close_delta > 0, 0.0)
        losses = -close_delta.where(close_delta < 0, 0.0)
        avg_gains = gains.rolling(window=periods, min_periods=1).mean()
        avg_losses = losses.rolling(window=periods, min_periods=1).mean()
        rs = avg_gains / avg_losses
        rsi = 100.0 - (100.0 / (1.0 + rs))
        return rsi.fillna(50.0)
    except Exception as e:
        raise Exception(f"Error calculating RSI: {str(e)}")


def calculate_bollinger_bands(df: pd.DataFrame, window: int = 20) -> Tuple[pd.Series, pd.Series]:
    """Calculate Bollinger Bands."""
    try:
        sma = df['close'].rolling(window=window).mean()
        std = df['close'].rolling(window=window).std()
        upper_band = sma + (std * 2)
        lower_band = sma - (std * 2)
        return upper_band.fillna(method='bfill'), lower_band.fillna(method='bfill')
    except Exception as e:
        raise Exception(f"Error calculating Bollinger Bands: {str(e)}")


def calculate_obv(df: pd.DataFrame) -> pd.Series:
    """Calculate On-Balance Volume (OBV)."""
    try:
        obv = pd.Series(index=df.index, dtype=float)
        obv.iloc[0] = 0
        for i in range(1, len(df)):
            if df['close'].iloc[i] > df['close'].iloc[i-1]:
                obv.iloc[i] = obv.iloc[i-1] + df['volume'].iloc[i]
            elif df['close'].iloc[i] < df['close'].iloc[i-1]:
                obv.iloc[i] = obv.iloc[i-1] - df['volume'].iloc[i]
            else:
                obv.iloc[i] = obv.iloc[i-1]
        return obv
    except Exception as e:
        raise Exception(f"Error calculating OBV: {str(e)}")
