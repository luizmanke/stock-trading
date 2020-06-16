#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# System libraries
import datetime as dt
from dotenv import load_dotenv

# Own libraries
from ...common import database
from .. import update_metadata

# Configurations
load_dotenv()


def test_update_metadata():
    initial_time = dt.datetime.utcnow()
    update_metadata.run()
    final_time = dt.datetime.utcnow()

    filter_ = {"createdAt": {"$gte": initial_time, "$lte": final_time}}
    fields = {"_id": 0}
    fundamentals = database.find("fundamentals", filter=filter_, projection=fields)
    KEYS = {"priceToEarnings": float,
            "priceToBookValue": float,
            "priceToSalesRatio": float,
            "dividendYield": float,
            "priceToAsset": float,
            "priceToWorkingCapital": float,
            "priceToEbit": float,
            "priceToNetCurrentAsset": float,
            "enterpriseValueToEbit": float,
            "enterpriseValueToEbitda": float,
            "ebitMargin": float,
            "netMargin": float,
            "currentLiquidity": float,
            "returnOnInvestedCapital": float,
            "returnOnEquity": float,
            "netEquity": float,
            "grossDebtToEquity": float,
            "cagr": float,
            "ticker": str,
            "occurredAt": dt.datetime,
            "createdAt": dt.datetime}
    one_fundamental = fundamentals[0]
    assert len(fundamentals) > 10
    for key, type_ in KEYS.items():
        assert type(one_fundamental[key]) == type_

    filter_ = {"createdAt": {"$gte": initial_time, "$lte": final_time}}
    fields = {"_id": 0}
    quotations = database.find("quotations", filter=filter_, projection=fields)
    KEYS = {"close": float,
            "open": float,
            "high": float,
            "low": float,
            "volume": float,
            "ticker": str,
            "occurredAt": dt.datetime,
            "createdAt": dt.datetime}
    one_quotation = quotations[0]
    assert len(quotations) > 10
    for key, type_ in KEYS.items():
        assert type(one_quotation[key]) == type_
