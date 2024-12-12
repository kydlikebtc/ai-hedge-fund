"""
Test historical ETH price data retrieval from CoinMarketCap API with fallback provider.
"""
import os
from datetime import datetime
import pandas as pd
from src.tools import get_prices, prices_to_df

def test_historical_eth_prices():
    """Test fetching historical ETH price data."""
    print("Testing Historical ETH Price Data Retrieval")
    print("==========================================")

    # Use previous year's data since we can't get future prices
    start_date = "2023-12-01"
    end_date = "2023-12-11"
    prices = get_prices("ETH", start_date, end_date)
    df = prices_to_df(prices)

    # Validate data structure and content
    assert isinstance(df, pd.DataFrame), "Result should be a pandas DataFrame"
    assert not df.empty, "Price data should not be empty"
    assert len(df) > 0, "Should have price entries"

    # Validate required columns
    required_columns = ['open', 'high', 'low', 'close', 'volume']
    for col in required_columns:
        assert col in df.columns.str.lower(), f"Missing required column: {col}"

    # Validate date range
    assert df.index.min().strftime('%Y-%m-%d') == start_date, f"Start date should be {start_date}"
    assert df.index.max().strftime('%Y-%m-%d') == end_date, f"End date should be {end_date}"

    # Validate data types
    assert pd.api.types.is_numeric_dtype(df['close']), "Close prices should be numeric"
    assert pd.api.types.is_numeric_dtype(df['volume']), "Volume should be numeric"

    # Print results for inspection
    print("\nValidation passed successfully!")
    print("\nProcessed DataFrame:")
    print("------------------")
    print(df)

if __name__ == "__main__":
    test_historical_eth_prices()
