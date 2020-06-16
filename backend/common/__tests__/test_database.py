#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# System libraries
import datetime as dt
import pandas as pd
from dotenv import load_dotenv

# Own libraries
from .. import database

# Configurations
load_dotenv()


def test_find():
    filter_ = {"ticker": "IBOV"}
    fields = {"_id": 0, "ticker": 1, "occurredAt": 1}
    sort = [("occurredAt", 1)]
    limit = 10
    docs = database.find(
        "quotations", filter=filter_, projection=fields, sort=sort, limit=limit)

    dataframe = pd.DataFrame(docs)
    assert type(docs) == list
    assert ["IBOV"] == list(set(dataframe["ticker"]))
    assert (["ticker", "occurredAt"] == dataframe.columns).all()
    assert (dataframe.index == sorted(dataframe.index)).all()
    assert len(docs) == limit


def test_aggregate():
    pipeline = [{"$match": {"ticker": "IBOV"}},
                {"$sort": {"occurredAt": 1}},
                {"$group": {
                    "_id": "$ticker",
                    "ticker": {"$last": "$ticker"},
                    "occurredAt": {"$last": "$occurredAt"}}}]
    docs = database.aggregate(pipeline, "quotations")

    dataframe = pd.DataFrame(docs)
    assert type(docs) == list
    assert ["IBOV"] == list(set(dataframe["ticker"]))
    assert (["_id", "ticker", "occurredAt"] == dataframe.columns).all()
    assert len(docs) == 1


def test_insert_many_and_delete_many():
    created_at = dt.datetime.utcnow()
    items = [
        {"ticker": "A", "occurredAt": created_at},
        {"ticker": "B", "occurredAt": created_at},
        {"ticker": "C", "occurredAt": created_at}
    ]
    n_inserted_items = database.insert_many(items, "tests")
    n_deleted_items = database.delete_many(items, "tests")
    assert len(items) == n_inserted_items
    assert n_inserted_items == n_deleted_items


def test_delete_many():
    created_at = dt.datetime.utcnow()
    items = [
        {"ticker": "A", "occurredAt": created_at},
        {"ticker": "B", "occurredAt": created_at},
        {"ticker": "C", "occurredAt": created_at}
    ]
    n_inserted_items = database.insert_many(items, "tests")
    n_deleted_items = database.delete({"occurredAt": created_at}, "tests")
    assert len(items) == n_inserted_items
    assert n_inserted_items == n_deleted_items
