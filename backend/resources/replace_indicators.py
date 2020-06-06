#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# System libraries
import datetime as dt
import pandas as pd

# Own libraries
from ..common import database
from ..analytics.strategy import Strategy


def run():
    fundamentals, quotations = _get_data()
    indicators = _compute_indicators(fundamentals, quotations)
    _delete_colection()
    _insert_data(indicators)


def _get_data():
    fields = {"ticker": 1, "occurredAt": 1, "cagr": 1,
              "returnOnInvestedCapital": 1, "priceToEarnings": 1}
    fundamentals = database.find(collection="fundamentals", projection=fields)
    fundamentals = pd.DataFrame(fundamentals)

    fields = {"ticker": 1, "occurredAt": 1, "close": 1, "volume": 1}
    quotations = database.find(collection="quotations", projection=fields)
    quotations = pd.DataFrame(quotations)

    return fundamentals, quotations


def _compute_indicators(fundamentals, quotations):
    indicators = []
    for index in set(fundamentals["occurredAt"]):

        index_fundamentals = fundamentals[fundamentals["occurredAt"] == index]
        index_quotations = quotations[
            (quotations["occurredAt"] <= index) &
            (quotations["occurredAt"] > (index - dt.timedelta(days=150)))]
        new_indicators = Strategy().get_indicators(index_fundamentals, index_quotations)
        for item in new_indicators:
            item["occurredAt"] = index

        indicators = indicators + new_indicators
    return indicators


def _delete_colection():
    fields = {"ticker": 1, "occurredAt": 1}
    indicators = database.find(collection="indicators", projection=fields)
    connection = database._get_connection()
    connection["indicators"].drop()
    print(f" > {len(indicators)} items deleted")


def _insert_data(indicators):
    n_inserted = database.insert(indicators, "indicators")
    print(f" > {n_inserted} items inserted")
