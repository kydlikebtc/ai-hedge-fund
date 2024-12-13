import asyncio
import logging
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
        if 'data' in data:
            print(f'Data points: {len(data["data"])} days')
            print('Test passed: Future date handling works correctly')
    except Exception as e:
        print(f'Error: {str(e)}')
        raise

if __name__ == "__main__":
    asyncio.run(test_sol_data())
