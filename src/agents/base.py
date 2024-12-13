"""
Base agent class for cryptocurrency market analysis.
"""

from typing import Dict, Any, Optional

class BaseAgent:
    """Base class for all cryptocurrency analysis agents."""

    async def analyze(self, price_data, market_data, show_reasoning=False):
        """
        Analyze cryptocurrency market data and return insights.

        Args:
            price_data: Historical price data
            market_data: Current market data from CoinMarketCap
            show_reasoning: Whether to show detailed reasoning

        Returns:
            str: Analysis results
        """
        raise NotImplementedError("Subclasses must implement analyze method")
