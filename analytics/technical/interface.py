#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# System libraries
import datetime as dt
import os
import pandas as pd
import pickle

# Own libraries
from connection import Connection
from database import Database
from strategy import Strategy
from wallet import Wallet

# Configurations
directory = os.path.dirname(__file__)


# TODO: Add multiprocessing
class Interface(Connection, Database, Strategy, Wallet):

    def __init__(self):
        UTC = -3
        super(Interface, self).__init__()
        self.companies_ = {}

        # Private variables
        index = dt.datetime.utcnow() + dt.timedelta(hours=UTC)
        index = index.strftime("%Y-%m-%d")
        index = dt.datetime.strptime(index, "%Y-%m-%d")
        self._index = index
        self._trades = []

        self._load_data_and_configurations()
        self._update_database()

    def update_remaining_cash(self):
        new_remaining_cash = input("How much cash you have left? ")
        self.wallet_["remaining_cash"] = float(new_remaining_cash)

    def update_wallet(self):

        # Request inputs
        operation = input("What was the operation? (buy/sell) ")
        assert operation in ["buy", "sell"], "Operation must be 'buy' or 'sell'."

        ticker = input("What was the ticker? ")
        if operation == "sell":
            assert ticker in self.wallet_, "Ticker is not in wallet."

        index = input("When the trade occurred? (yyyy-mm-dd) ")
        index = dt.datetime.strptime(index, "%Y-%m-%d")

        n_stocks = input("How many stocks? ")
        price = input("What was the price? ")

        # Update wallet
        deal = {"n_stocks": int(n_stocks), "price": float(price)}
        if operation == "buy":
            self._insert_in_wallet(index, ticker, deal)
        else:
            new_trades = self._remove_from_wallet(ticker, deal)
            self._trades = self._trades + new_trades

        # Update data
        data = self.data_.loc[self._index]
        self._update_logs(index, self._trades, data)
        self._save_data_and_configurations()

    def update_deals(self):
        last_indicators = self._get_last_indicators()
        deals = self.get_deals(last_indicators)
        print(deals)

    def _get_last_indicators(self):
        indicators = self.indicators_
        indexes = indicators.index
        last_index = max(indexes)
        last_indicators = indicators[indicators.index == last_index]
        return last_indicators

    def _update_database(self):
        print("Updating database...")

        # Update companies
        if (self._index.day == 1) or (len(self.companies_) == 0):
            companies = self.request_companies()
            self.companies_.update(companies)

        # Loop companies
        minimum_date = self._index
        tickers = set(self.data_["ticker"])
        for ticker, item in self.companies_.items():
            initial_date_str = "01/01/2015"
            initial_date = pd.to_datetime(initial_date_str)

            # Update quotations
            if ticker in tickers:
                data = self.data_[self.data_["ticker"] == ticker]
                maximum_date = max(data.index)
                initial_date = maximum_date - dt.timedelta(days=15)
                initial_date_str = initial_date.strftime("%d/%m/%Y")
                if self._index - maximum_date >= dt.timedelta(days=1):
                    continue
            quotations = self.request_quotations({ticker: item}, initial_date_str)

            # Update database
            self.update_database(quotations)

            if initial_date < minimum_date:
                minimum_date = initial_date

        # Update indicators
        if self.indicators_.shape[0] > 0:
            indicators_date = max(self.indicators_.index) - dt.timedelta(days=90)
            if minimum_date > indicators_date:
                minimum_date = indicators_date
        data = self.data_[self.data_.index >= minimum_date]
        self.update_indicators(data)

        self._save_data_and_configurations()

    def _load_data_and_configurations(self):
        try:
            with open(f"{directory}/interface/database.pkl", "rb") as file:
                dictionary = pickle.load(file)
            self._from_dict(dictionary)
            print("Interface initiated with a saved database.")
        except Exception:
            print("Interface initiated with an empty database.")

    def _save_data_and_configurations(self):
        try:
            dictionary = self._to_dict()
            with open(f"{directory}/interface/database.pkl", "wb") as file:
                pickle.dump(dictionary, file)
            print("Data and configurations saved.")
        except Exception:
            print("Data and configurations not saved.")

    def _from_dict(self, dictionary):
        self.companies_ = dictionary["companies_"]
        self.data_ = dictionary["data_"]
        self.indicators_ = dictionary["indicators_"]
        self.wallet_ = dictionary["wallet_"]
        self.logs_ = dictionary["logs_"]

    def _to_dict(self):
        dictionary = {"companies_": self.companies_,
                      "data_": self.data_,
                      "indicators_": self.indicators_,
                      "wallet_": self.wallet_,
                      "logs_": self.logs_}
        return dictionary


if __name__ == "__main__":

    # Run
    initial_time = dt.datetime.now()
    interface = Interface()
    interface.update_deals()
    elapsed_time = dt.datetime.now() - initial_time
    print(f"Elapsed time: {elapsed_time}")
