"""
Mock provider for cryptocurrency market data testing.
"""
from datetime import datetime, timedelta
import random
from typing import Dict, Any, List

class MockCryptoProvider:
    """Mock provider for cryptocurrency data."""

    def __init__(self):
        """Initialize mock provider with mainstream cryptocurrencies."""
        self.supported_cryptos = {
            'BTC': 'Bitcoin',
            'ETH': 'Ethereum',
            'SOL': 'Solana',
            'BNB': 'Binance Coin',
            'XRP': 'Ripple',
            'ADA': 'Cardano',
            'DOGE': 'Dogecoin',
            'AVAX': 'Avalanche',
            'DOT': 'Polkadot',
            'MATIC': 'Polygon'
        }

        # Base prices for supported cryptocurrencies (approximate current prices)
        self.base_prices = {
            'BTC': 43000.0,
            'ETH': 2250.0,
            'SOL': 70.0,
            'BNB': 230.0,
            'XRP': 0.6,
            'ADA': 0.45,
            'DOGE': 0.095,
            'AVAX': 40.0,
            'DOT': 7.5,
            'MATIC': 0.8
        }

        # Market sentiment factors for price trend simulation
        self.market_trends = {
            symbol: random.uniform(-0.2, 0.2) for symbol in self.supported_cryptos
        }

    async def get_market_data(self, symbol: str) -> Dict[str, Any]:
        """Get current market data for a cryptocurrency."""
        if symbol not in self.supported_cryptos:
            raise ValueError(f"Unsupported cryptocurrency: {symbol}")

        base_price = self.base_prices[symbol]
        current_price = base_price * (1 + random.uniform(-0.1, 0.1))
        volume_24h = base_price * 1000000 * random.uniform(0.5, 1.5)
        percent_change_24h = random.uniform(-5, 5)
        percent_change_7d = random.uniform(-10, 10)
        volume_change_24h = random.uniform(-20, 20)

        return {
            'data': {
                symbol: {
                    'symbol': symbol,
                    'name': self.supported_cryptos[symbol],
                    'quote': {
                        'USD': {
                            'price': current_price,
                            'volume_24h': volume_24h,
                            'volume_change_24h': volume_change_24h,
                            'percent_change_24h': percent_change_24h,
                            'percent_change_7d': percent_change_7d,
                            'market_cap': current_price * 1000000 * random.uniform(0.8, 1.2)
                        }
                    }
                }
            }
        }

    async def get_price_data(self, symbol: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get historical price data for a cryptocurrency."""
        if symbol not in self.supported_cryptos:
            raise ValueError(f"Unsupported cryptocurrency: {symbol}")

        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        current = datetime.now()

        base_price = self.base_prices[symbol]
        current_price = base_price
        quotes = []

        # Calculate trend factors
        trend = self.market_trends[symbol]
        volatility = random.uniform(0.02, 0.08)  # Different volatility for different coins

        current_date = start
        while current_date <= end:
            # Add trend-based price movement
            if current_date > current:
                # Future dates: Add more volatility and trend influence
                daily_trend = trend * random.uniform(0.8, 1.2)
                price_change = random.uniform(-volatility, volatility) + daily_trend
            else:
                # Historical dates: More stable price movement
                price_change = random.uniform(-volatility/2, volatility/2) + trend/2

            current_price *= (1 + price_change)

            # Ensure price doesn't go below a minimum threshold
            current_price = max(current_price, base_price * 0.1)

            # Generate daily OHLCV data
            daily_volatility = volatility * random.uniform(0.5, 1.5)
            open_price = current_price * (1 + random.uniform(-daily_volatility, daily_volatility))
            high_price = max(open_price, current_price) * (1 + random.uniform(0, daily_volatility))
            low_price = min(open_price, current_price) * (1 - random.uniform(0, daily_volatility))

            # Volume increases with price volatility
            volume_factor = 1 + abs(price_change) * 10
            base_volume = base_price * 1000000

            quotes.append({
                'timestamp': current_date.strftime("%Y-%m-%d"),
                'quote': {
                    'USD': {
                        'open': open_price,
                        'high': high_price,
                        'low': low_price,
                        'close': current_price,
                        'volume': base_volume * volume_factor * random.uniform(0.8, 1.2)
                    }
                }
            })

            current_date += timedelta(days=1)

        return {
            'data': {
                symbol: {
                    'quotes': quotes
                }
            }
        }

    async def get_supported_cryptocurrencies(self) -> Dict[str, str]:
        """Get list of supported cryptocurrencies."""
        return self.supported_cryptos
