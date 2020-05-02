#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# System libraries
import datetime as dt
import os
import pickle
from dateutil.relativedelta import relativedelta

# Own libraries
from connection import Connection
from database import Database
from strategy import Strategy
from wallet import Wallet

# Configurations
directory = os.path.dirname(__file__)


class Interface(Connection, Database, Strategy, Wallet):

    def __init__(self):
        super(Interface, self).__init__()
        self._load_data_and_configurations()
        self._update_database()

        # Private variables
        self._trades = []

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

    def get_deals(self):
        market_data = self.data_[self.data_["ticker"] == "IBOV"]
        companies_data = self.data_.loc[self._index]
        companies_data = companies_data.set_index("ticker")
        rates, trend = self.get_companies_rates(companies_data, market_data)
        deals = super(Interface, self).get_deals(self._index, rates, trend)
        self._save_data_and_configurations()
        return deals, rates, trend

    def _update_database(self):
        print("Updating database...")
        UTC = -3
        index = dt.datetime.utcnow() + dt.timedelta(hours=UTC)
        index = index.strftime("%Y-%m-%d")
        index = dt.datetime.strptime(index, "%Y-%m-%d")
        initial_index_str = (index - dt.timedelta(days=300)).strftime("%d/%m/%Y")
        indicators = self.request_indicators()
        market_data = self.request_market_data(initial_index_str)
        self.update_indicators(index, indicators)
        self.update_market_data(index, market_data)
        self._index = index

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
        self.data_ = dictionary["data_"]
        self.wallet_ = dictionary["wallet_"]
        self.logs_ = dictionary["logs_"]

    def _to_dict(self):
        dictionary = {"data_": self.data_,
                      "wallet_": self.wallet_,
                      "logs_": self.logs_}
        return dictionary


if __name__ == "__main__":

    # Run
    initial_time = dt.datetime.now()
    interface = Interface()
    deals, rate, trend = interface.get_deals()

    if not trend:
        print("Market in downtrend.")
    for deal in deals:
        print(deal)
    elapsed_time = dt.datetime.now() - initial_time
    print(f"Elapsed time: {elapsed_time}")
