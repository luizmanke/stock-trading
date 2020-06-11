#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# System libraries
import datetime as dt

# Own libraries
from .utils import get_today_date
from ..common import database
from ..analytics.strategy import Strategy


def run():
    print("Indicators...")

    fundamentals = _get_last_fundamentals()
    quotations = _get_last_quotations()
    indicators = Strategy().get_indicators(fundamentals, quotations)
    for item in indicators:
        item["occurredAt"] = get_today_date()
    print(f" > {len(indicators)} new items")

    n_deleted = database.delete({}, "indicators")
    print(f" > {n_deleted} items deleted")

    n_inserted = database.insert_many(indicators, "indicators")
    print(f" > {n_inserted} items inserted")


def _get_last_fundamentals():
    pipeline = [{"$sort": {"occurredAt": 1}},
                {"$group": {
                    "_id": "$ticker",
                    "ticker": {"$last": "$ticker"},
                    "cagr": {"$last": "$cagr"},
                    "returnOnInvestedCapital": {"$last": "$returnOnInvestedCapital"},
                    "priceToEarnings": {"$last": "$priceToEarnings"}}}]
    return database.aggregate(pipeline, "fundamentals")


def _get_last_quotations():
    minimum_date = get_today_date() - dt.timedelta(days=150)
    filter = {"occurredAt": {"$gte": minimum_date}}
    fields = {"ticker": 1, "close": 1, "volume": 1}
    sort = [("occurredAt", 1)]
    return database.find(collection="quotations", filter=filter, projection=fields, sort=sort)
