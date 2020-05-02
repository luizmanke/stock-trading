#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# System libraries
import pandas as pd


# TODO: Improve market trend
class Strategy():

    def __init__(self):
        super(Strategy, self).__init__()

    @staticmethod
    def get_companies_rates(companies_data, market_data):
        DESCENDING_KEY = "roic"
        ASCENDING_KEY = "pe"

        # Filter data
        data = companies_data[companies_data["volume"] > 20000]
        data = data[data["cagr"] > 0.05]
        data = data[data[DESCENDING_KEY] > 0]
        data = data[data[ASCENDING_KEY] > 0]
        data = data[[DESCENDING_KEY, ASCENDING_KEY, "price"]]

        # Rate subset
        new_descending_key = f"{DESCENDING_KEY}_rate"
        new_ascending_key = f"{ASCENDING_KEY}_rate"
        rates_list = range(data.shape[0])
        data = data.sort_values(DESCENDING_KEY, ascending=False)
        data[new_descending_key] = rates_list
        data = data.sort_values(ASCENDING_KEY)
        data[new_ascending_key] = rates_list

        # Rate companies
        data["rate"] = data[new_descending_key] + data[new_ascending_key]
        data = data.sort_values("rate")

        # Market trend
        WINDOW = 200
        market_mean = market_data["price"].ewm(span=WINDOW, min_periods=WINDOW).mean()
        difference = market_mean - market_mean.shift(1)
        trend = difference.where(difference < 0, 1)
        trend = trend.where(trend >= 0, -1)
        market_trend = trend.iloc[-1]

        return data, market_trend
