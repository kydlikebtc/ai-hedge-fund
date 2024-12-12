"""
Cryptocurrency Market Data Provider

This module provides cryptocurrency market data using multiple data sources.
Specializes in historical cryptocurrency price and volume data retrieval with support
for major cryptocurrencies like BTC, ETH, and others.

Features:
- Historical cryptocurrency price and volume data
- Automatic USD pair handling for crypto assets
- Built-in error handling and logging
- CoinMarketCap-compatible data format
"""
from datetime import datetime, timedelta
import logging
import yfinance as yf
from typing import Dict, Any

from .base import BaseProvider


class CryptoMarketProvider(BaseProvider):
    """
    Provider for historical cryptocurrency market data.

    Fetches and processes cryptocurrency price data with automatic USD pair handling.
    Returns data in a format compatible with CoinMarketCap API structure for
    seamless integration with other components.
    """

    def __init__(self):
        """Initialize the cryptocurrency data provider."""
        self.logger = logging.getLogger(__name__)
        super().__init__()

    def _initialize_provider(self) -> None:
        """Initialize the cryptocurrency data provider."""
        # No API keys required for basic crypto price data
        self.logger.info("Initialized cryptocurrency market data provider")

    def get_historical_prices(self, symbol: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """
        Get historical price data for a cryptocurrency.

        Retrieves historical price and volume data for any cryptocurrency pair
        against USD. Automatically handles cryptocurrency symbol formatting by
        appending -USD suffix for proper pair querying.

        Args:
            symbol: The cryptocurrency symbol (e.g., 'BTC', 'ETH')
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            dict: Historical price and volume data in CoinMarketCap-compatible format
                 with the following structure:
                 {
                     'data': {
                         'BTC': {
                             'quote': {
                                 'USD': {
                                     'prices': {'2024-01-01': 42000.00, ...},
                                     'volumes': {'2024-01-01': 1234567.89, ...}
                                 }
                             }
                         }
                     }
                 }
        """
        try:
            # Parse dates
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            # Add one day to end_date to make it inclusive
            adjusted_end = (end_dt + timedelta(days=1)).strftime('%Y-%m-%d')

            self.logger.info(f"Fetching {symbol} cryptocurrency data from {start_date} to {adjusted_end}")

            # Create ticker with -USD suffix for crypto pairs
            ticker = yf.Ticker(f"{symbol}-USD")

            # Get historical data with adjusted end date
            df = ticker.history(start=start_date, end=adjusted_end)

            if df.empty:
                raise ValueError(f"No cryptocurrency data returned for {symbol} in date range")

            # Convert dates to string format
            dates = df.index.strftime('%Y-%m-%d').tolist()
            prices = df['Close'].tolist()
            volumes = df['Volume'].tolist()

            self.logger.info(f"Retrieved {len(dates)} days of data")
            self.logger.debug(f"Date range: {dates[0]} to {dates[-1]}")

            # Format data to match CoinMarketCap structure
            return {
                'data': {
                    symbol: {
                        'quote': {
                            'USD': {
                                'prices': dict(zip(dates, prices)),
                                'volumes': dict(zip(dates, volumes))
                            }
                        }
                    }
                }
            }
        except Exception as e:
            self.logger.error(f"Error fetching cryptocurrency historical prices: {e}")
            raise
