#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# System libraries
import pandas as pd
import pytest

# Own libraries
from ..wallet import Wallet


@pytest.fixture
def wallet():
    return Wallet(remaining_cash=100000)


def test_compute_deals(wallet):
    data = {"A": {"close": 10.0}, "B": {"close": 20.0}}
    indicators = [{"ticker": "IBOV", "rank": float("nan"), "trend": 1},
                  {"ticker": "A", "rank": 1, "trend": 1},
                  {"ticker": "B", "rank": 1, "trend": 1}]
    index = "2020-01-01"
    wallet.compute_deals(data, indicators, index)
    deals = wallet.deals_

    KEYS = {
        "ticker": str,
        "operation": str,
        "n_stocks": int,
        "price": float
    }
    deal = deals[0]
    for key, type_ in KEYS.items():
        assert type(deal[key]) == type_


def test_update_records(wallet):
    wallet_ = {"remaining_cash": 10000,
               "A": {"initial_price": 10,
                     "current_price": 20,
                     "n_stocks": 100}}
    trades = [{"profit": 1000, "percentage": 0.1},
              {"profit": 2000, "percentage": 0.2}]
    index = "2020-01-01"
    wallet.update_records(wallet_, trades, index)

    KEYS = {
        "patrimony": float,
        "n_trades_with_gain": float,
        "n_trades_with_loss": float,
        "gain_profit": float,
        "loss_profit": float,
        "avg_gain_profit_percentage": float,
        "avg_loss_profit_percentage": float
    }
    records = wallet.records_
    assert type(records) == pd.DataFrame
    assert records.shape[0] == 1
    for key, type_ in KEYS.items():
        assert records[key].iloc[0].dtype == type_


def test_update_wallet(wallet):
    data = {"A": {"close": 10.0}, "B": {"close": 20.0}}
    index = "2020-01-01"
    wallet.wallet_.update(
        {"A": {"n_stocks": 100, "current_price": 1, "initial_price": 2}})
    wallet.deals_ = [
        {"ticker": "A", "operation": "sell"},
        {"ticker": "B", "operation": "buy", "n_stocks": 200, "price": 10}]
    wallet.update_wallet(data, index)

    KEYS = ["initial_date", "n_stocks", "initial_price", "current_price", "current_date"]
    new_wallet = wallet.wallet_
    assert new_wallet["remaining_cash"] == 98100
    for key in KEYS:
        assert key in new_wallet["B"]
