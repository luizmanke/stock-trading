#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# System libraries
import pandas as pd
from dateutil.relativedelta import relativedelta


# TODO: Buy only if the stock trend is up
# TODO: Operate in downtrend
class Wallet():

    def __init__(self, remaining_cash=100000):
        super(Wallet, self).__init__()
        self._LOGS_COLUMNS = ["patrimony", "n_trades_with_gain",
                              "n_trades_with_loss", "gain_profit",
                              "loss_profit", "avg_gain_profit_percentage",
                              "avg_loss_profit_percentage"]
        self.wallet_ = {"remaining_cash": remaining_cash}
        self.logs_ = pd.DataFrame(columns=self._LOGS_COLUMNS)

    # TODO: Add transaction charge
    def update_wallet(self, deals, data, index):
        wallet = self.wallet_

        # Loop deals
        trades = []
        for deal in deals:
            ticker = deal["ticker"]
            if ticker not in data.index:
                continue

            # Buy
            if deal["operation"] == "buy":
                self._insert_in_wallet(index, ticker, deal)

            # Sell
            elif deal["operation"] == "sell":
                new_trade = self._remove_from_wallet(ticker, deal)
                trades.append(new_trade)

        # Update logs
        self._update_logs(index, trades, data)

    def _insert_in_wallet(self, index, ticker, deal):
        self.wallet_["remaining_cash"] -= (deal["n_stocks"] * deal["price"])
        self.wallet_[ticker] = {"current_date": None,
                                "initial_date": index,
                                "n_stocks": deal["n_stocks"],
                                "current_price": None,
                                "initial_price": deal["price"]}

    def _remove_from_wallet(self, ticker, deal):
        wallet = self.wallet_

        # Compute profit
        current_price = wallet[ticker]["current_price"]
        initial_price = wallet[ticker]["initial_price"]
        n_stocks = wallet[ticker]["n_stocks"]
        profit = n_stocks * (current_price - initial_price)
        percentage = (current_price - initial_price) / initial_price

        # Update wallet
        wallet["remaining_cash"] += (n_stocks * current_price)
        wallet.pop(ticker)

        # Return details
        trade = {"profit": profit, "percentage": percentage}
        return trade

    def _update_logs(self, index, trades, data):
        wallet = self.wallet_.copy()

        # Update values
        for ticker, item in wallet.items():
            if ticker in data.index:
                item["current_date"] = index
                item["current_price"] = data.loc[ticker, "price"]

        # Compute patimony
        patrimony = wallet.pop("remaining_cash")
        for _, item in wallet.items():
            initial_price = item["initial_price"]
            current_price = item["current_price"]
            profit = current_price - initial_price
            patrimony += (item["n_stocks"] * (initial_price + profit))

        # Loop trades
        n_trades_with_gain = 0
        n_trades_with_loss = 0
        gain_profit = 0
        loss_profit = 0
        gain_profit_percentage_sum = 0
        loss_profit_percentage_sum = 0
        for trade in trades:

            # Gain
            if trade["profit"] >= 0:
                n_trades_with_gain += 1
                gain_profit += trade["profit"]
                gain_profit_percentage_sum += trade["percentage"]

            # Loss
            else:
                n_trades_with_loss += 1
                loss_profit += trade["profit"]
                loss_profit_percentage_sum += trade["percentage"]

        # Percentage profit
        avg_gain_profit_percentage = 0
        avg_loss_profit_percentage = 0
        if n_trades_with_gain:
            avg_gain_profit_percentage = (gain_profit_percentage_sum /
                                          n_trades_with_gain)
        if n_trades_with_loss:
            avg_loss_profit_percentage = (loss_profit_percentage_sum /
                                          n_trades_with_loss)

        # Update variable
        new_log = {}
        new_log["patrimony"] = patrimony
        new_log["n_trades_with_gain"] = n_trades_with_gain
        new_log["n_trades_with_loss"] = n_trades_with_loss
        new_log["gain_profit"] = gain_profit
        new_log["loss_profit"] = loss_profit
        new_log["avg_gain_profit_percentage"] = avg_gain_profit_percentage
        new_log["avg_loss_profit_percentage"] = avg_loss_profit_percentage
        new_log_dataframe = pd.Series(new_log)
        self.logs_.loc[index] = new_log_dataframe

    def get_deals(self, index, indicators, trend):
        MONTHS_TO_HOLD_STOCK = 6
        N_COMPANIES = 20
        wallet = self.wallet_.copy()
        remaining_cash = wallet.pop("remaining_cash")
        deals = []

        # Sell
        for ticker, item in wallet.items():
            limit_index = item["initial_date"] + relativedelta(months=MONTHS_TO_HOLD_STOCK)
            if (index >= limit_index) or (trend == -1):
                deals.append({"ticker": ticker, "operation": "sell"})

        # Compute spots left in wallet
        spots_left = N_COMPANIES - len(wallet) + len(deals)
        if (not spots_left) or (trend == -1):
            return deals

        # Filter indicators
        indicators = indicators.sort_values("rate", ascending=False)
        for ticker in wallet:
            indicators = indicators.drop(ticker, errors="ignore")
        indicators = indicators.iloc[-spots_left:]

        # Buy
        cash_per_company = remaining_cash / spots_left
        for ticker, indicator in indicators.iterrows():
            if ticker == indicators.index[-1]:
                cash_per_company = remaining_cash
            n_stocks = int(cash_per_company / indicator["price"])
            remaining_cash -= (n_stocks * indicator["price"])
            deals.append({"ticker": ticker,
                          "operation": "buy",
                          "n_stocks": n_stocks,
                          "price": indicator["price"]})

        return deals
