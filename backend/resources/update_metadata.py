#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# System libraries
import datetime as dt

# Own libraries
from .utils import get_today_date
from ..common import database
from ..common import request_fundamentals
from ..common import request_quotations


def run():
    _update_fundamentals()
    _update_quotations()


def _update_fundamentals():
    print("Fundamentals...")

    fundamentals = request_fundamentals.run()
    for item in fundamentals:
        item["occurredAt"] = get_today_date()
    print(f" > {len(fundamentals)} items found")

    n_deleted = database.delete_many(fundamentals, "fundamentals")
    print(f" > {n_deleted} items deleted")

    n_inserted = database.insert_many(fundamentals, "fundamentals")
    print(f" > {n_inserted} items inserted")


def _update_quotations():
    print("Quotations...")

    initial_date = get_today_date() - dt.timedelta(days=2)
    initial_date = initial_date.strftime(("%d/%m/%Y"))
    quotations = request_quotations.run(initial_date)
    print(f" > {len(quotations)} items found")

    n_deleted = database.delete_many(quotations, "quotations")
    print(f" > {n_deleted} items deleted")

    n_inserted = database.insert_many(quotations, "quotations")
    print(f" > {n_inserted} items inserted")
