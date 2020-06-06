#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# System libraries
import operator
import pandas as pd
from dateutil.relativedelta import relativedelta


class Dealer:

    def __init__(self):
        self.deals_ = []

    def compute_deals(self, wallet, data, indicators, index):
        self.deals_ = []
        indicators = self._preprocess_indicators(indicators)
        self._create_sell_deals(wallet, indicators, index)
        spots_left = self._compute_spots_left_in_wallet(wallet)
        if spots_left and indicators.loc["IBOV", "trend"] != -1:
            filtered_indicators = self._filter_indicators(wallet, indicators)
            self._create_buy_deals(wallet, data, filtered_indicators, spots_left)
        return self.deals_

    @staticmethod
    def _preprocess_indicators(indicators):
        indicators = pd.DataFrame(indicators)
        indicators = indicators.set_index("ticker")
        return indicators

    def _create_sell_deals(self, wallet, indicators, index):
        MONTHS_TO_HOLD_STOCK = 6
        wallet = {key: value for key, value in wallet.items() if key != "remaining_cash"}
        for ticker, item in wallet.items():
            max_index = item["initial_date"] + relativedelta(months=MONTHS_TO_HOLD_STOCK)
            market_trend = indicators.loc["IBOV", "trend"]
            if (index >= max_index) or (market_trend == -1):
                self.deals_.append({"ticker": ticker, "operation": "sell"})

    def _compute_spots_left_in_wallet(self, wallet):
        MAX_COMPANIES_IN_WALLET = 20
        wallet = {key: value for key, value in wallet.items() if key != "remaining_cash"}
        spots_left = MAX_COMPANIES_IN_WALLET - len(wallet) + len(self.deals_)
        return spots_left

    @staticmethod
    def _filter_indicators(wallet, indicators):
        TOP_COMPANIES = 30
        indicators = indicators.dropna(subset=["rank"])
        indicators = indicators.sort_values("rank")
        indicators = indicators.iloc[:TOP_COMPANIES]
        for ticker in wallet:
            indicators = indicators.drop(ticker, errors="ignore")
        return indicators

    def _create_buy_deals(self, wallet, data, indicators, spots_left):
        remaining_cash = wallet["remaining_cash"]
        cash_per_company = remaining_cash / spots_left
        for ticker, row in indicators.iterrows():
            if row["trend"] != 1:
                continue

            price = data[ticker]["close"]
            n_stocks = int(cash_per_company / price)
            remaining_cash -= n_stocks * price
            self.deals_.append({"ticker": ticker,
                                "operation": "buy",
                                "n_stocks": n_stocks,
                                "price": price})

            spots_left -= 1
            if spots_left == 1:
                cash_per_company = remaining_cash
            elif spots_left == 0:
                break


class Record:
    _RECORD_COLUMNS = ["patrimony", "n_trades_with_gain", "n_trades_with_loss",
                       "gain_profit", "loss_profit", "avg_gain_profit_percentage",
                       "avg_loss_profit_percentage"]

    def __init__(self):
        self.records_ = pd.DataFrame(columns=self._RECORD_COLUMNS)

    def update_records(self, wallet, trades, index):
        new_record = pd.Series(index=self._RECORD_COLUMNS)
        self._compute_patrimony(wallet, new_record)
        self._compute_gain_statistics(trades, new_record)
        self._compute_loss_statistics(trades, new_record)
        self.records_.loc[index] = new_record

    @staticmethod
    def _compute_patrimony(wallet, record):
        patrimony = wallet["remaining_cash"]
        wallet = {key: value for key, value in wallet.items() if key != "remaining_cash"}
        for _, item in wallet.items():
            initial_price = item["initial_price"]
            current_price = item["current_price"]
            profit = current_price - initial_price
            patrimony += (item["n_stocks"] * (initial_price + profit))
        record["patrimony"] = patrimony

    def _compute_gain_statistics(self, trades, record):
        n_trades, profit, avg_profit_in_percentage = \
            self._compute_trade_statistics(trades, operator.ge)
        record["n_trades_with_gain"] = n_trades
        record["gain_profit"] = profit
        record["avg_gain_profit_percentage"] = avg_profit_in_percentage

    def _compute_loss_statistics(self, trades, record):
        n_trades, profit, avg_profit_in_percentage = \
            self._compute_trade_statistics(trades, operator.lt)
        record["n_trades_with_loss"] = n_trades
        record["loss_profit"] = profit
        record["avg_loss_profit_percentage"] = avg_profit_in_percentage

    @staticmethod
    def _compute_trade_statistics(trades, operator):
        n_trades = 0
        profit = 0
        sum_of_profit_in_percentage_sum = 0
        for trade in trades:
            if operator(trade["profit"], 0):
                n_trades += 1
                profit += trade["profit"]
                sum_of_profit_in_percentage_sum += trade["percentage"]

        avg_profit_in_percentage = 0
        if n_trades > 0:
            avg_profit_in_percentage = (sum_of_profit_in_percentage_sum / n_trades)
        return n_trades, profit, avg_profit_in_percentage


# TODO: Add transaction charge
# TODO: Add DARF charge
# TODO: Operate in downtrend
class Wallet(Dealer, Record):

    def __init__(self, remaining_cash):
        Dealer.__init__(self)
        Record.__init__(self)
        self.wallet_ = {"remaining_cash": remaining_cash}

    def compute_deals(self, data, indicators, index):
        Dealer.compute_deals(self, self.wallet_, data, indicators, index)

    def update_wallet(self, data, index):
        new_trades = []
        for deal in self.deals_:
            ticker = deal["ticker"]
            if ticker not in data:
                continue

            if deal["operation"] == "buy":
                self._insert_in_wallet(ticker, deal, index)
            elif deal["operation"] == "sell":
                new_trade = self._remove_from_wallet(ticker, deal)
                new_trades.append(new_trade)

        self._update_prices(data, index)
        self.update_records(self.wallet_, new_trades, index)

    def _insert_in_wallet(self, ticker, deal, index):
        self.wallet_["remaining_cash"] -= (deal["n_stocks"] * deal["price"])
        self.wallet_[ticker] = {"initial_date": index,
                                "n_stocks": deal["n_stocks"],
                                "initial_price": deal["price"]}

    def _remove_from_wallet(self, ticker, deal):
        item = self.wallet_[ticker]
        trade = self._compute_trade_profit(ticker)
        self.wallet_["remaining_cash"] += (item["n_stocks"] * item["current_price"])
        self.wallet_.pop(ticker)
        return trade

    def _compute_trade_profit(self, ticker):
        current_price = self.wallet_[ticker]["current_price"]
        initial_price = self.wallet_[ticker]["initial_price"]
        n_stocks = self.wallet_[ticker]["n_stocks"]
        profit = n_stocks * (current_price - initial_price)
        percentage = (current_price - initial_price) / initial_price
        return {"profit": profit, "percentage": percentage}

    def _update_prices(self, data, index):
        for ticker, item in self.wallet_.items():
            if ticker in data:
                item["current_date"] = index
                item["current_price"] = data[ticker]["close"]
