#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# System libraries
import datetime as dt
import json
import os
import pytest
import requests
from dotenv import load_dotenv

# Own libraries
from ..get_performances import GetPerformances

# Configurations
load_dotenv()


def test_get_performances():
    docs = GetPerformances().get()

    # Baseline
    KEYS = {"profit_in_percentage": float,
            "sharpe_ratio": float,
            "maximum_drawdown_in_percentage": float}
    baseline = docs["IBOV"]
    _ = dt.datetime.strptime(baseline.pop("initial_date"), "%Y-%m-%d 00:00:00")
    _ = dt.datetime.strptime(baseline.pop("current_date"), "%Y-%m-%d 00:00:00")
    for _, performance in baseline.items():
        for key, type_ in KEYS.items():
            assert type(performance[key]) == type_

    # Strategy
    KEYS = {"profit_in_percentage": [int, float],
            "sharpe_ratio": [int, float],
            "maximum_drawdown_in_percentage": [int, float],
            "total_trades": [int, float],
            "percentage_of_gain_trades": [int, float],
            "percentage_of_loss_trades": [int, float],
            "avg_gain_per_trade": [int, float],
            "avg_loss_per_trade": [int, float],
            "avg_gain_in_percentage": [int, float],
            "avg_loss_in_percentage": [int, float]}
    strategy = docs["strategy"]
    _ = dt.datetime.strptime(strategy.pop("initial_date"), "%Y-%m-%d 00:00:00")
    _ = dt.datetime.strptime(strategy.pop("current_date"), "%Y-%m-%d 00:00:00")
    for _, performance in strategy.items():
        for key, types in KEYS.items():
            assert type(performance[key]) in types


@pytest.mark.integration
def test_get_performances_endpoint():
    app = os.environ.get("HEROKU_APP")
    url = f"http://{app}.herokuapp.com/get-performances"
    response = requests.get(url)
    docs = json.loads(response.text)

    # Baseline
    KEYS = {"profit_in_percentage": float,
            "sharpe_ratio": float,
            "maximum_drawdown_in_percentage": float}
    baseline = docs["IBOV"]
    _ = dt.datetime.strptime(baseline.pop("initial_date"), "%Y-%m-%d 00:00:00")
    _ = dt.datetime.strptime(baseline.pop("current_date"), "%Y-%m-%d 00:00:00")
    for _, performance in baseline.items():
        for key, type_ in KEYS.items():
            assert type(performance[key]) == type_

    # Strategy
    KEYS = {"profit_in_percentage": [int, float],
            "sharpe_ratio": [int, float],
            "maximum_drawdown_in_percentage": [int, float],
            "total_trades": [int, float],
            "percentage_of_gain_trades": [int, float],
            "percentage_of_loss_trades": [int, float],
            "avg_gain_per_trade": [int, float],
            "avg_loss_per_trade": [int, float],
            "avg_gain_in_percentage": [int, float],
            "avg_loss_in_percentage": [int, float]}
    strategy = docs["strategy"]
    _ = dt.datetime.strptime(strategy.pop("initial_date"), "%Y-%m-%d 00:00:00")
    _ = dt.datetime.strptime(strategy.pop("current_date"), "%Y-%m-%d 00:00:00")
    for _, performance in strategy.items():
        for key, types in KEYS.items():
            assert type(performance[key]) in types
