#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# System libraries
import datetime as dt
import pandas as pd


def update_wallet(wallet, stock_price, index):

    # Inititate wallet
    remaining_cash = wallet["remainingCash"]
    if "IBOV" not in wallet["wallet"]:
        n_stocks = int(remaining_cash / stock_price)
        wallet["remainingCash"] = remaining_cash - n_stocks * stock_price
        wallet["wallet"]["IBOV"] = {
            "initial_date": index,
            "n_stocks": n_stocks,
            "initial_price": stock_price,
            "current_date": index,
            "current_price": stock_price}

    # Update wallet
    else:
        wallet["wallet"]["IBOV"]["current_date"] = index
        wallet["wallet"]["IBOV"]["current_price"] = stock_price


def compute_record(wallet):
    record = {}
    item = wallet["wallet"]["IBOV"]
    record["patrimony"] = wallet["remainingCash"] + item["n_stocks"] * item["current_price"]
    record["n_trades_with_gain"] = 0
    record["n_trades_with_loss"] = 0
    record["gain_profit"] = 0
    record["loss_profit"] = 0
    record["avg_gain_profit_percentage"] = 0
    record["avg_loss_profit_percentage"] = 0
    return record
