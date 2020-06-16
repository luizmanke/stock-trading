#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# System libraries
import datetime as dt
from dotenv import load_dotenv

# Own libraries
from ...common import database
from .. import update_indicators

# Configurations
load_dotenv()


def test_update_indicators():
    initial_time = dt.datetime.utcnow()
    update_indicators.run()
    final_time = dt.datetime.utcnow()

    filter_ = {"createdAt": {"$gte": initial_time, "$lte": final_time}}
    fields = {"_id": 0}
    indicators = database.find("indicators", filter=filter_, projection=fields)
    KEYS = {"ticker": str,
            "rank": int,
            "trend": float,
            "occurredAt": dt.datetime,
            "createdAt": dt.datetime}
    one_indicator = indicators[0]
    assert len(indicators) > 10
    for key, type_ in KEYS.items():
        assert type(one_indicator[key]) == type_
