import os
import logging
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List, Tuple

from src.providers.mock_provider import MockCryptoProvider
from src.providers.crypto_market_provider import CryptoMarketProvider


def get_market_data(symbol: str) -> Dict[str, Any]:
    """Get current market data for a cryptocurrency."""
    try:
        if os.getenv('COINMARKETCAP_API_KEY'):
            provider = CryptoMarketProvider()
        else:
            logging.info("Using mock provider for market data")
            provider = MockCryptoProvider()

        return provider.get_market_data(symbol)
    except Exception as e:
        raise Exception(f"Failed to get market data: {str(e)}")


def get_price_data(symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    """Get historical price data for a cryptocurrency."""
    try:
        if os.getenv('COINMARKETCAP_API_KEY'):
            provider = CryptoMarketProvider()
        else:
            logging.info("Using mock provider for price data")
            provider = MockCryptoProvider()

        prices = provider.get_price_data(symbol, start_date, end_date)
        return prices_to_df(prices)
    except Exception as e:
        raise Exception(f"Failed to get price data: {str(e)}")


def prices_to_df(prices: List[Dict[str, Any]]) -> pd.DataFrame:
    """Convert price data to pandas DataFrame."""
    try:
        df = pd.DataFrame(prices)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        return df
    except Exception as e:
        raise Exception(f"Error converting prices to DataFrame: {str(e)}")


def get_supported_cryptocurrencies() -> Dict[str, str]:
    """Get list of supported cryptocurrencies."""
    try:
        if os.getenv('COINMARKETCAP_API_KEY'):
            provider = CryptoMarketProvider()
        else:
            logging.info("Using mock provider for cryptocurrency list")
            provider = MockCryptoProvider()

        return provider.get_supported_cryptocurrencies()
    except Exception as e:
        raise Exception(f"Failed to get supported cryptocurrencies: {str(e)}")


def calculate_confidence_level(signals: Dict[str, float]) -> float:
    """Calculate confidence level based on signal differences."""
    sma_diff_prev = abs(signals["sma_5_prev"] - signals["sma_20_prev"])
    sma_diff_curr = abs(signals["sma_5_curr"] - signals["sma_20_curr"])
    diff_change = sma_diff_curr - sma_diff_prev
    confidence = min(max(diff_change / signals["current_price"], 0), 1)
    return confidence


def calculate_macd(prices_df: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
    """Calculate MACD and signal line."""
    ema_12 = prices_df["close"].ewm(span=12, adjust=False).mean()
    ema_26 = prices_df["close"].ewm(span=26, adjust=False).mean()
    macd_line = ema_12 - ema_26
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    return macd_line, signal_line


def calculate_rsi(prices_df: pd.DataFrame, period: int = 14) -> pd.Series:
    """Calculate Relative Strength Index."""
    delta = prices_df["close"].diff()
    gain = (delta.where(delta > 0, 0)).fillna(0)
    loss = (-delta.where(delta < 0, 0)).fillna(0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def calculate_bollinger_bands(prices_df: pd.DataFrame, window: int = 20) -> Tuple[pd.Series, pd.Series]:
    """Calculate Bollinger Bands."""
    sma = prices_df["close"].rolling(window).mean()
    std_dev = prices_df["close"].rolling(window).std()
    upper_band = sma + (std_dev * 2)
    lower_band = sma - (std_dev * 2)
    return upper_band, lower_band


def calculate_obv(prices_df: pd.DataFrame) -> pd.Series:
    """Calculate On-Balance Volume."""
    obv = [0]
    for i in range(1, len(prices_df)):
        if prices_df["close"].iloc[i] > prices_df["close"].iloc[i - 1]:
            obv.append(obv[-1] + prices_df["volume"].iloc[i])
        elif prices_df["close"].iloc[i] < prices_df["close"].iloc[i - 1]:
            obv.append(obv[-1] - prices_df["volume"].iloc[i])
        else:
            obv.append(obv[-1])
    prices_df["OBV"] = obv
    return prices_df["OBV"]
