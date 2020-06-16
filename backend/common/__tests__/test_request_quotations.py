#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# System libraries
import pandas as pd

# Own libraries
from .. import request_quotations


def test_run():
    KEYS = {
        "close": float,
        "open": float,
        "high": float,
        "low": float,
        "volume": float,
        "ticker": str,
        "occurredAt": pd._libs.tslibs.timestamps.Timestamp
    }
    quotations = request_quotations.run()
    quotation = quotations[0]
    for key, type_ in KEYS.items():
        assert type(quotation[key]) == type_
    assert len(KEYS) == len(quotation)
