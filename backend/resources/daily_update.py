#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# System libraries
import datetime as dt
import sys
import traceback

# Own libraries
from ..common import database
from ..common import request_fundamentals
from ..common import request_quotations
# from ..analytics.strategy import Strategy


def run():
    print("## DAILY UPDATE ##")
    try:
        _update_fundamentals()
        _update_quotations()
        # _update_indicators()
    except Exception:
        traceback.print_exc(file=sys.stdout)


def _update_fundamentals():
    print("Fundamentals...")
    fundamentals = request_fundamentals.run()
    for item in fundamentals:
        item["occurredAt"] = _get_today_date()
    print(f" > {len(fundamentals)} items found")
    n_deleted = database.delete(fundamentals, "fundamentals")
    print(f" > {n_deleted} items deleted")
    n_inserted = database.insert(fundamentals, "fundamentals")
    print(f" > {n_inserted} items inserted")


def _update_quotations():
    print("Quotations...")
    initial_date = _get_today_date() - dt.timedelta(days=2)
    initial_date = initial_date.strftime(("%d/%m/%Y"))
    quotations = request_quotations.run(initial_date)
    print(f" > {len(quotations)} items found")
    n_deleted = database.delete(quotations, "quotations")
    print(f" > {n_deleted} items deleted")
    n_inserted = database.insert(quotations, "quotations")
    print(f" > {n_inserted} items inserted")


# TODO: Limit fundamentals
# def _update_indicators():
#     print("Indicators...")

#     pipeline = [{"$sort": {"occurredAt": 1}},
#                 {"$group": {
#                     "_id": "$ticker",
#                     "ticker": {"$last": "$ticker"},
#                     "cagr": {"$last": "$cagr"},
#                     "returnOnInvestedCapital": {"$last": "$returnOnInvestedCapital"},
#                     "priceToEarnings": {"$last": "$priceToEarnings"}}}]
#     fundamentals = database.aggregate(pipeline, "fundamentals")

#     minimum_date = occurred_at - dt.timedelta(days=200)
#     filter_ = {"occurredAt": {"$gte": minimum_date}}
#     fields = {"ticker": 1, "close": 1, "volume": 1}
#     quotations = database.find(filter_, fields, "quotations")

#     indicators = strategy.get_indicators(fundamentals, quotations)
#     print(f" > {len(indicators)} new items")
#     database.insert(indicators, "indicators")


def _get_today_date():
    UTC = -3
    today_date = dt.datetime.utcnow() + dt.timedelta(hours=UTC)
    today_date = today_date.replace(hour=0, minute=0, second=0, microsecond=0)
    return today_date
