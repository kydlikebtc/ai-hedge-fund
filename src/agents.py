"""
Cryptocurrency market analysis agents and workflow.
"""

import os
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage

from src.tools import (
    get_market_data,
    get_price_data,
    prices_to_df
)
from src.agents.specialized import (
    MarketDataAgent,
    SentimentAgent,
    TechnicalAgent,
    RiskManagementAgent,
    PortfolioAgent
)

async def market_data_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """Analyzes current market data and trends."""
    data = state.get("data", {})
    metadata = state.get("metadata", {})
    show_reasoning = metadata.get("show_reasoning", False)

    try:
        # Get market data
        symbol = data.get("ticker")
        start_date = data.get("start_date")
        end_date = data.get("end_date")

        market_data = await get_market_data(symbol)
        price_data = await get_price_data(symbol, start_date, end_date)

        if show_reasoning:
            show_agent_reasoning({
                "market_data": market_data,
                "price_data": price_data
            }, "market_data_agent")

        message = HumanMessage(
            content="Market data analysis complete",
            name="market_data_agent"
        )

        return {
            "messages": [message],
            "data": {
                **data,
                "market_data": market_data,
                "price_data": price_data
            },
            "metadata": metadata
        }
    except Exception as e:
        message = HumanMessage(
            content=f"Error in market data analysis: {str(e)}",
            name="market_data_agent"
        )
        return {"messages": [message], "data": data, "metadata": metadata}

async def sentiment_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """Analyzes market sentiment."""
    data = state.get("data", {})
    metadata = state.get("metadata", {})
    show_reasoning = metadata.get("show_reasoning", False)

    try:
        agent = SentimentAgent()
        analysis = await agent.analyze(
            data.get("price_data"),
            data.get("market_data"),
            show_reasoning
        )

        message = HumanMessage(
            content=analysis,
            name="sentiment_agent"
        )

        return {
            "messages": state.get("messages", []) + [message],
            "data": data,
            "metadata": metadata
        }
    except Exception as e:
        message = HumanMessage(
            content=f"Error in sentiment analysis: {str(e)}",
            name="sentiment_agent"
        )
        return {
            "messages": state.get("messages", []) + [message],
            "data": data,
            "metadata": metadata
        }

async def technical_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """Analyzes technical indicators."""
    data = state.get("data", {})
    metadata = state.get("metadata", {})
    show_reasoning = metadata.get("show_reasoning", False)

    try:
        agent = TechnicalAgent()
        analysis = await agent.analyze(
            data.get("price_data"),
            data.get("market_data"),
            show_reasoning
        )

        message = HumanMessage(
            content=analysis,
            name="technical_agent"
        )

        return {
            "messages": state.get("messages", []) + [message],
            "data": data,
            "metadata": metadata
        }
    except Exception as e:
        message = HumanMessage(
            content=f"Error in technical analysis: {str(e)}",
            name="technical_agent"
        )
        return {
            "messages": state.get("messages", []) + [message],
            "data": data,
            "metadata": metadata
        }

async def risk_management_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """Analyzes market risks."""
    data = state.get("data", {})
    metadata = state.get("metadata", {})
    show_reasoning = metadata.get("show_reasoning", False)

    try:
        agent = RiskManagementAgent()
        analysis = await agent.analyze(
            data.get("price_data"),
            data.get("market_data"),
            show_reasoning
        )

        message = HumanMessage(
            content=analysis,
            name="risk_management_agent"
        )

        return {
            "messages": state.get("messages", []) + [message],
            "data": data,
            "metadata": metadata
        }
    except Exception as e:
        message = HumanMessage(
            content=f"Error in risk analysis: {str(e)}",
            name="risk_management_agent"
        )
        return {
            "messages": state.get("messages", []) + [message],
            "data": data,
            "metadata": metadata
        }

async def portfolio_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """Provides portfolio recommendations."""
    data = state.get("data", {})
    metadata = state.get("metadata", {})
    show_reasoning = metadata.get("show_reasoning", False)

    try:
        agent = PortfolioAgent()
        analysis = await agent.analyze(
            data.get("price_data"),
            data.get("market_data"),
            show_reasoning
        )

        message = HumanMessage(
            content=analysis,
            name="portfolio_agent"
        )

        return {
            "messages": state.get("messages", []) + [message],
            "data": data,
            "metadata": metadata
        }
    except Exception as e:
        message = HumanMessage(
            content=f"Error in portfolio analysis: {str(e)}",
            name="portfolio_agent"
        )
        return {
            "messages": state.get("messages", []) + [message],
            "data": data,
            "metadata": metadata
        }

def show_agent_reasoning(output: Any, agent_name: str) -> None:
    """Display agent reasoning if show_reasoning is True."""
    print(f"\n{'=' * 10} {agent_name.center(28)} {'=' * 10}")
    print(output)
    print('=' * 50)

async def analyze_market(
    symbol: str,
    market_data: Dict[str, Any],
    price_data: Dict[str, Any],
    show_reasoning: bool = False
) -> Dict[str, str]:
    """
    Run market analysis using all specialized agents.

    Args:
        symbol: Cryptocurrency symbol
        market_data: Current market data
        price_data: Historical price data
        show_reasoning: Whether to show detailed agent reasoning

    Returns:
        Dict containing analysis results from each agent
    """
    try:
        # Initialize agents
        market_agent = MarketDataAgent()
        sentiment_agent = SentimentAgent()
        technical_agent = TechnicalAgent()
        risk_agent = RiskManagementAgent()
        portfolio_agent = PortfolioAgent()

        # Run analysis in parallel
        results = await asyncio.gather(
            market_agent.analyze(price_data, market_data, show_reasoning),
            sentiment_agent.analyze(price_data, market_data, show_reasoning),
            technical_agent.analyze(price_data, market_data, show_reasoning),
            risk_agent.analyze(price_data, market_data, show_reasoning),
            portfolio_agent.analyze(price_data, market_data, show_reasoning)
        )

        # Map results to agent names
        return {
            "market_data_agent": results[0],
            "sentiment_agent": results[1],
            "technical_agent": results[2],
            "risk_management_agent": results[3],
            "portfolio_agent": results[4]
        }
    except Exception as e:
        return {
            "market_data_agent": f"Error in market analysis: {str(e)}",
            "sentiment_agent": "Analysis failed",
            "technical_agent": "Analysis failed",
            "risk_management_agent": "Analysis failed",
            "portfolio_agent": "Analysis failed"
        }

async def run_hedge_fund(
    ticker: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    show_reasoning: bool = False,
) -> Dict[str, Any]:
    """
    Run the cryptocurrency market analysis workflow.

    Args:
        ticker: Cryptocurrency symbol (e.g., 'BTC', 'ETH', 'SOL')
        start_date: Analysis start date (YYYY-MM-DD)
        end_date: Analysis end date (YYYY-MM-DD)
        show_reasoning: Whether to show detailed agent reasoning

    Returns:
        Dict containing analysis results and messages
    """
    # Set default dates if not provided
    if not end_date:
        end_date = datetime.now().strftime("%Y-%m-%d")
    if not start_date:
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
        start_date = (
            end_date_obj.replace(month=end_date_obj.month - 3)
            if end_date_obj.month > 3
            else end_date_obj.replace(
                year=end_date_obj.year - 1, month=end_date_obj.month + 9
            )
        ).strftime("%Y-%m-%d")

    # Initialize workflow
    workflow = StateGraph(Dict[str, Any])

    # Add nodes
    workflow.add_node("market_data", market_data_agent)
    workflow.add_node("sentiment", sentiment_agent)
    workflow.add_node("technical", technical_agent)
    workflow.add_node("risk", risk_management_agent)
    workflow.add_node("portfolio", portfolio_agent)

    # Define edges
    workflow.add_edge("market_data", "sentiment")
    workflow.add_edge("sentiment", "technical")
    workflow.add_edge("technical", "risk")
    workflow.add_edge("risk", "portfolio")
    workflow.add_edge("portfolio", END)

    # Set entry point
    workflow.set_entry_point("market_data")

    # Create app
    app = workflow.compile()

    # Run analysis
    final_state = await app.ainvoke({
        "data": {
            "ticker": ticker,
            "start_date": start_date,
            "end_date": end_date,
        },
        "metadata": {
            "show_reasoning": show_reasoning
        },
        "messages": []
    })

    return final_state

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Cryptocurrency Market Analysis")
    parser.add_argument("--ticker", type=str, required=True, help="Cryptocurrency symbol (e.g., BTC)")
    parser.add_argument("--start-date", type=str, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", type=str, help="End date (YYYY-MM-DD)")
    parser.add_argument("--show-reasoning", action="store_true", help="Show detailed agent reasoning")

    args = parser.parse_args()

    result = asyncio.run(run_hedge_fund(
        ticker=args.ticker,
        start_date=args.start_date,
        end_date=args.end_date,
        show_reasoning=args.show_reasoning
    ))

    # Print results
    print("\nAnalysis Results:")
    for message in result["messages"]:
        print(f"\n{message.name}:")
        print(message.content)
