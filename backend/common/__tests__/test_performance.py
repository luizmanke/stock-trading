#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# System libraries
import pandas as pd

# Own libraries
from ..performance import compute_performance


def test_compute_performance():
    records = [
        {
            "patrimony": 100000.0,
            "n_trades_with_gain": 0,
            "n_trades_with_loss": 0,
            "gain_profit": 0,
            "loss_profit": 0,
            "avg_gain_profit_percentage": 0,
            "avg_loss_profit_percentage": 0,
            "occurredAt": pd.to_datetime("2020-05-01 00:00:00")
        },
        {
            "patrimony": 101000.0,
            "n_trades_with_gain": 2,
            "n_trades_with_loss": 1,
            "gain_profit": 600,
            "loss_profit": 50,
            "avg_gain_profit_percentage": 0.1,
            "avg_loss_profit_percentage": 0.05,
            "occurredAt": pd.to_datetime("2020-06-01 00:00:00")
        }
    ]
    records = pd.DataFrame(records).set_index("occurredAt")
    performance = compute_performance(records)

    KEYS = {
        'profit': float,
        'profit_in_percentage': float,
        'annual_profit_in_percentage': float,
        'sharpe_ratio': float,
        'maximum_drawdown_in_percentage': float,
        'total_trades': int,
        'percentage_of_gain_trades': float,
        'percentage_of_loss_trades': float,
        'avg_gain_per_trade': float,
        'avg_loss_per_trade': float,
        'avg_gain_in_percentage': float,
        'avg_loss_in_percentage': float,
        'payoff': float,
        'profit_factor': float,
        'recuperation_factor': float
    }
    for key, type_ in KEYS.items():
        assert type(performance[key]) == type_
