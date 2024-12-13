from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List, Optional
import asyncio
from datetime import datetime, timedelta
import os

from src.tools import get_supported_cryptocurrencies, get_market_data, get_price_data
from src.agents import analyze_market
from src.providers.mock_provider import MockCryptoProvider

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://sol-data-app-0uaoqyk7.devinapps.com"],  # Allow frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/cryptocurrencies")
async def list_cryptocurrencies():
    """Get list of supported cryptocurrencies."""
    try:
        cryptocurrencies = await get_supported_cryptocurrencies()
        return {"data": cryptocurrencies}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/market-data/{symbol}")
async def get_crypto_market_data(symbol: str):
    """Get market data for a specific cryptocurrency."""
    try:
        market_data = await get_market_data(symbol)
        if not market_data:
            raise HTTPException(status_code=404, detail=f"No market data found for {symbol}")

        # Extract relevant market data
        quote = market_data['data'][symbol]['quote']['USD']
        return {
            "price": quote['price'],
            "change24h": quote['percent_change_24h'],
            "volume": quote['volume_24h'] / 1e9  # Convert to billions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analysis/{symbol}")
async def get_crypto_analysis(
    symbol: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """Get AI agent analysis for a specific cryptocurrency."""
    try:
        # Use current date range if not specified
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")

        # Get market and price data
        market_data = await get_market_data(symbol)
        price_data = await get_price_data(symbol, start_date, end_date)

        # Run analysis
        analysis_results = await analyze_market(
            symbol=symbol,
            market_data=market_data,
            price_data=price_data,
            show_reasoning=True
        )

        # Format results for frontend
        agents = [
            {"title": "市场数据代理", "content": analysis_results["market_data_agent"]},
            {"title": "情绪代理", "content": analysis_results["sentiment_agent"]},
            {"title": "技术代理", "content": analysis_results["technical_agent"]},
            {"title": "风险代理", "content": analysis_results["risk_management_agent"]},
            {"title": "投资组合代理", "content": analysis_results["portfolio_agent"]}
        ]

        return {"agents": agents}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
