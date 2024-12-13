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

        Raises:
            ValueError: If no data is returned or date validation fails
            Exception: For other API or processing errors
        """
        try:
            # Validate dates
            try:
                start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                end_dt = datetime.strptime(end_date, '%Y-%m-%d')
                if start_dt > end_dt:
                    raise ValueError("Start date must be before end date")
                if end_dt > datetime.now():
                    raise ValueError("End date cannot be in the future")
            except ValueError as e:
                self.logger.error(f"Date validation failed: {e}")
                raise

            # Validate cryptocurrency symbol
            from src.tools import CMCClient
            client = CMCClient()
            try:
                available_cryptos = client.get_available_cryptocurrencies()
                valid_symbols = [crypto['symbol'] for crypto in available_cryptos['data']]
                if symbol.upper() not in valid_symbols:
                    raise ValueError(f"Invalid cryptocurrency symbol: {symbol}. Please use one of the supported symbols from CoinMarketCap.")
            except Exception as e:
                self.logger.error(f"Symbol validation failed: {e}")
                raise ValueError(f"Failed to validate cryptocurrency symbol: {str(e)}")

            self.logger.info(f"Fetching {symbol} cryptocurrency data from {start_date} to {end_date}")

            # Initialize CMC client for data fetching
            # Note: We reuse the client from symbol validation
            if not client:
                client = CMCClient()

            # Get historical data with adjusted end date
            try:
                response = client.get_historical_prices(symbol, start_date, end_date)
            except Exception as e:
                self.logger.error(f"CMC API error: {str(e)}")
                raise ValueError(f"Failed to fetch data from CoinMarketCap API: {str(e)}")

            # Validate response structure
            if not response or 'data' not in response:
                raise ValueError(f"Invalid response format from CoinMarketCap API for {symbol}")

            if symbol not in response['data']:
                raise ValueError(f"No data found for symbol {symbol} in response")

            if 'quote' not in response['data'][symbol]:
                raise ValueError(f"Missing quote data for {symbol}")

            if 'USD' not in response['data'][symbol]['quote']:
                raise ValueError(f"Missing USD quote data for {symbol}")

            # Extract price and volume data from CMC response
            quote_data = response['data'][symbol]['quote']['USD']

            if 'prices' not in quote_data or 'volumes' not in quote_data:
                raise ValueError(f"Missing price or volume data for {symbol}")

            dates = list(quote_data['prices'].keys())
            prices = list(quote_data['prices'].values())
            volumes = list(quote_data['volumes'].values())

            if not dates or not prices or not volumes:
                raise ValueError(f"Empty price or volume data for {symbol}")

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
