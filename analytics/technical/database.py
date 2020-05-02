#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# System libraries
import datetime as dt
import pandas as pd


class Database():

    def __init__(self):
        super(Database, self).__init__()
        self.data_ = pd.DataFrame(columns=["ticker"])

    def update_database(self, quotations):

        # Loop tickers
        for ticker, new_data in quotations.items():

            # Create ticker dataframe
            new_data.index = [dt.datetime.strptime(date, "%d.%m.%Y")
                              for date in new_data.index]
            new_data = new_data.rename(columns={"Último": "close",
                                                "Abertura": "open",
                                                "Máxima": "high",
                                                "Mínima": "low",
                                                "Vol.": "volume",
                                                "Var%": "change"})
            new_data = new_data.drop("change", axis=1)

            # Convert to float
            new_data = new_data.replace(",", ".", regex=True)
            new_data = new_data.replace("%", "", regex=True)
            new_data = new_data.replace("-", float("nan"))
            new_data["multiplier"] = 1
            multiplier = new_data.pop("multiplier")
            multiplier = multiplier.where(new_data["volume"].str.find("K") < 0, 1000)
            multiplier = multiplier.where(new_data["volume"].str.find("M") < 0, 1000000)
            multiplier = multiplier.where(new_data["volume"].str.find("B") < 0, 1000000000)
            new_data = new_data.replace("K", "", regex=True)
            new_data = new_data.replace("M", "", regex=True)
            new_data = new_data.replace("B", "", regex=True)
            new_data = new_data.astype(float)

            # Rescale data
            for column in ["close", "open", "high", "low"]:
                new_data[column] = new_data[column] / 100
            new_data["volume"] = new_data["volume"] * multiplier

            # Update history
            new_data["ticker"] = ticker
            ticker_data = self.data_[self.data_["ticker"] == ticker]
            ticker_data = pd.concat([ticker_data, new_data])
            ticker_data = ticker_data[~ticker_data.index.duplicated(keep="last")]
            remaining_data = self.data_[self.data_["ticker"] != ticker]
            self.data_ = pd.concat([remaining_data, ticker_data])

        self.data_ = self.data_.sort_index()
