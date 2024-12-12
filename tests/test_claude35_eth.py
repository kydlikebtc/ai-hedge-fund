"""
Integration test for Claude 3.5 models with ETH data.
Generates tabular output matching README example format.
"""

import os
import pandas as pd
from datetime import datetime
from src.config import get_model_provider
from src.tools import get_market_data, get_financial_metrics

def format_tabular_output(analysis_results, initial_investment=100000.00):
    print("Starting backtest...")
    print("Date         Ticker Action Quantity    Price         Cash    Stock  Total Value")
    print("----------------------------------------------------------------------")

    current_cash = initial_investment
    current_stock = 0.0

    for date in pd.date_range(start='2023-12-01', end='2023-12-11'):
        day_data = analysis_results[date.strftime('%Y-%m-%d')]
        action = day_data['action']
        price = day_data['price']
        quantity = day_data.get('quantity', 0.0)

        if action == 'buy':
            quantity = min((current_cash * 0.99) / price, quantity) if quantity > 0 else 0.0
            current_cash -= quantity * price
            current_stock = quantity
        elif action == 'sell':
            current_cash += current_stock * price
            current_stock = 0.0

        total_value = current_cash + (current_stock * price)
        print(f"{date.strftime('%Y-%m-%d')}   ETH    {action:4} {quantity:9.1f} {price:9.2f} {current_cash:10.2f} {current_stock:8.1f} {total_value:11.2f}")

def analyze_market_conditions(provider, state):
    """Generate trading decision using Claude 3.5 model."""
    system_prompt = """You are a cryptocurrency trading expert. Based on the provided market data, generate a trading decision.
IMPORTANT: Respond ONLY with a valid JSON object in this exact format, nothing else:
{
    "action": "buy/sell/hold",
    "price_change": 0.00,
    "quantity": 0.00
}
Where:
- action must be exactly "buy", "sell", or "hold"
- price_change is the expected price change as a decimal (e.g., 0.05 for 5% increase)
- quantity is the amount to trade (0 for hold)"""

    user_prompt = f"""Current ETH market data:
- Price: ${state['current_price']:,.2f}
- Market Cap: ${state['market_cap']:,.2f}
- 24h Volume: ${state['volume_24h']:,.2f}
- 24h Change: {state['percent_change_24h']}%

Analyze this data and respond ONLY with a JSON object containing your trading decision for {state['date']}.
"""

    response = provider.generate_response(
        system_prompt=system_prompt,
        user_prompt=user_prompt
    )

    import json
    try:
        # Clean the response to extract only the JSON part
        response_text = response.strip()
        if '```' in response_text:
            # Extract JSON from code blocks if present
            json_text = response_text.split('```')[1]
            if json_text.startswith('json'):
                json_text = json_text[4:]
        else:
            json_text = response_text

        decision = json.loads(json_text.strip())

        # Validate decision format
        if 'action' not in decision or decision['action'] not in ['buy', 'sell', 'hold']:
            raise ValueError("Invalid action in response")

        return {
            'action': decision['action'],
            'price_change': float(decision.get('price_change', 0.0)),
            'quantity': float(decision.get('quantity', 0.0))
        }
    except Exception as e:
        print(f"Error parsing model response: {str(e)}")
        print(f"Raw response: {response}")
        return {'action': 'hold', 'price_change': 0.0, 'quantity': 0.0}

def generate_daily_analysis(provider, market_data, financial_data, start_date, end_date):
    """Generate daily trading decisions and price predictions."""
    results = {}
    current_price = float(market_data['data']['ETH']['quote']['USD']['price'])

    for date in pd.date_range(start=start_date, end=end_date):
        state = {
            'date': date.strftime('%Y-%m-%d'),
            'current_price': current_price,
            'market_cap': float(market_data['data']['ETH']['quote']['USD']['market_cap']),
            'volume_24h': float(market_data['data']['ETH']['quote']['USD']['volume_24h']),
            'percent_change_24h': float(market_data['data']['ETH']['quote']['USD']['percent_change_24h'])
        }

        analysis = analyze_market_conditions(provider, state)
        predicted_price = current_price * (1 + analysis['price_change'])

        results[date.strftime('%Y-%m-%d')] = {
            'action': analysis['action'],
            'price': predicted_price,
            'quantity': analysis['quantity'] if analysis['action'] in ['buy', 'sell'] else 0.0
        }

        current_price = predicted_price

    return results

def main():
    try:
        provider = get_model_provider(
            provider_name="anthropic",
            model="claude-3-5-sonnet-20241022"
        )

        market_data = get_market_data('ETH')
        financial_data = get_financial_metrics('ETH')

        analysis_results = generate_daily_analysis(
            provider,
            market_data,
            financial_data,
            start_date='2023-12-01',
            end_date='2023-12-11'
        )

        format_tabular_output(analysis_results)

    except Exception as e:
        print(f"Error during testing: {str(e)}")
        raise

if __name__ == "__main__":
    main()
