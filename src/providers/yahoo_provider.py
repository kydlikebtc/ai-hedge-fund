"""
Yahoo Finance provider for historical cryptocurrency data.
"""
from datetime import datetime, timedelta
import logging
import yfinance as yf
from typing import Dict, Any

from .base import BaseProvider


class YahooFinanceProvider(BaseProvider):
    """Provider for historical cryptocurrency data using Yahoo Finance."""

    def __init__(self):
        """Initialize the Yahoo Finance provider."""
        self.logger = logging.getLogger(__name__)
        super().__init__()

    def _initialize_provider(self) -> None:
        """Initialize the Yahoo Finance provider."""
        # Yahoo Finance doesn't require API keys or special initialization
        self.logger.info("Initialized Yahoo Finance provider")

    def get_historical_prices(self, symbol: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """
        Get historical price data for a cryptocurrency.

        Args:
            symbol: The cryptocurrency symbol (e.g., 'ETH')
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            dict: Historical price data in CoinMarketCap-compatible format
        """
        try:
            # Parse dates
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            # Add one day to end_date to make it inclusive
            adjusted_end = (end_dt + timedelta(days=1)).strftime('%Y-%m-%d')

            self.logger.info(f"Fetching {symbol} data from {start_date} to {adjusted_end}")

            # Create ticker with -USD suffix for crypto pairs
            ticker = yf.Ticker(f"{symbol}-USD")

            # Get historical data with adjusted end date
            df = ticker.history(start=start_date, end=adjusted_end)

            if df.empty:
                raise ValueError(f"No data returned for {symbol} in date range")

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
            self.logger.error(f"Error fetching historical prices from Yahoo Finance: {e}")
            raise
