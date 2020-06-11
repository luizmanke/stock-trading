#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# System libraries
import datetime as dt
import pandas as pd

# Own libraries
from ..common import database
from ..analytics.strategy import Strategy


def run():
    print("Replacing...")
    fundamentals, quotations = _get_data()
    indicators = _compute_indicators(fundamentals, quotations)
    _delete_colection()
    _insert_data(indicators)


def _get_data():

    pipeline = [{"$sort": {"occurredAt": 1}},
                {"$group": {
                    "_id": "$ticker",
                    "ticker": {"$last": "$ticker"},
                    "occurredAt": {"$last": "$occurredAt"},
                    "cagr": {"$last": "$cagr"},
                    "returnOnInvestedCapital": {"$last": "$returnOnInvestedCapital"},
                    "priceToEarnings": {"$last": "$priceToEarnings"}}}]
    fundamentals = database.aggregate(pipeline, "fundamentals")

    index = max(fundamentals, key=lambda item: item["occurredAt"])["occurredAt"]
    minimum_index = index - dt.timedelta(days=150)
    filter = {"occurredAt": {"$gte": minimum_index}}
    fields = {"ticker": 1, "occurredAt": 1, "close": 1, "volume": 1}
    sort = [("occurredAt", 1)]
    quotations = database.find(
        collection="quotations", filter=filter, projection=fields, sort=sort)

    return fundamentals, quotations


def _compute_indicators(fundamentals, quotations):
    indicators = Strategy().get_indicators(fundamentals, quotations)
    index = max(fundamentals, key=lambda item: item["occurredAt"])["occurredAt"]
    for item in indicators:
        item["occurredAt"] = index
    return indicators


def _delete_colection():
    delete_count = database.delete({}, "indicators")
    print(f" > {delete_count} items deleted")


def _insert_data(indicators):
    n_inserted = database.insert_many(indicators, "indicators")
    print(f" > {n_inserted} items inserted")


if __name__ == "__main__":

    # Run
    import dotenv
    dotenv.load_dotenv()
    run()
