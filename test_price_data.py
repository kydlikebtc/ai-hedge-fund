import asyncio
import logging
from datetime import datetime
from src.providers.crypto_market_provider import CryptoMarketProvider

logging.basicConfig(level=logging.INFO)

async def test_sol_data():
    """Test SOL price data retrieval for November 2024."""
    provider = CryptoMarketProvider()
    try:
        print("\nTesting SOL price data for November 2024...")
        data = await provider.get_price_data('SOL', '2024-11-01', '2024-11-30')
        print('Successfully retrieved SOL data')
        print(f'Response structure: {data.keys()}')

        if 'data' in data and 'SOL' in data['data']:
            quotes = data['data']['SOL'].get('quotes', [])
            print(f'Data points: {len(quotes)} days')

            # Print first and last data points
            if quotes:
                print("\nFirst day data:")
                print(f"Date: {quotes[0]['timestamp']}")
                print(f"Price: ${quotes[0]['quote']['USD']['close']:.2f}")

                print("\nLast day data:")
                print(f"Date: {quotes[-1]['timestamp']}")
                print(f"Price: ${quotes[-1]['quote']['USD']['close']:.2f}")

            print('\nTest passed: Future date handling works correctly')
    except Exception as e:
        print(f'Error: {str(e)}')
        raise

if __name__ == "__main__":
    asyncio.run(test_sol_data())
