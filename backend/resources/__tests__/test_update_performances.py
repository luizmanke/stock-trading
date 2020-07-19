#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# System libraries
import datetime as dt
from dotenv import load_dotenv

# Own libraries
from ...common import database
from .. import update_performances

# Configurations
load_dotenv()


def test_update_performances():
    initial_time = dt.datetime.utcnow()
    update_performances.run()
    final_time = dt.datetime.utcnow()

    filter_ = {"createdAt": {"$gte": initial_time, "$lte": final_time}}
    fields = {"_id": 0}
    performances = database.find("performances", filter=filter_, projection=fields)
    KEYS = {"annual_profit_in_percentage": float,
            "avg_gain_in_percentage": float,
            "avg_gain_per_trade": float,
            "avg_loss_in_percentage": float,
            "avg_loss_per_trade": float,
            "maximum_drawdown_in_percentage": float,
            "payoff": float,
            "percentage_of_gain_trades": float,
            "percentage_of_loss_trades": float,
            "profit": float,
            "profit_in_percentage": float,
            "recuperation_factor": float,
            "sharpe_ratio": float,
            "profit_factor": float}
    unique_user_ids = len(set([item["userId"] for item in performances]))
    one_performance = performances[0]
    one_performance.pop("userId")
    assert unique_user_ids == len(performances)
    assert type(one_performance.pop("occurredAt")) == dt.datetime
    assert type(one_performance.pop("createdAt")) == dt.datetime
    assert type(one_performance.pop("initial_date")) == dt.datetime
    assert type(one_performance.pop("current_date")) == dt.datetime
    for _, month in one_performance.items():
        for key, type_ in KEYS.items():
            assert type(month[key]) == type_
