#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# System libraries
import numpy as np

# Own libraries
from ..strategy import Strategy

# Configurations
np.random.seed(1)


def test_get_indicators():
    fundamentals = _create_fundamentals()
    quotations = _create_quotations()
    indicators = Strategy().get_indicators(fundamentals, quotations)

    KEYS = {"ticker": str, "rank": int, "trend": float}
    indicator = indicators[0]
    for key, type_ in KEYS.items():
        assert type(indicator[key]) == type_
    assert len(indicators) == 3


def _create_fundamentals():
    fundamentals = [
        {"ticker": "A", "returnOnInvestedCapital": 10, "priceToEarnings": 10, "cagr": 10},
        {"ticker": "B", "returnOnInvestedCapital": 30, "priceToEarnings": 5, "cagr": 10}
    ]
    return fundamentals


def _create_quotations():
    N_SAMPLES = 300
    market_quotations = [{"ticker": "IBOV", "volume": volume, "close": close}
                         for volume in np.random.uniform(500000, size=N_SAMPLES)
                         for close in np.linspace(0, 100, num=N_SAMPLES)]
    quotations_1 = [{"ticker": "A", "volume": volume, "close": close}
                    for volume in np.random.uniform(500000, size=N_SAMPLES)
                    for close in np.linspace(0, 100, num=N_SAMPLES)]
    quotations_2 = [{"ticker": "B", "volume": volume, "close": close}
                    for volume in np.random.uniform(500000, size=N_SAMPLES)
                    for close in np.linspace(0, 100, num=N_SAMPLES)]
    quotations = market_quotations + quotations_1 + quotations_2
    return quotations
