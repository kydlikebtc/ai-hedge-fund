from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import pandas as pd

from src.agents import run_hedge_fund
from src.tools import get_price_data


class Backtester:
    def __init__(self, agent, ticker, start_date, end_date, initial_capital):
        self.agent = agent
        self.ticker = ticker
        self.start_date = start_date
        self.end_date = end_date
        self.initial_capital = initial_capital
        self.portfolio = {"cash": initial_capital, "crypto": 0}
        self.portfolio_values = []

    def parse_action(self, agent_output):
        try:
            import json

            decision = json.loads(agent_output)
            return decision["action"], decision["quantity"]
        except:
            print(f"Error parsing action: {agent_output}")
            return "hold", 0

    def execute_trade(self, action, quantity, current_price):
        if action == "buy" and quantity > 0:
            cost = quantity * current_price
            if cost <= self.portfolio["cash"]:
                self.portfolio["crypto"] += quantity
                self.portfolio["cash"] -= cost
                return quantity
            else:
                max_quantity = self.portfolio["cash"] // current_price
                if max_quantity > 0:
                    self.portfolio["crypto"] += max_quantity
                    self.portfolio["cash"] -= max_quantity * current_price
                    return max_quantity
                return 0
        elif action == "sell" and quantity > 0:
            quantity = min(quantity, self.portfolio["crypto"])
            if quantity > 0:
                self.portfolio["cash"] += quantity * current_price
                self.portfolio["crypto"] -= quantity
                return quantity
            return 0
        return 0

    def run_backtest(self):
        dates = pd.date_range(self.start_date, self.end_date, freq="D")

        print("\nStarting cryptocurrency backtest...")
        print(
            f"{'Date':<12} {'Ticker':<6} {'Action':<6} {'Quantity':>8} {'Price':>8} {'Cash':>12} {'Crypto':>8} {'Total Value':>12}"
        )
        print("-" * 70)

        for current_date in dates:
            lookback_start = (current_date - timedelta(days=30)).strftime("%Y-%m-%d")
            current_date_str = current_date.strftime("%Y-%m-%d")

            agent_output = self.agent(
                ticker=self.ticker,
                start_date=lookback_start,
                end_date=current_date_str,
                portfolio=self.portfolio,
            )

            action, quantity = self.parse_action(agent_output)
            df = get_price_data(self.ticker, lookback_start, current_date_str)
            current_price = df.iloc[-1]["close"]

            executed_quantity = self.execute_trade(action, quantity, current_price)

            total_value = (
                self.portfolio["cash"] + self.portfolio["crypto"] * current_price
            )
            self.portfolio["portfolio_value"] = total_value

            print(
                f"{current_date.strftime('%Y-%m-%d'):<12} {self.ticker:<6} {action:<6} {executed_quantity:>8} {current_price:>8.2f} "
                f"{self.portfolio['cash']:>12.2f} {self.portfolio['crypto']:>8} {total_value:>12.2f}"
            )

            self.portfolio_values.append(
                {"Date": current_date, "Portfolio Value": total_value}
            )

    def analyze_performance(self):
        performance_df = pd.DataFrame(self.portfolio_values).set_index("Date")

        total_return = (
            self.portfolio["portfolio_value"] - self.initial_capital
        ) / self.initial_capital
        print(f"Total Return: {total_return * 100:.2f}%")

        performance_df["Portfolio Value"].plot(
            title="Portfolio Value Over Time", figsize=(12, 6)
        )
        plt.ylabel("Portfolio Value ($)")
        plt.xlabel("Date")
        plt.show()

        performance_df["Daily Return"] = performance_df["Portfolio Value"].pct_change()

        mean_daily_return = performance_df["Daily Return"].mean()
        std_daily_return = performance_df["Daily Return"].std()
        sharpe_ratio = (mean_daily_return / std_daily_return) * (252**0.5)
        print(f"Sharpe Ratio: {sharpe_ratio:.2f}")

        rolling_max = performance_df["Portfolio Value"].cummax()
        drawdown = performance_df["Portfolio Value"] / rolling_max - 1
        max_drawdown = drawdown.min()
        print(f"Maximum Drawdown: {max_drawdown * 100:.2f}%")

        return performance_df


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run cryptocurrency backtesting simulation")
    parser.add_argument("--ticker", type=str, help="Cryptocurrency ticker symbol (e.g., BTC)")
    parser.add_argument(
        "--end_date",
        type=str,
        default=datetime.now().strftime("%Y-%m-%d"),
        help="End date in YYYY-MM-DD format",
    )
    parser.add_argument(
        "--start_date",
        type=str,
        default=(datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d"),
        help="Start date in YYYY-MM-DD format",
    )
    parser.add_argument(
        "--initial_capital",
        type=float,
        default=100000,
        help="Initial capital amount in USD (default: 100000)",
    )

    args = parser.parse_args()

    backtester = Backtester(
        agent=run_hedge_fund,
        ticker=args.ticker,
        start_date=args.start_date,
        end_date=args.end_date,
        initial_capital=args.initial_capital,
    )

    backtester.run_backtest()
    performance_df = backtester.analyze_performance()
