"""
AI-powered trading agents package.
"""

from typing import Dict, Any
import asyncio

from .base import BaseAgent
from .specialized import (
    MarketDataAgent,
    SentimentAgent,
    TechnicalAgent,
    RiskManagementAgent,
    PortfolioAgent
)

__all__ = ['BaseAgent', 'analyze_market']

async def analyze_market(
    symbol: str,
    market_data: Dict[str, Any],
    price_data: Dict[str, Any],
    show_reasoning: bool = False
) -> Dict[str, str]:
    """
    Analyze market data using all available agents.

    Args:
        symbol: Cryptocurrency symbol (e.g., 'BTC', 'ETH')
        market_data: Current market data
        price_data: Historical price data
        show_reasoning: Whether to show detailed reasoning

    Returns:
        Dict containing analysis results from each agent
    """
    # Initialize all agents
    agents = {
        "market_data_agent": MarketDataAgent(),
        "sentiment_agent": SentimentAgent(),
        "technical_agent": TechnicalAgent(),
        "risk_management_agent": RiskManagementAgent(),
        "portfolio_agent": PortfolioAgent()
    }

    # Run all agent analyses concurrently
    tasks = []
    for name, agent in agents.items():
        task = asyncio.create_task(
            agent.analyze(price_data, market_data, show_reasoning)
        )
        tasks.append((name, task))

    # Gather results
    results = {}
    for name, task in tasks:
        try:
            results[name] = await task
        except Exception as e:
            results[name] = f"Error in {name}: {str(e)}"

    return results
