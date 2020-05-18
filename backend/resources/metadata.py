#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# System libraries
import datetime as dt

# Own libraries
from ..common.database import Database
from ..common.request import Request


def update_database():
    print("## UPDATE DATABASE ##")
    try:
        UTC = -3
        occurred_at = dt.datetime.utcnow() - dt.timedelta(hours=UTC)
        occurred_at = occurred_at.replace(hour=0, minute=0, second=0, microsecond=0)

        request = Request()
        database = Database()

        # Fundamentals
        print("Fundamentals...")
        fundamentals = request.fundamentals()
        for item in fundamentals:
            item["occurredAt"] = occurred_at
        print(f" > {len(fundamentals)} items found")
        database.insert(fundamentals, "fundamentals")

        # Quotations
        print("Quotations...")
        initial_date = occurred_at - dt.timedelta(days=2)
        initial_date = initial_date.strftime(("%d/%m/%Y"))
        quotations = request.quotations(initial_date)
        print(f" > {len(quotations)} items found")
        database.insert(quotations, "quotations")

    except Exception as error:
        print(error)
