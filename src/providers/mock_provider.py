"""
Mock provider for cryptocurrency market data testing.
"""
from datetime import datetime, timedelta
import random
from typing import Dict, Any, List

class MockCryptoProvider:
    """Mock provider for cryptocurrency data."""

    def __init__(self):
        self.supported_cryptos = {
            'SOL': 'Solana',
            'ETH': 'Ethereum',
            'BTC': 'Bitcoin',
            'DOGE': 'Dogecoin',
            'XRP': 'Ripple'
        }

        # Base prices for supported cryptocurrencies
        self.base_prices = {
            'SOL': 100.0,
            'ETH': 2000.0,
            'BTC': 40000.0,
            'DOGE': 0.1,
            'XRP': 0.5
        }

    def get_market_data(self, ticker: str) -> Dict[str, Any]:
        """Get current market data for a cryptocurrency."""
        if ticker not in self.supported_cryptos:
            raise ValueError(f"Unsupported cryptocurrency: {ticker}")

        base_price = self.base_prices[ticker]
        current_price = base_price * (1 + random.uniform(-0.1, 0.1))

        return {
            'data': {
                ticker: {
                    'symbol': ticker,
                    'name': self.supported_cryptos[ticker],
                    'quote': {
                        'USD': {
                            'price': current_price,
                            'volume_24h': base_price * 1000000 * random.uniform(0.5, 1.5),
                            'percent_change_24h': random.uniform(-5, 5),
                            'market_cap': current_price * 1000000 * random.uniform(0.8, 1.2)
                        }
                    }
                }
            }
        }

    def get_price_data(self, ticker: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Get historical price data for a cryptocurrency."""
        if ticker not in self.supported_cryptos:
            raise ValueError(f"Unsupported cryptocurrency: {ticker}")

        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")

        base_price = self.base_prices[ticker]
        current_price = base_price
        prices = []

        current_date = start
        while current_date <= end:
            # Simulate price movement
            price_change = random.uniform(-0.05, 0.05)
            current_price *= (1 + price_change)

            prices.append({
                'timestamp': current_date.strftime("%Y-%m-%d"),
                'open': current_price * (1 + random.uniform(-0.02, 0.02)),
                'high': current_price * (1 + random.uniform(0, 0.05)),
                'low': current_price * (1 - random.uniform(0, 0.05)),
                'close': current_price,
                'volume': base_price * 1000000 * random.uniform(0.5, 1.5)
            })

            current_date += timedelta(days=1)

        return prices

    def get_supported_cryptocurrencies(self) -> Dict[str, str]:
        """Get list of supported cryptocurrencies."""
        return self.supported_cryptos
