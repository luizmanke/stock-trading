#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# System libraries
import datetime as dt
import pandas as pd

# Own libraries
from .utils import get_today_date
from ..common import baseline, database
from ..analytics.wallet import Wallet


def run():
    print("Wallets...")
    _update_baseline()
    _update_strategy()


def _update_baseline():
    print(" - baseline")
    USER_ID = 0
    index = get_today_date()
    wallet = _get_wallet(USER_ID)
    stock_price = _get_baseline_price()
    baseline.update_wallet(wallet, stock_price, index)
    record = baseline.compute_record(wallet)
    _save_wallet(USER_ID, wallet)
    _save_record(USER_ID, record)


def _get_baseline_price():
    filter_ = {"ticker": "IBOV"}
    fields = {"ticker": 1, "close": 1}
    sort = [("occurredAt", -1)]
    docs = database.find(
        collection="quotations", filter=filter_, projection=fields, sort=sort, limit=1)
    return docs[0]["close"]


def _update_strategy():
    print(" - strategy")
    USER_ID = 1
    wallet = _get_wallet(USER_ID)
    quotations = _get_quotations()
    indicators = _get_indicators()
    new_wallet, new_record = _compute_strategy(wallet, indicators, quotations)
    _save_wallet(USER_ID, new_wallet)
    _save_record(USER_ID, new_record)


def _get_quotations():
    pipeline = [{"$sort": {"occurredAt": 1}},
                {"$group": {
                    "_id": "$ticker",
                    "ticker": {"$last": "$ticker"},
                    "close": {"$last": "$close"}}}]
    docs = database.aggregate(pipeline, "quotations")
    docs = pd.DataFrame(docs).set_index("ticker")
    docs = docs[["close"]].to_dict(orient="index")
    return docs


def _get_indicators():
    fields = {"ticker": 1, "rank": 1, "trend": 1}
    docs = database.find(collection="indicators", projection=fields)
    return docs


def _compute_strategy(wallet, indicators, data):
    index = get_today_date()
    manager = Wallet(wallet["remainingCash"])
    for key, value in wallet["wallet"].items():
        manager.wallet_[key] = value
    manager.compute_deals(data, indicators, index)
    manager.update_wallet(data, index)
    wallet = {
        "remainingCash": manager.wallet_.pop("remaining_cash"), "wallet": manager.wallet_}
    record = manager.records_.to_dict(orient="records")[0]
    return wallet, record


def _get_wallet(user_id):
    fields = {"_id": 0, "createdAt": 0}
    filter_ = {"userId": user_id}
    docs = database.find(collection="wallets", filter=filter_, projection=fields)
    return docs[0]


def _save_wallet(user_id, wallet):
    wallet = wallet.copy()

    wallet["userId"] = user_id
    wallet["occurredAt"] = get_today_date()
    wallet["createdAt"] = dt.datetime.utcnow()

    n_deleted = database.delete({"userId": {"$eq": user_id}}, "wallets")
    print(f"  > {n_deleted} wallet deleted")
    n_inserted = database.insert_many([wallet], "wallets")
    print(f"  > {n_inserted} wallet inserted")


def _save_record(user_id, record):

    record["userId"] = user_id
    record["occurredAt"] = get_today_date()
    record["createdAt"] = dt.datetime.utcnow()

    filter = {"userId": {"$eq": user_id}, "occurredAt": {"$eq": get_today_date()}}
    n_deleted = database.delete(filter, "records")
    print(f"  > {n_deleted} record deleted")
    n_inserted = database.insert_many([record], "records")
    print(f"  > {n_inserted} record inserted")
