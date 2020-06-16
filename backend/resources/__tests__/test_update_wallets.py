#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# System libraries
import datetime as dt
from dotenv import load_dotenv

# Own libraries
from ...common import database
from .. import update_wallets

# Configurations
load_dotenv()


def test_update_indicators():
    initial_time = dt.datetime.utcnow()
    update_wallets.run()
    final_time = dt.datetime.utcnow()

    filter_ = {"createdAt": {"$gte": initial_time, "$lte": final_time}}
    fields = {"_id": 0}
    wallets = database.find("wallets", filter=filter_, projection=fields)
    KEYS = {"remainingCash": float,
            "wallet": dict,
            "occurredAt": dt.datetime,
            "createdAt": dt.datetime,
            "userId": int}
    unique_user_ids = len(set([item["userId"] for item in wallets]))
    one_wallet = wallets[0]
    assert unique_user_ids == len(wallets)
    for key, type_ in KEYS.items():
        assert type(one_wallet[key]) == type_
