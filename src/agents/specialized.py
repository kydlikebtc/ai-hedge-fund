"""
Specialized cryptocurrency trading agent implementations.
"""

from typing import Dict, Any
from datetime import datetime
from .base import BaseAgent
from ..tools import (
    calculate_bollinger_bands, calculate_macd,
    calculate_obv, calculate_rsi, get_market_data,
    get_price_data, prices_to_df
)

class MarketDataAgent(BaseAgent):
    """Analyzes current market data and trends for any cryptocurrency."""

    async def analyze(self, price_data, market_data, show_reasoning=False):
        try:
            if not market_data or 'data' not in market_data:
                return "Error: No market data available"

            crypto_data = list(market_data['data'].values())[0]
            quote = crypto_data['quote']['USD']

            analysis = (
                f"Current Price: ${quote['price']:.2f}\n"
                f"24h Change: {quote['percent_change_24h']:.2f}%\n"
                f"Volume: ${quote['volume_24h']/1e6:.1f}M\n"
                f"Market Cap: ${quote['market_cap']/1e9:.2f}B"
            )
            return analysis
        except Exception as e:
            return f"Error analyzing market data: {str(e)}"

class SentimentAgent(BaseAgent):
    """Analyzes market sentiment for any cryptocurrency."""

    async def analyze(self, price_data, market_data, show_reasoning=False):
        try:
            quote = list(market_data['data'].values())[0]['quote']['USD']
            sentiment = "bullish" if quote['percent_change_24h'] > 0 else "bearish"

            analysis = (
                f"Market Sentiment: {sentiment.upper()}\n"
                f"24h Trend: {quote['percent_change_24h']:.2f}%\n"
                f"7d Trend: {quote['percent_change_7d']:.2f}%"
            )
            return analysis
        except Exception as e:
            return f"Error analyzing sentiment: {str(e)}"

class TechnicalAgent(BaseAgent):
    """Analyzes technical indicators for any cryptocurrency."""

    async def analyze(self, price_data, market_data, show_reasoning=False):
        try:
            df = prices_to_df(price_data)
            if df.empty:
                return "Error: No price data available for technical analysis"

            # Calculate technical indicators
            rsi = calculate_rsi(df)
            macd_line, signal_line = calculate_macd(df)
            upper_band, lower_band = calculate_bollinger_bands(df)

            # Get latest values and ensure they're scalar
            latest_rsi = float(rsi.iloc[-1])
            latest_macd = float(macd_line.iloc[-1])
            latest_signal = float(signal_line.iloc[-1])
            latest_close = float(df['close'].iloc[-1])
            latest_upper = float(upper_band.iloc[-1])
            latest_lower = float(lower_band.iloc[-1])

            # Generate analysis based on technical indicators
            analysis = []

            # RSI Analysis
            if latest_rsi > 70:
                rsi_signal = "Overbought"
            elif latest_rsi < 30:
                rsi_signal = "Oversold"
            else:
                rsi_signal = "Neutral"

            # MACD Analysis
            macd_signal = "Bullish" if latest_macd > latest_signal else "Bearish"

            # Bollinger Bands Analysis
            if latest_close > latest_upper:
                bb_signal = "Overbought"
            elif latest_close < latest_lower:
                bb_signal = "Oversold"
            else:
                bb_signal = "Neutral"

            analysis = (
                f"Technical Analysis:\n"
                f"RSI (14): {latest_rsi:.2f} - {rsi_signal}\n"
                f"MACD Signal: {macd_signal} (MACD: {latest_macd:.2f}, Signal: {latest_signal:.2f})\n"
                f"Bollinger Bands: {bb_signal} (Price: {latest_close:.2f}, Upper: {latest_upper:.2f}, Lower: {latest_lower:.2f})"
            )
            return analysis
        except Exception as e:
            return f"Error analyzing technical indicators: {str(e)}"

class RiskManagementAgent(BaseAgent):
    """Analyzes market risks for any cryptocurrency."""

    async def analyze(self, price_data, market_data, show_reasoning=False):
        try:
            quote = list(market_data['data'].values())[0]['quote']['USD']
            volatility = abs(quote['percent_change_24h'])

            risk_level = "HIGH" if volatility > 10 else "MEDIUM" if volatility > 5 else "LOW"

            analysis = (
                f"Risk Level: {risk_level}\n"
                f"Volatility: {volatility:.2f}%\n"
                f"Volume Change: {quote['volume_change_24h']:.2f}%"
            )
            return analysis
        except Exception as e:
            return f"Error analyzing risks: {str(e)}"

class PortfolioAgent(BaseAgent):
    """Provides portfolio recommendations for any cryptocurrency."""

    async def analyze(self, price_data, market_data, show_reasoning=False):
        try:
            quote = list(market_data['data'].values())[0]['quote']['USD']
            trend = quote['percent_change_24h']

            if trend > 5:
                action = "TAKE PROFIT"
            elif trend < -5:
                action = "BUY DIP"
            else:
                action = "HOLD"

            analysis = (
                f"Recommended Action: {action}\n"
                f"Price Trend: {trend:.2f}%\n"
                f"Market Direction: {'Upward' if trend > 0 else 'Downward'}"
            )
            return analysis
        except Exception as e:
            return f"Error generating portfolio advice: {str(e)}"
