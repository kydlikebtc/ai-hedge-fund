# AI Hedge Fund

An AI-powered hedge fund that uses multiple agents to make trading decisions. The system employs several agents working together:

1. Market Data Analyst - Gathers and preprocesses market data
2. Sentiment Agent - Analyzes market sentiment and generates trading signals
3. Fundamentals Agent - Analyzes fundamental data and generates trading signals
4. Quant Analyst - Analyzes technical indicators and generates trading signals
5. Risk Manager - Evaluates portfolio risk and sets position limits
6. Portfolio Manager - Makes final trading decisions and generates orders

<img width="1025" alt="Screenshot 2024-12-11 at 12 20 37 AM" src="https://github.com/user-attachments/assets/a03aed40-46cc-45a2-92c5-2a34acb27fd2">

Note: the system simulates trading decisions, it does not actually trade.

## Disclaimer

This project is for **educational and research purposes only**.

- Not intended for real trading or investment.
- No warranties or guarantees provided
- Past performance does not indicate future results
- Creator assumes no liability for financial losses
- Consult a financial advisor for investment decisions

By using this software, you agree to use it solely for learning purposes.

## Table of Contents
- [Features](#features)
- [Setup](#setup)
- [Usage](#usage)
  - [Running the Hedge Fund](#running-the-hedge-fund)
  - [Running the Hedge Fund (with Reasoning)](#running-the-hedge-fund-with-reasoning)
  - [Running the Backtester](#running-the-backtester)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## Features

- Multi-agent architecture for trading decisions
- Technical analysis using MACD, RSI, Bollinger Bands, and OBV
- Fundamental analysis using financial metrics
- Sentiment analysis using web search
- Risk management with position sizing recommendations
- Portfolio management with automated trading decisions
- Backtesting capabilities with performance analytics

## Setup

Clone the repository:
```bash
git clone https://github.com/virattt/ai-hedge-fund.git
cd ai-hedge-fund
```

1. Install Poetry (if not already installed):
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

2. Install dependencies:
```bash
poetry install
```

3. Set up your environment variables:
```bash
# Create .env file for your API keys
cp .env.example .env

export OPENAI_API_KEY='your-api-key-here' # Get a key from https://platform.openai.com/
export FINANCIAL_DATASETS_API_KEY='your-api-key-here' # Get a key from https://financialdatasets.ai/
```

## Usage

### Running the Hedge Fund

```bash
poetry run python src/agents.py --ticker AAPL
```
You can optionally specify the start and end dates to make decisions for a specific time period.

```bash
poetry run python src/agents.py --ticker AAPL --start-date 2024-01-01 --end-date 2024-03-01
```

### Running the Hedge Fund (with Reasoning)
This will print the reasoning of each agent to the console.

```bash
poetry run python src/agents.py --ticker AAPL --show-reasoning
```

### Running the Backtester

```bash
poetry run python src/backtester.py --ticker AAPL
```

**Example Output:**
```
Starting backtest...
Date         Ticker Action Quantity    Price         Cash    Stock  Total Value
----------------------------------------------------------------------
2024-01-01   AAPL   buy       519.0   192.53        76.93    519.0    100000.00
2024-01-02   AAPL   hold          0   185.64        76.93    519.0     96424.09
2024-01-03   AAPL   hold          0   184.25        76.93    519.0     95702.68
2024-01-04   AAPL   hold          0   181.91        76.93    519.0     94488.22
2024-01-05   AAPL   hold          0   181.18        76.93    519.0     94109.35
2024-01-08   AAPL   sell        519   185.56     96382.57      0.0     96382.57
2024-01-09   AAPL   buy       520.0   185.14       109.77    520.0     96382.57
```

You can optionally specify the start and end dates to backtest over a specific time period.

```bash
poetry run python src/backtester.py --ticker AAPL --start-date 2024-01-01 --end-date 2024-03-01
```

## Project Structure
```
ai-hedge-fund/
├── src/
│   ├── agents.py # Main agent definitions and workflow
│   ├── backtester.py # Backtesting functionality
│   ├── tools.py # Agent tools
├── pyproject.toml # Poetry configuration
├── .env.example # Environment variables
└── README.md # Documentation
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
