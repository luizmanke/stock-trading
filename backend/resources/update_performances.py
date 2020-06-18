#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# System libraries
import datetime as dt
import pandas as pd
import warnings

# Own libraries
from .utils import get_today_date
from ..common import database
from ..common.performance import compute_performance

# Configurations
warnings.filterwarnings("ignore")


def run():
    print("Performance...")

    print(f" - baseline")
    _update_performance(user_id=0)

    print(f" - strategy")
    _update_performance(user_id=1)


def _update_performance(user_id):
    records = _get_records(user_id)
    records["year"] = records.index.year
    records["month"] = records.index.month
    aux_records = records.reset_index(drop=False)

    performance = {"initial_date": records.index[0], "current_date": records.index[-1]}
    performance["overall"] = compute_performance(records)
    for year in sorted(set(records["year"]), reverse=True):
        for month in sorted(set(records["month"]), reverse=True):
            period_records = records[(records["year"] == year) & (records["month"] == month)]

            first_date = period_records.index[0]
            first_index = aux_records[aux_records["occurredAt"] == first_date].index[0]
            if first_index:
                past_record = records.iloc[first_index - 1:first_index]
                period_records = pd.concat([past_record, period_records])

            performance[f"{year}-{month:02d}"] = compute_performance(period_records)

    _save_performance(user_id, performance)


def _get_records(user_id):
    fields = {"_id": 0, "createdAt": 0}
    filter_ = {"userId": user_id}
    sort = [("occurredAt", 1)]
    docs = database.find(collection="records", filter=filter_, projection=fields, sort=sort)
    return pd.DataFrame(docs).set_index("occurredAt")


def _save_performance(user_id, performance):
    performance["userId"] = user_id
    performance["occurredAt"] = get_today_date()
    performance["createdAt"] = dt.datetime.utcnow()

    n_deleted = database.delete({"userId": {"$eq": user_id}}, "performances")
    print(f"  > {n_deleted} item deleted")
    n_inserted = database.insert_many([performance], "performances")
    print(f"  > {n_inserted} item inserted")
