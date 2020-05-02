#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# System libraries
import datetime as dt
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pickle
import os
from dateutil.relativedelta import relativedelta

# Own libraries
from strategy import Strategy
from wallet import Wallet

# Configurations
directory = os.path.dirname(__file__)


# TODO: Compute indicators only once
class Backtest(Strategy, Wallet):

    def __init__(self):
        super(Backtest, self).__init__()
        self.data_ = pd.DataFrame()
        self.baseline_ = pd.DataFrame()
        self.comparison_ = pd.DataFrame()

        # Private variables
        self._periods = []

    def run(self):

        # Setup
        print("Setting up...")
        self._setup()

        # Loop setups
        print("Evaluating...")
        stats, base_stats = [], []
        for i, period in enumerate(self._periods):
            print(f" > {i+1}/{len(self._periods)}")

            # Compute results
            results = self._evaluate(period)
            overall_stats = self._get_overall_statistics(results)
            monthly_stats = self._get_monthly_statistics(results)

            # Compute baseline
            base_results = self._evaluate_baseline(period)
            base_overall_stats = self._get_overall_statistics(base_results)
            base_monthly_stats = self._get_monthly_statistics(base_results)

            # Compare
            better_months = self._get_better_months(monthly_stats,
                                                    base_monthly_stats)
            overall_stats["better_months"] = better_months
            base_overall_stats["better_months"] = 1 - better_months

            # Append
            stats.append(overall_stats)
            base_stats.append(base_overall_stats)

            # Plot
            self._plot_results(results, base_results, period)

        # Save results
        self._compare_and_save(stats, base_stats)

    def _evaluate(self, period):

        # Filter data
        data = self.data_
        period_data = data[(data.index > period["from"]) & (data.index < period["to"])]
        indexes = sorted(set(period_data.index))

        # Loop indexes
        deals = []
        self.wallet_ = {"remaining_cash": 100000}
        self.logs_ = pd.DataFrame(columns=self._LOGS_COLUMNS)
        for index in indexes:

            # Update wallet
            index_data = period_data[period_data.index == index]
            index_data = index_data.set_index("ticker")
            index_data = index_data[["price"]]
            self.update_wallet(deals, index_data, index)

            # Update deals
            market_data = self.baseline_[self.baseline_.index <= index]
            minimum_index = index - relativedelta(months=4)
            companies_data = data[(data.index <= index) & (data.index > minimum_index)]
            companies_data = companies_data.dropna(subset=["roic", "pe", "cagr"])
            companies_data = companies_data.drop_duplicates("ticker", keep="last")
            companies_data = companies_data.set_index("ticker")
            rates, market_trend = self.get_companies_rates(companies_data, market_data)
            deals = self.get_deals(index, rates, market_trend)

        return self.logs_.copy()

    def _evaluate_baseline(self, period):

        # Filter data
        data = self.baseline_
        data = data[(data.index > period["from"]) & (data.index < period["to"])]

        # Evaluate
        initial_patrimony = data["price"].iloc[0]
        final_patrimony = data["price"].iloc[-1]
        profit = final_patrimony - initial_patrimony
        profit_percentage = profit / initial_patrimony

        # Results
        results = data["price"].to_frame("patrimony")
        results["n_trades_with_gain"] = 0
        results["n_trades_with_loss"] = 0
        results["gain_profit"] = 0
        results["loss_profit"] = 0
        results["avg_gain_profit_percentage"] = 0
        results["avg_loss_profit_percentage"] = 0
        n_trades_key = "n_trades_with_gain"
        profit_key = "gain_profit"
        percentage_key = "avg_gain_profit_percentage"
        if initial_patrimony < final_patrimony:
            n_trades_key = "n_trades_with_loss"
            profit_key = "loss_profit"
            percentage_key = "avg_loss_profit_percentage"
        last_index = results.index[-1]
        results.loc[last_index, n_trades_key] = 1
        results.loc[last_index, profit_key] = profit
        results.loc[last_index, percentage_key] = profit_percentage

        return results

    @staticmethod
    def _get_overall_statistics(results):
        patrimony = results["patrimony"]

        # Profit
        initial_patrimony = patrimony.iloc[0]
        final_patrimony = patrimony.iloc[-1]
        profit = final_patrimony - initial_patrimony
        profit_in_percentage = 100 * profit / initial_patrimony

        # Annual profit
        indexes = patrimony.index
        delta = indexes[-1] - indexes[0]
        delta_years = delta.days / 365
        annual_profit_percentage = 100 * (((1 + profit_in_percentage/100) **
                                           (1/delta_years)) - 1)

        # Sharp ratio
        daily_returns = patrimony.pct_change(1)
        avg_daily_returns = daily_returns.mean()
        std_daily_returns = daily_returns.std()
        daily_sharpe_ratio = avg_daily_returns / std_daily_returns
        sharpe_ratio = (252 ** 0.5) * daily_sharpe_ratio

        # Drawdown
        rolling_maximum = patrimony.cummax()
        drawdowns = 100 * (patrimony - rolling_maximum) / rolling_maximum
        drawdowns = drawdowns.dropna()
        maximum_drawdown_percentage = min(drawdowns)

        # Trades
        n_trades_with_gain = results["n_trades_with_gain"].sum()
        n_trades_with_loss = results["n_trades_with_loss"].sum()
        total_trades = n_trades_with_gain + n_trades_with_loss

        # Trades percentage
        percentage_of_gain_trades = 100 * n_trades_with_gain / total_trades
        percentage_of_loss_trades = 100 * n_trades_with_loss / total_trades

        # Mean profit
        gain_tmp = n_trades_with_gain if n_trades_with_gain else 1
        loss_tmp = n_trades_with_loss if n_trades_with_loss else 1
        avg_gain_per_trade = results["gain_profit"].sum() / gain_tmp
        avg_loss_per_trade = results["loss_profit"].sum() / loss_tmp
        avg_gain_percentage = ((results["n_trades_with_gain"] *
                                results["avg_gain_profit_percentage"]).sum() /
                               gain_tmp) * 100
        avg_loss_percentage = ((results["n_trades_with_loss"] *
                                results["avg_loss_profit_percentage"]).sum() /
                               loss_tmp) * 100

        # Payoff
        payoff = profit / total_trades

        # Factors
        loss_profit = results["loss_profit"].sum()
        loss_profit = loss_profit if loss_profit else 1
        profit_factor = abs(results["gain_profit"].sum() / loss_profit)
        recuperation_factor = abs(profit / maximum_drawdown_percentage)

        # Return
        statistics = {}
        statistics["annual_profit_percentage"] = annual_profit_percentage
        statistics["sharpe_ratio"] = sharpe_ratio
        statistics["maximum_drawdown_percentage"] = maximum_drawdown_percentage
        statistics["total_trades"] = total_trades
        statistics["percentage_of_gain_trades"] = percentage_of_gain_trades
        statistics["percentage_of_loss_trades"] = percentage_of_loss_trades
        statistics["avg_gain_per_trade"] = avg_gain_per_trade
        statistics["avg_loss_per_trade"] = avg_loss_per_trade
        statistics["avg_gain_percentage"] = avg_gain_percentage
        statistics["avg_loss_percentage"] = avg_loss_percentage
        statistics["payoff"] = payoff
        statistics["profit_factor"] = profit_factor
        statistics["recuperation_factor"] = recuperation_factor
        return statistics

    @staticmethod
    def _get_monthly_statistics(results):
        patrimony = results["patrimony"]
        statistics = []

        # Loop indexes
        monthly_patrimony = patrimony.resample("M").last()
        previous_patrimony = patrimony.iloc[0]
        for index, current_patrimony in monthly_patrimony.iteritems():
            percentage = ((current_patrimony - previous_patrimony)
                          / previous_patrimony * 100)
            statistics.append({"year": index.year,
                               "month": index.month,
                               "percentage": percentage})
            previous_patrimony = current_patrimony

        statistics = pd.DataFrame(statistics)
        return statistics

    @staticmethod
    def _get_better_months(monthly_stats_1, monthly_stats_2):
        better_months = 0
        for _, row in monthly_stats_1.iterrows():
            year = row["year"]
            month = row["month"]
            data = monthly_stats_2[(monthly_stats_2["year"] == year) &
                                   (monthly_stats_2["month"] == month)]
            if row["percentage"] >= data["percentage"].iloc[0]:
                better_months += 1
        better_months = better_months / monthly_stats_1.shape[0]
        return better_months

    @staticmethod
    def _plot_results(results, base_results, period):
        data = results["patrimony"] / results["patrimony"].iloc[0]
        base = base_results["patrimony"] / base_results["patrimony"].iloc[0]
        from_ = dt.datetime.strftime(period["from"], "%Y-%m-%d")
        to = dt.datetime.strftime(period["to"], "%Y-%m-%d")
        fig, ax = plt.subplots()
        data.plot(ax=ax, label="backtest")
        base.plot(ax=ax, label="baseline")
        plt.legend(loc="best")
        plt.title(f"{from_}  to  {to}")
        plt.xlabel("Timestamp")
        plt.ylabel("Profit in Percentage")
        plt.savefig(f"{directory}/backtest/{from_}_{to}.png", dpi=300)
        plt.close(fig)

    def _compare_and_save(self, results, baseline):

        # Results
        results_dataframe = pd.DataFrame(results)
        annual_profit_percentage = results_dataframe.pop("annual_profit_percentage")
        results_mean = results_dataframe.mean()
        results_mean["median_annual_profit_percentage"] = np.median(annual_profit_percentage)
        results_mean["mean_annual_profit_percentage"] = np.mean(annual_profit_percentage)
        results_mean["max_annual_profit_percentage"] = np.max(annual_profit_percentage)
        results_mean["min_annual_profit_percentage"] = np.min(annual_profit_percentage)
        results_mean["std_annual_profit_percentage"] = np.std(annual_profit_percentage)

        # Baseline
        baseline_dataframe = pd.DataFrame(baseline)
        annual_profit_percentage = baseline_dataframe.pop("annual_profit_percentage")
        baseline_mean = baseline_dataframe.mean()
        baseline_mean["median_annual_profit_percentage"] = np.median(annual_profit_percentage)
        baseline_mean["mean_annual_profit_percentage"] = np.mean(annual_profit_percentage)
        baseline_mean["max_annual_profit_percentage"] = np.max(annual_profit_percentage)
        baseline_mean["min_annual_profit_percentage"] = np.min(annual_profit_percentage)
        baseline_mean["std_annual_profit_percentage"] = np.std(annual_profit_percentage)

        # Concatenate
        comparison = results_mean.to_frame("backtest")
        comparison["baseline"] = baseline_mean
        comparison = comparison.round(2)

        # Save
        comparison.to_csv(f"{directory}/backtest/comparison.csv")
        self.comparison_ = comparison

    def _setup(self):
        MAX_PERIODS_PER_SETUP = 100
        SETUP_LIST = [{"duration_in_years": 3, "months_btw_periods": 4},
                      {"duration_in_years": 5, "months_btw_periods": 2}]

        # Load data
        BASELINE_TICKER = "IBOV"
        BLOCK_TICKERS = []
        with open(f"{directory}/backtest/input_data.pkl", "rb") as file:
            data = pickle.load(file)
        for ticker in BLOCK_TICKERS:
            data = data[data["ticker"] != ticker]
        self.baseline_ = data[data["ticker"] == BASELINE_TICKER]
        self.data_ = data[data["ticker"] != BASELINE_TICKER]

        # Loop setups
        self._periods = []
        minimum_date = pd.to_datetime("2012-01-01")
        maximum_date = max(self.data_.index)
        for setup in SETUP_LIST:
            duration_in_years = setup["duration_in_years"]
            months_btw_periods = setup["months_btw_periods"]

            # Loop periods
            initial_date = minimum_date
            for _ in range(MAX_PERIODS_PER_SETUP):
                final_date = initial_date + relativedelta(years=duration_in_years)
                final_date = final_date if final_date < maximum_date else maximum_date
                new_period = {"from": initial_date, "to": final_date}
                self._periods.append(new_period)
                initial_date = initial_date + relativedelta(months=months_btw_periods)
                if final_date >= maximum_date:
                    break


if __name__ == "__main__":

    # Run
    initial_time = dt.datetime.now()
    backtest = Backtest()
    backtest.run()
    elapsed_time = dt.datetime.now() - initial_time
    print(f"Elapsed time: {elapsed_time}")
