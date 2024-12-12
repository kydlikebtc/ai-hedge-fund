"""
Integration test for Claude 3.5 models with BTC data.
"""

import os
from datetime import datetime, timedelta
from src.config import get_model_provider
from src.tools import CMCClient, get_market_data, get_financial_metrics

def main():
    """Run integration test with Claude 3.5 and BTC data."""
    try:
        # Set up API keys from environment variables
        anthropic_api_key = os.environ.get('ANTHROPIC_API_KEY')
        cmc_api_key = os.environ.get('COINMARKETCAP_API_KEY')

        if not anthropic_api_key or not cmc_api_key:
            raise ValueError("Required API keys not found in environment variables")

        os.environ['COINMARKETCAP_API_KEY'] = cmc_api_key

        # Get BTC market data
        market_data = get_market_data('BTC')
        financial_data = get_financial_metrics('BTC')

        # Prepare state
        state = {
            'symbol': 'BTC',
            'market_data': market_data['data']['BTC']['quote']['USD'],
            'financial_data': financial_data['data']['BTC']
        }

        # Test with Claude 3.5 Sonnet
        provider = get_model_provider(
            provider_name="anthropic",
            model="claude-3-5-sonnet-20241022"
        )

        # Generate analysis
        system_prompt = """
        You are a cryptocurrency analyst specializing in Bitcoin market analysis.
        Analyze the provided market data and provide insights on:
        1. Current price trends and momentum
        2. Market sentiment based on volume and market cap
        3. Key risk factors and opportunities
        4. Short-term price outlook (24-48 hours)

        Format your analysis in a clear, structured way.
        """

        response = provider.generate_response(
            system_prompt=system_prompt,
            user_prompt=f"Here is the current market data for Bitcoin (BTC): {state}"
        )

        print("\nClaude 3.5 Sonnet Analysis:")
        print("-" * 50)
        print(response)
        print("-" * 50)

    except Exception as e:
        print(f"Error during testing: {str(e)}")

if __name__ == "__main__":
    main()
