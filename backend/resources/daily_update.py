#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# System libraries
import datetime as dt
import sys
import traceback

# Own libraries
from .utils import get_today_date
from ..common import database
from ..common import request_fundamentals
from ..common import request_quotations
from ..analytics.strategy import Strategy


# TODO: Create status API
def run():
    print("## DAILY UPDATE ##")
    try:
        _update_fundamentals()
        _update_quotations()
        _update_indicators()
    except Exception:
        traceback.print_exc(file=sys.stdout)


def _update_fundamentals():
    print("Fundamentals...")

    fundamentals = request_fundamentals.run()
    for item in fundamentals:
        item["occurredAt"] = get_today_date()
    print(f" > {len(fundamentals)} items found")

    n_deleted = database.delete(fundamentals, "fundamentals")
    print(f" > {n_deleted} items deleted")

    n_inserted = database.insert(fundamentals, "fundamentals")
    print(f" > {n_inserted} items inserted")


def _update_quotations():
    print("Quotations...")

    initial_date = get_today_date() - dt.timedelta(days=2)
    initial_date = initial_date.strftime(("%d/%m/%Y"))
    quotations = request_quotations.run(initial_date)
    print(f" > {len(quotations)} items found")

    n_deleted = database.delete(quotations, "quotations")
    print(f" > {n_deleted} items deleted")

    n_inserted = database.insert(quotations, "quotations")
    print(f" > {n_inserted} items inserted")


def _update_indicators():
    print("Indicators...")

    fundamentals = _get_last_fundamentals()
    quotations = _get_last_quotations()
    indicators = Strategy().get_indicators(fundamentals, quotations)
    for item in indicators:
        item["occurredAt"] = get_today_date()
    print(f" > {len(indicators)} new items")

    n_deleted = database.delete(indicators, "indicators")
    print(f" > {n_deleted} items deleted")

    n_inserted = database.insert(indicators, "indicators")
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
    minimum_date = get_today_date() - dt.timedelta(days=120)
    filter = {"occurredAt": {"$gte": minimum_date}}
    fields = {"ticker": 1, "close": 1, "volume": 1}
    return database.find(collection="quotations", filter=filter, projection=fields)
