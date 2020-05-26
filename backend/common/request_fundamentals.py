#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# System libraries
import datetime as dt
import pandas as pd
import requests


def run():
    raw_fundamentals = _get_fundamentals()
    fundamentals = _preprocess(raw_fundamentals)
    return fundamentals


def _get_fundamentals():
    TICKERS_URL = "http://fundamentus.com.br/resultado.php"
    response = requests.post(url=TICKERS_URL)
    fundamentals = pd.read_html(response.text)[0]
    return fundamentals


def _preprocess(table):

    # Rename
    new_table = table.rename(columns={
        "Papel": "ticker", "Cotação": "price", "P/L": "priceToEarnings",
        "P/VP": "priceToBookValue", "PSR": "priceToSalesRatio",
        "Div.Yield": "dividendYield", "P/Ativo": "priceToAsset",
        "P/Cap.Giro": "priceToWorkingCapital", "P/EBIT": "priceToEbit",
        "P/Ativ Circ.Liq": "priceToNetCurrentAsset", "EV/EBIT": "enterpriseValueToEbit",
        "EV/EBITDA": "enterpriseValueToEbitda", "Mrg Ebit": "ebitMargin",
        "Mrg. Líq.": "netMargin", "Liq. Corr.": "currentLiquidity",
        "ROIC": "returnOnInvestedCapital", "ROE": "returnOnEquity",
        "Liq.2meses": "volume", "Patrim. Líq": "netEquity",
        "Dív.Brut/ Patrim.": "grossDebtToEquity", "Cresc. Rec.5a": "cagr"})

    # To float
    new_table = new_table.replace("%", "", regex=True)
    new_table = new_table.replace("\\.", "", regex=True)
    new_table = new_table.replace(",", ".", regex=True)
    tickers = new_table.pop("ticker")
    new_table = new_table.astype(float)
    new_table["ticker"] = tickers

    # Rescale
    COLUMNS = ["price", "priceToEarnings", "priceToBookValue", "priceToWorkingCapital",
               "priceToEbit", "priceToNetCurrentAsset", "enterpriseValueToEbit",
               "enterpriseValueToEbitda", "currentLiquidity", "volume", "netEquity",
               "grossDebtToEquity"]
    for column in COLUMNS:
        new_table[column] = new_table[column] / 100
    for column in ["priceToSalesRatio", "priceToAsset"]:
        new_table[column] = new_table[column] / 1000

    new_table = new_table.drop(["price", "volume"], axis=1)
    new_table = new_table.to_dict(orient="records")
    return new_table
