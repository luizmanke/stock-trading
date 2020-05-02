#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# System libraries
import datetime as dt
import pandas as pd


class Wallet():

    def __init__(self, remaining_cash=100000):
        super(Wallet, self).__init__()
        self._LOGS_COLUMNS = ["patrimony", "n_trades_with_gain",
                              "n_trades_with_loss", "gain_profit",
                              "loss_profit", "avg_gain_profit_percentage",
                              "avg_loss_profit_percentage"]
        self.wallet_ = {"remaining_cash": remaining_cash}
        self.logs_ = pd.DataFrame(columns=self._LOGS_COLUMNS)

        # Private variables
        self._patrimony = 0
        self._virtual_remaining_cash = 0
        self._month_initial_cash = 0
        self._month_current_loss = 0

    # TODO: Add transaction charge
    def update_wallet(self, input_deals, data, index):
        wallet = self.wallet_

        # Loop deals
        output_deals = {}
        trades = []
        for ticker, deal in input_deals.items():
            start_price = deal["start"]
            if ticker not in data.index:
                continue

            # Buy
            if deal["operation"] == "buy":
                if deal["trend"] == "positive":
                    available = data.loc[ticker, "high"] >= start_price
                elif deal["trend"] == "negative":
                    available = data.loc[ticker, "low"] <= start_price
                if available:
                    output_deals[ticker] = self._insert_in_wallet(index,
                                                                  ticker,
                                                                  deal)

            # Sell
            elif deal["operation"] == "sell":
                if deal["trend"] == "positive":
                    available = data.loc[ticker, "low"] <= start_price
                elif deal["trend"] == "negative":
                    available = data.loc[ticker, "high"] >= start_price
                if available:
                    new_trade = self._remove_from_wallet(ticker, deal)
                    trades.append(new_trade)

        # Update values
        for ticker, item in wallet.items():
            if ticker in data.index:
                item["date"] = index
                item["current_price"] = data.loc[ticker, "close"]

        # Update logs
        self._update_logs(index, trades)

        return output_deals

    def _insert_in_wallet(self, index, ticker, deal):
        self.wallet_["remaining_cash"] -= (deal["n_stocks"] * deal["start"])
        self.wallet_[ticker] = {"date": index,
                                "n_stocks": deal["n_stocks"],
                                "initial_price": deal["start"],
                                "trend": deal["trend"]}
        new_deal = {"operation": "sell",
                    "trend": deal["trend"],
                    "date": index,
                    "n_stocks": None,
                    "start": deal["stop"],
                    "stop": None}
        return new_deal

    def _remove_from_wallet(self, ticker, deal):
        wallet = self.wallet_

        # Compute profit
        initial_price = wallet[ticker]["initial_price"]
        n_stocks = wallet[ticker]["n_stocks"]
        trend = wallet[ticker]["trend"]
        if trend == "positive":
            profit = n_stocks * (deal["start"] - initial_price)
        elif trend == "negative":
            profit = n_stocks * (initial_price - deal["start"])
        percentage = (profit / n_stocks) / initial_price

        # Update wallet
        wallet["remaining_cash"] += (n_stocks * deal["start"])
        wallet.pop(ticker)

        # Return details
        trade = {"profit": profit, "percentage": percentage}
        return trade

    def _update_logs(self, index, trades):
        wallet = self.wallet_.copy()

        # Compute patimony
        patrimony = wallet.pop("remaining_cash")
        for _, item in wallet.items():
            initial_price = item["initial_price"]
            current_price = item["current_price"]
            trend = item["trend"]
            if trend == "positive":
                profit = current_price - initial_price
            elif trend == "negative":
                profit = initial_price - current_price
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

    def get_deals(self, indicators):
        MAX_MONTH_LOSS = 0.05

        # Compute current status
        self._compute_current_status()

        # Loop indicators
        deals = {}
        indicators = indicators.sort_values("strength", ascending=False)
        for _, indicator in indicators.iterrows():
            new_deal = {}

            # Buy
            if indicator["sign"] == "buy":
                available = (self._month_current_loss <
                             self._month_initial_cash * MAX_MONTH_LOSS)
                if available:
                    new_deal = self._get_buy_deal(indicator)

            # Sell
            elif indicator["sign"] == "sell":
                new_deal = self._get_sell_deal(indicator)

            # Update deals
            if new_deal:
                deals[indicator["ticker"]] = new_deal

        return deals

    def _get_buy_deal(self, indicator):
        MAX_STOCK_LOSS = 0.005
        deal = {}

        if indicator["ticker"] not in self.wallet_:
            deal_loss = abs(indicator["start"] - indicator["stop"])
            n_stocks = int((self._patrimony * MAX_STOCK_LOSS) / deal_loss)
            deal_price = n_stocks * indicator["start"]
            if n_stocks > 0 and self._virtual_remaining_cash > deal_price:
                self._virtual_remaining_cash -= deal_price
                deal = {"operation": "buy",
                        "trend": indicator["trend"],
                        "date": indicator.name,
                        "n_stocks": n_stocks,
                        "start": indicator["start"],
                        "stop": indicator["stop"]}

        return deal

    def _get_sell_deal(self, indicator):
        deal = {}
        if indicator["ticker"] in self.wallet_:
            deal = {"operation": "sell",
                    "trend": indicator["trend"],
                    "date": indicator.name,
                    "n_stocks": None,
                    "start": indicator["start"],
                    "stop": None}
        return deal

    def _compute_current_status(self):
        current_date = dt.datetime.now()

        # Create initial logs
        if self.logs_.shape[0] == 0:
            self.logs_ = pd.DataFrame(
                {"patrimony": self.wallet_["remaining_cash"],
                 "loss_profit": 0},
                index=[current_date])

        # Get month status
        logs = self.logs_
        last_log_index = logs.index[-1]
        case_1 = last_log_index.year == current_date.year
        case_2 = last_log_index.month == current_date.month
        if case_1 and case_2:

            # Get initial month patrimony
            monthly_logs_start = logs.resample("MS").first()
            month_initial_cash = monthly_logs_start["patrimony"].iloc[-1]

            # Get current month loss
            monthly_logs_end = logs.resample("M").last()
            month_current_loss = monthly_logs_end["loss_profit"].iloc[-1]

        else:
            month_initial_cash = logs["patrimony"].iloc[-1]
            month_current_loss = 0

        self._month_initial_cash = month_initial_cash
        self._month_current_loss = month_current_loss

        # Get current patrimony
        self._patrimony = self.logs_["patrimony"].iloc[-1]

        # Get current remaining cash
        self._virtual_remaining_cash = self.wallet_["remaining_cash"]
