# AI Hedge Fund 🤖📈

[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![Poetry](https://img.shields.io/badge/poetry-package%20manager-blue)](https://python-poetry.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An AI-powered hedge fund that uses multiple agents to make trading decisions. The system employs several specialized agents working together to analyze markets and execute trades.

<img width="1025" alt="AI Hedge Fund Architecture" src="https://github.com/user-attachments/assets/a03aed40-46cc-45a2-92c5-2a34acb27fd2">

> **Note**: This system simulates trading decisions, it does not actually execute trades.

## 📋 Table of Contents
- [Disclaimer](#-disclaimer)
- [Features](#-features)
- [Requirements](#-requirements)
- [Installation](#-installation)
  - [Setting up Poetry](#setting-up-poetry)
  - [Installing Dependencies](#installing-dependencies)
  - [Configuring API Keys](#configuring-api-keys)
  - [Verification Steps](#verification-steps)
- [Usage](#-usage)
  - [Running the Hedge Fund](#running-the-hedge-fund)
  - [Running with Reasoning](#running-with-reasoning)
  - [Running the Backtester](#running-the-backtester)
- [Architecture](#-architecture)
  - [Agent System](#agent-system)
  - [Data Providers](#data-providers)
- [Project Structure](#-project-structure)
- [Development](#-development)
  - [Testing](#testing)
  - [Contributing](#contributing)
- [License](#-license)

## ⚠️ Disclaimer

This project is for **educational and research purposes only**.

- Not intended for real trading or investment
- No warranties or guarantees provided
- Past performance does not indicate future results
- Creator assumes no liability for financial losses
- Consult a financial advisor for investment decisions

By using this software, you agree to use it solely for learning purposes.

## ✨ Features

- Multi-agent architecture for sophisticated trading decisions:
  - Market Data Agent: Gathers and preprocesses market data
  - Sentiment Agent: Analyzes market sentiment
  - Fundamentals Agent: Analyzes company financials
  - Quant Agent: Processes technical indicators
  - Risk Manager: Evaluates portfolio risk
  - Portfolio Manager: Makes final trading decisions
- Technical analysis using multiple indicators:
  - MACD (Moving Average Convergence Divergence)
  - RSI (Relative Strength Index)
  - Bollinger Bands
  - OBV (On-Balance Volume)
- Fundamental analysis using financial metrics
- Sentiment analysis using web search
- Risk management with position sizing
- Portfolio management with automated decisions
- Comprehensive backtesting capabilities

## 🔧 Requirements

- Python 3.8 or higher
- Poetry package manager
- API Keys:
  - OpenAI API key
  - Financial Datasets API key

## 📥 Installation

### Setting up Poetry

```bash
# Install Poetry if not already installed
curl -sSL https://install.python-poetry.org | python3 -
```

### Installing Dependencies

```bash
# Clone the repository
git clone https://github.com/virattt/ai-hedge-fund.git
cd ai-hedge-fund

# Install project dependencies
poetry install
```

### Configuring API Keys

1. Create your environment file:
```bash
cp .env.example .env
```

2. Set up your API keys:
```bash
# Get your API key from https://platform.openai.com/
export OPENAI_API_KEY='your-api-key-here'

# Get your API key from https://financialdatasets.ai/
export FINANCIAL_DATASETS_API_KEY='your-api-key-here'
```

### Verification Steps

1. Verify Poetry installation:
```bash
poetry --version
```

2. Verify environment setup:
```bash
poetry run python -c "import os; print('OpenAI API Key:', bool(os.getenv('OPENAI_API_KEY')))"
```

## 🚀 Usage

### Running the Hedge Fund

Basic usage:
```bash
poetry run python src/agents.py --ticker AAPL
```

With date range:
```bash
poetry run python src/agents.py --ticker AAPL --start-date 2024-01-01 --end-date 2024-03-01
```

### Running with Reasoning

View detailed agent decision-making process:
```bash
poetry run python src/agents.py --ticker AAPL --show-reasoning
```

### Running the Backtester

Basic backtesting:
```bash
poetry run python src/backtester.py --ticker AAPL
```

Example output:
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

## 🏗️ Architecture

### Agent System

The system uses a multi-agent architecture where each agent specializes in different aspects of trading:

1. **Market Data Agent**: Gathers and preprocesses market data
2. **Sentiment Agent**: Analyzes market sentiment and news
3. **Fundamentals Agent**: Analyzes company financial metrics
4. **Quant Agent**: Processes technical indicators
5. **Risk Manager**: Evaluates portfolio risk
6. **Portfolio Manager**: Makes final trading decisions

### Data Providers

The system supports multiple data sources:
- Stock data from Financial Datasets API
- Cryptocurrency data from CoinMarketCap API
- News and sentiment data from various sources

## 📁 Project Structure

```
ai-hedge-fund/
├── src/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base.py          # Base agent classes
│   └── specialized.py   # Specialized agent implementations
│   ├── providers/
│   │   ├── __init__.py
│   │   ├── base.py          # Base provider interface
│   │   ├── openai_provider.py
│   │   └── anthropic_provider.py
│   ├── config/
│   │   ├── __init__.py
│   │   └── model_config.py  # Model configurations
│   ├── agents.py            # Main agent workflow
│   ├── backtester.py        # Backtesting system
│   └── tools.py             # Utility functions
├── tests/
│   ├── test_technical_analysis.py
│   ├── test_providers.py
│   └── test_integration.py
├── config/
│   └── models.yaml          # Model configurations
├── pyproject.toml           # Project dependencies
├── poetry.lock             # Locked dependencies
├── .env.example            # Environment template
└── README.md               # Documentation
```

## 🛠️ Development

### Testing

Run the test suite:
```bash
poetry run pytest
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

Please ensure your PR:
- Includes tests for new features
- Updates documentation as needed
- Follows the existing code style
- Includes a clear description of changes

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
