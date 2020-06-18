#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Own libraries
from .. import request_fundamentals


def test_run():
    KEYS = {
        "priceToEarnings": float,
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
        "ticker": str
    }
    fundamentals = request_fundamentals.run()
    fundamental = fundamentals[0]
    for key, type_ in KEYS.items():
        assert type(fundamental[key]) == type_
    assert len(KEYS) == len(fundamental)
