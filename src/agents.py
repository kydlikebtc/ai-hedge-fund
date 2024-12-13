"""
AI-powered hedge fund trading system with multi-agent workflow.
"""

import argparse
import json
import operator
from datetime import datetime
from typing import Annotated, Any, Dict, Sequence, TypedDict

from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import END, StateGraph

from src.tools import (calculate_bollinger_bands, calculate_macd,
                      calculate_obv, calculate_rsi, get_financial_metrics,
                      get_market_data, get_price_data, get_prices, prices_to_df)
from src.agents.specialized import (MarketDataAgent, SentimentAgent, TechnicalAgent,
                                  RiskManagementAgent, PortfolioAgent)
from src.config import get_model_provider

def merge_dicts(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    return {**a, **b}


# Define agent state
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    data: Annotated[Dict[str, Any], merge_dicts]
    metadata: Annotated[Dict[str, Any], merge_dicts]


##### Market Data Agent #####
def market_data_agent(state: AgentState):
    """Analyzes current market data and trends."""
    show_reasoning = state["metadata"]["show_reasoning"]
    data = state["data"]
    ticker = data["ticker"]

    try:
        # Get current market data
        market_data = get_market_data(ticker)
        if not market_data or 'data' not in market_data:
            raise ValueError(f"Failed to fetch market data for {ticker}")

        crypto_data = list(market_data['data'].values())[0]
        quote = crypto_data['quote']['USD']

        # Analyze market data
        message_content = {
            "price": quote['price'],
            "change_24h": quote['percent_change_24h'],
            "volume": quote['volume_24h'],
            "market_cap": quote['market_cap'],
            "analysis": "Market shows " + (
                "bullish momentum" if quote['percent_change_24h'] > 0
                else "bearish pressure"
            )
        }

        # Create the market data message
        message = HumanMessage(
            content=str(message_content),
            name="market_data_agent",
        )

        # Print the reasoning if the flag is set
        if show_reasoning:
            show_agent_reasoning(message_content, "Market Data Agent")

        return {
            "messages": [message],
            "data": data,
        }

    except Exception as e:
        error_msg = f"Market data analysis failed: {str(e)}"
        return {
            "messages": [HumanMessage(content=error_msg, name="market_data_agent")],
            "data": data,
        }


##### Quantitative Agent #####
def quant_agent(state: AgentState):
    """Analyzes technical indicators and generates trading signals."""
    show_reasoning = state["metadata"]["show_reasoning"]

    data = state["data"]
    prices = data["prices"]
    prices_df = prices_to_df(prices)

    # Calculate indicators
    # 1. MACD (Moving Average Convergence Divergence)
    macd_line, signal_line = calculate_macd(prices_df)

    # 2. RSI (Relative Strength Index)
    rsi = calculate_rsi(prices_df)

    # 3. Bollinger Bands (Bollinger Bands)
    upper_band, lower_band = calculate_bollinger_bands(prices_df)

    # 4. OBV (On-Balance Volume)
    obv = calculate_obv(prices_df)

    # Generate individual signals
    signals = []

    # MACD signal
    if (
        macd_line.iloc[-2] < signal_line.iloc[-2]
        and macd_line.iloc[-1] > signal_line.iloc[-1]
    ):
        signals.append("bullish")
    elif (
        macd_line.iloc[-2] > signal_line.iloc[-2]
        and macd_line.iloc[-1] < signal_line.iloc[-1]
    ):
        signals.append("bearish")
    else:
        signals.append("neutral")

    # RSI signal
    if rsi.iloc[-1] < 30:
        signals.append("bullish")
    elif rsi.iloc[-1] > 70:
        signals.append("bearish")
    else:
        signals.append("neutral")

    # Bollinger Bands signal
    current_price = prices_df["close"].iloc[-1]
    if current_price < lower_band.iloc[-1]:
        signals.append("bullish")
    elif current_price > upper_band.iloc[-1]:
        signals.append("bearish")
    else:
        signals.append("neutral")

    # OBV signal
    obv_slope = obv.diff().iloc[-5:].mean()
    if obv_slope > 0:
        signals.append("bullish")
    elif obv_slope < 0:
        signals.append("bearish")
    else:
        signals.append("neutral")

    # Add reasoning collection
    reasoning = {
        "MACD": {
            "signal": signals[0],
            "details": f"MACD Line crossed {'above' if signals[0] == 'bullish' else 'below' if signals[0] == 'bearish' else 'neither above nor below'} Signal Line",
        },
        "RSI": {
            "signal": signals[1],
            "details": f"RSI is {rsi.iloc[-1]:.2f} ({'oversold' if signals[1] == 'bullish' else 'overbought' if signals[1] == 'bearish' else 'neutral'})",
        },
        "Bollinger": {
            "signal": signals[2],
            "details": f"Price is {'below lower band' if signals[2] == 'bullish' else 'above upper band' if signals[2] == 'bearish' else 'within bands'}",
        },
        "OBV": {
            "signal": signals[3],
            "details": f"OBV slope is {obv_slope:.2f} ({signals[3]})",
        },
    }

    # Determine overall signal
    bullish_signals = signals.count("bullish")
    bearish_signals = signals.count("bearish")

    if bullish_signals > bearish_signals:
        overall_signal = "bullish"
    elif bearish_signals > bullish_signals:
        overall_signal = "bearish"
    else:
        overall_signal = "neutral"

    # Calculate confidence level based on the proportion of indicators agreeing
    total_signals = len(signals)
    confidence = max(bullish_signals, bearish_signals) / total_signals

    # Generate the message content
    message_content = {
        "signal": overall_signal,
        "confidence": round(confidence, 2),
        "reasoning": {
            "MACD": reasoning["MACD"],
            "RSI": reasoning["RSI"],
            "Bollinger": reasoning["Bollinger"],
            "OBV": reasoning["OBV"],
        },
    }

    # Create the quant message
    message = HumanMessage(
        content=str(message_content),  # Convert dict to string for message content
        name="quant_agent",
    )

    # Print the reasoning if the flag is set
    if show_reasoning:
        show_agent_reasoning(message_content, "Quant Agent")

    return {
        "messages": [message],
        "data": data,
    }


##### Fundamental Agent #####
def fundamentals_agent(state: AgentState):
    """Analyzes fundamental data and generates trading signals."""
    show_reasoning = state["metadata"]["show_reasoning"]
    data = state["data"]
    metrics = data["financial_metrics"][0]  # Get the most recent metrics

    # Initialize signals list for different fundamental aspects
    signals = []
    reasoning = {}

    # 1. Profitability Analysis
    profitability_score = 0
    if metrics["market_dominance"] > 0.15:  # Strong market dominance above 15%
        profitability_score += 1
    if metrics["volume_24h"] > metrics["avg_volume_7d"]:  # Strong trading volume
        profitability_score += 1
    if metrics["active_addresses"] > metrics["avg_active_addresses_7d"]:  # Growing network usage
        profitability_score += 1

    signals.append(
        "bullish"
        if profitability_score >= 2
        else "bearish"
        if profitability_score == 0
        else "neutral"
    )
    reasoning["Profitability"] = {
        "signal": signals[0],
        "details": f"Market Dominance: {metrics['market_dominance']:.2%}, Trading Volume: {metrics['volume_24h']:,.0f}, Active Addresses: {metrics['active_addresses']:,}",
    }

    # 2. Growth Analysis
    growth_score = 0
    if metrics["revenue_growth"] > 0.10:  # 10% revenue growth
        growth_score += 1
    if metrics["earnings_growth"] > 0.10:  # 10% earnings growth
        growth_score += 1
    if metrics["book_value_growth"] > 0.10:  # 10% book value growth
        growth_score += 1

    signals.append(
        "bullish"
        if growth_score >= 2
        else "bearish"
        if growth_score == 0
        else "neutral"
    )
    reasoning["Growth"] = {
        "signal": signals[1],
        "details": f"Revenue Growth: {metrics['revenue_growth']:.2%}, Earnings Growth: {metrics['earnings_growth']:.2%}",
    }

    # 3. Financial Health
    health_score = 0
    # Get historical hash rate data
    historical_hash_rate = metrics.get("historical_hash_rate", [])
    previous_hash_rate = historical_hash_rate[-2] if len(historical_hash_rate) > 1 else metrics["network_hash_rate"]

    if metrics["liquidity_24h"] > 1000000:  # Strong liquidity (>$1M daily)
        health_score += 1
    if metrics["network_hash_rate"] > previous_hash_rate:  # Growing network strength
        health_score += 1
    if metrics["miner_revenue"] > metrics["avg_miner_revenue_7d"]:  # Healthy mining economics
        health_score += 1

    signals.append(
        "bullish"
        if health_score >= 2
        else "bearish"
        if health_score == 0
        else "neutral"
    )
    reasoning["Financial_Health"] = {
        "signal": signals[2],
        "details": f"Hash Rate Change: {(metrics['network_hash_rate'] / previous_hash_rate - 1):.2%}, Mining Difficulty: {metrics['mining_difficulty']:,}",
    }

    # 4. Network Analysis
    network_score = 0

    # Check network metrics
    if metrics["transaction_count_24h"] > metrics["avg_transaction_count_7d"]:
        network_score += 1
    if metrics["avg_transaction_value"] > metrics["avg_transaction_value_7d"]:
        network_score += 1
    if metrics["mining_difficulty"] > metrics["avg_mining_difficulty_7d"]:
        network_score += 1

    signals.append(
        "Strong Buy"
        if network_score >= 2
        else "Buy"
        if network_score == 1
        else "Neutral"
    )
    reasoning["Network_Health"] = {
        "signal": signals[3],
        "details": f"Transactions: {metrics['transaction_count_24h']:,}, Avg Value: ${metrics['avg_transaction_value']:,.2f}, Difficulty: {metrics['mining_difficulty']:,}",
    }

    # Determine overall signal
    bullish_signals = signals.count("bullish")
    bearish_signals = signals.count("bearish")

    if bullish_signals > bearish_signals:
        overall_signal = "bullish"
    elif bearish_signals > bullish_signals:
        overall_signal = "bearish"
    else:
        overall_signal = "neutral"

    # Calculate confidence level
    total_signals = len(signals)
    confidence = max(bullish_signals, bearish_signals) / total_signals

    message_content = {
        "signal": overall_signal,
        "confidence": round(confidence, 2),
        "reasoning": reasoning,
    }

    # Create the fundamental analysis message
    message = HumanMessage(
        content=str(message_content),
        name="fundamentals_agent",
    )

    # Print the reasoning if the flag is set
    if show_reasoning:
        show_agent_reasoning(message_content, "Fundamental Analysis Agent")

    return {
        "messages": [message],
        "data": data,
    }


##### Sentiment Agent #####
def sentiment_agent(state: AgentState):
    """Analyzes market sentiment and generates trading signals."""
    data = state["data"]
    insider_trades = data["insider_trades"]
    show_reasoning = state["metadata"]["show_reasoning"]

    # Create sentiment agent with default provider
    agent = SentimentAgent()
    message_content = agent.analyze_sentiment(insider_trades)

    # Create the market sentiment message
    message = HumanMessage(
        content=str(message_content),
        name="sentiment_agent",
    )

    # Print the reasoning if the flag is set
    if show_reasoning:
        show_agent_reasoning(message_content, "Sentiment Analysis Agent")

    return {
        "messages": [message],
        "data": data,
    }

##### Risk Management Agent #####
def risk_management_agent(state: AgentState):
    """Evaluates portfolio risk and sets position limits"""
    show_reasoning = state["metadata"]["show_reasoning"]
    portfolio = state["data"]["portfolio"]

    # Get agent messages
    quant_message = next(msg for msg in state["messages"] if msg.name == "quant_agent")
    fundamentals_message = next(
        msg for msg in state["messages"] if msg.name == "fundamentals_agent"
    )
    sentiment_message = next(
        msg for msg in state["messages"] if msg.name == "sentiment_agent"
    )

    # Create risk management agent with default provider
    agent = RiskManagementAgent()

    # Parse message contents
    quant_signal = eval(quant_message.content)
    fundamental_signal = eval(fundamentals_message.content)
    sentiment_signal = eval(sentiment_message.content)

    # Generate risk assessment
    result = agent.evaluate_risk(
        quant_signal,
        fundamental_signal,
        sentiment_signal,
        portfolio
    )

    # Create message
    message = HumanMessage(
        content=str(result),
        name="risk_management_agent",
    )

    # Print the decision if the flag is set
    if show_reasoning:
        show_agent_reasoning(result, "Risk Management Agent")

    return {"messages": state["messages"] + [message]}

##### Portfolio Management Agent #####
def portfolio_management_agent(state: AgentState):
    """Provides portfolio management recommendations."""
    show_reasoning = state["metadata"]["show_reasoning"]
    data = state["data"]
    ticker = data["ticker"]

    try:
        # Get current market data
        market_data = get_market_data(ticker)
        if not market_data or 'data' not in market_data:
            raise ValueError(f"Failed to fetch market data for {ticker}")

        crypto_data = list(market_data['data'].values())[0]
        quote = crypto_data['quote']['USD']
        trend = quote['percent_change_24h']

        # Generate portfolio advice
        if trend > 5:
            action = "TAKE PROFIT"
        elif trend < -5:
            action = "BUY DIP"
        else:
            action = "HOLD"

        message_content = {
            "action": action,
            "trend": trend,
            "direction": "Upward" if trend > 0 else "Downward",
            "reasoning": f"Based on {trend:.2f}% 24h change"
        }

        # Create the portfolio message
        message = HumanMessage(
            content=str(message_content),
            name="portfolio_agent",
        )

        # Print the reasoning if the flag is set
        if show_reasoning:
            show_agent_reasoning(message_content, "Portfolio Agent")

        return {
            "messages": [message],
            "data": data,
        }

    except Exception as e:
        error_msg = f"Portfolio analysis failed: {str(e)}"
        return {
            "messages": [HumanMessage(content=error_msg, name="portfolio_agent")],
            "data": data,
        }

def show_agent_reasoning(output, agent_name):
    print(f"\n{'=' * 10} {agent_name.center(28)} {'=' * 10}")
    if isinstance(output, (dict, list)):
        # If output is already a dictionary or list, just pretty print it
        print(json.dumps(output, indent=2))
    else:
        try:
            # Parse the string as JSON and pretty print it
            parsed_output = json.loads(output)
            print(json.dumps(parsed_output, indent=2))
        except json.JSONDecodeError:
            # Fallback to original string if not valid JSON
            print(output)
    print("=" * 48)


##### Run the Hedge Fund #####
def run_hedge_fund(
    ticker: str,
    start_date: str,
    end_date: str,
    portfolio: dict,
    show_reasoning: bool = False,
):
    final_state = app.invoke(
        {
            "messages": [
                HumanMessage(
                    content="Make a trading decision based on the provided data.",
                )
            ],
            "data": {
                "ticker": ticker,
                "portfolio": portfolio,
                "start_date": start_date,
                "end_date": end_date,
            },
            "metadata": {
                "show_reasoning": show_reasoning,
            },
        },
    )
    return final_state["messages"][-1].content


# Define the new workflow
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("market_data_agent", market_data_agent)
workflow.add_node("quant_agent", quant_agent)
workflow.add_node("fundamentals_agent", fundamentals_agent)
workflow.add_node("sentiment_agent", sentiment_agent)
workflow.add_node("risk_management_agent", risk_management_agent)
workflow.add_node("portfolio_management_agent", portfolio_management_agent)

# Define the workflow
workflow.set_entry_point("market_data_agent")
workflow.add_edge("market_data_agent", "quant_agent")
workflow.add_edge("market_data_agent", "fundamentals_agent")
workflow.add_edge("market_data_agent", "sentiment_agent")
workflow.add_edge("quant_agent", "risk_management_agent")
workflow.add_edge("fundamentals_agent", "risk_management_agent")
workflow.add_edge("sentiment_agent", "risk_management_agent")
workflow.add_edge("risk_management_agent", "portfolio_management_agent")
workflow.add_edge("portfolio_management_agent", END)

app = workflow.compile()

# Add this at the bottom of the file
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the hedge fund trading system")
    parser.add_argument("--ticker", type=str, required=True, help="Cryptocurrency symbol")
    parser.add_argument(
        "--start-date",
        type=str,
        help="Start date (YYYY-MM-DD). Defaults to 3 months before end date",
    )
    parser.add_argument(
        "--end-date", type=str, help="End date (YYYY-MM-DD). Defaults to today"
    )
    parser.add_argument(
        "--show-reasoning", action="store_true", help="Show reasoning from each agent"
    )

    args = parser.parse_args()

    # Validate dates if provided
    if args.start_date:
        try:
            datetime.strptime(args.start_date, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Start date must be in YYYY-MM-DD format")

    if args.end_date:
        try:
            datetime.strptime(args.end_date, "%Y-%m-%d")
        except ValueError:
            raise ValueError("End date must be in YYYY-MM-DD format")

    # Sample portfolio - you might want to make this configurable too
    portfolio = {
        "cash": 100000.0,  # $100,000 initial cash
        "crypto": 0,  # No initial crypto position
    }

    result = run_hedge_fund(
        ticker=args.ticker,
        start_date=args.start_date,
        end_date=args.end_date,
        portfolio=portfolio,
        show_reasoning=args.show_reasoning,
    )
    print("\nFinal Result:")
    print(result)
