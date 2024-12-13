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
from typing import Dict, Any, List

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

    async def _initialize_provider(self) -> None:
        """Initialize the cryptocurrency data provider."""
        # No API keys required for basic crypto price data
        self.logger.info("Initialized cryptocurrency market data provider")

    async def get_market_data(self, symbol: str) -> Dict[str, Any]:
        """Get current market data for a cryptocurrency."""
        try:
            # Initialize CMC client for data fetching
            from src.tools import CMCClient
            client = CMCClient()

            # Get current market data
            response = await client.get_market_data(symbol)
            if not response or 'data' not in response:
                raise ValueError(f"Invalid response format from CoinMarketCap API for {symbol}")

            return response
        except Exception as e:
            self.logger.error(f"Error fetching market data: {e}")
            raise

    async def get_price_data(self, symbol: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get historical price data for a cryptocurrency."""
        try:
            # Validate dates
            try:
                start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                end_dt = datetime.strptime(end_date, '%Y-%m-%d')
                current_dt = datetime.now()

                if start_dt > end_dt:
                    raise ValueError("Start date must be before end date")

                # Use mock provider for future dates
                if end_dt > current_dt:
                    self.logger.warning(f"Future date range requested for {symbol}, using mock provider")
                    from .mock_provider import MockCryptoProvider
                    mock_provider = MockCryptoProvider()
                    return await mock_provider.get_price_data(symbol, start_date, end_date)

            except ValueError as e:
                self.logger.error(f"Date validation failed: {e}")
                raise

            self.logger.info(f"Fetching {symbol} cryptocurrency data from {start_date} to {end_date}")

            try:
                # Initialize CMC client for historical data
                from src.tools import CMCClient
                client = CMCClient()
                response = await client.get_historical_prices(symbol, start_date, end_date)

                # Validate response structure
                if not response:
                    raise ValueError(f"Empty response from CoinMarketCap API for {symbol}")
                if 'data' not in response:
                    raise ValueError(f"Invalid response format from CoinMarketCap API for {symbol}: missing 'data' field")
                if 'status' in response and response['status'].get('error_code'):
                    error_msg = response['status'].get('error_message', 'Unknown error')
                    raise ValueError(f"CoinMarketCap API error: {error_msg}")

                return response

            except Exception as e:
                error_msg = str(e)
                if "subscription plan doesn't support this endpoint" in error_msg:
                    self.logger.warning(f"CMC API subscription limitation, falling back to mock provider")
                    from .mock_provider import MockCryptoProvider
                    mock_provider = MockCryptoProvider()
                    return await mock_provider.get_price_data(symbol, start_date, end_date)
                raise ValueError(f"Failed to fetch data from CoinMarketCap API: {error_msg}")

        except Exception as e:
            self.logger.error(f"Error fetching cryptocurrency historical prices: {e}")
            raise

    async def get_supported_cryptocurrencies(self) -> Dict[str, str]:
        """Get list of supported cryptocurrencies."""
        try:
            # Initialize CMC client
            from src.tools import CMCClient
            client = CMCClient()

            # Get supported cryptocurrencies
            response = await client.get_available_cryptocurrencies()
            if not response or 'data' not in response:
                raise ValueError("Invalid response format from CoinMarketCap API")

            # Convert to simple symbol -> name mapping
            cryptos = {}
            for crypto in response['data']:
                cryptos[crypto['symbol']] = crypto['name']

            return cryptos
        except Exception as e:
            self.logger.error(f"Error fetching supported cryptocurrencies: {e}")
            raise
