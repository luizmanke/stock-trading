#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# System libraries
import pandas as pd

# Own libraries
from ..baseline import update_wallet, compute_record


def test_update_wallet():
    KEYS = {
        "n_stocks": int,
        "initial_price": float,
        "current_price": float,
        "initial_date": str,
        "current_date": str
    }

    # Initiate wallet
    wallet = {"remainingCash": 100000, "wallet": {}}
    update_wallet(wallet, 1.5, "2019")
    assert type(wallet["remainingCash"]) == float
    assert type(wallet["wallet"]) == dict
    for key, type_ in KEYS.items():
        assert type(wallet["wallet"]["IBOV"][key]) == type_

    # Update wallet
    update_wallet(wallet, 1.0, "2020")
    assert type(wallet["remainingCash"]) == float
    assert type(wallet["wallet"]) == dict
    for key, type_ in KEYS.items():
        assert type(wallet["wallet"]["IBOV"][key]) == type_


def test_compute_records():
    KEYS = {
        "patrimony": float,
        "n_trades_with_gain": int,
        "n_trades_with_loss": int,
        "gain_profit": int,
        "loss_profit": int,
        "avg_gain_profit_percentage": int,
        "avg_loss_profit_percentage": int
    }

    wallet = {
        "remainingCash": 100000.0,
        "wallet": {
            "IBOV": {
                "n_stocks": 200,
                "current_price": 5
            }
        }
    }
    record = compute_record(wallet)
    for key, type_ in KEYS.items():
        assert type(record[key]) == type_
