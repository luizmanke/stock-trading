#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# System libraries
import datetime as dt
import pandas as pd
import requests


def run():
    raw_fundamentals = _request_fundamentals()
    fundamentals = _preprocess(raw_fundamentals)
    return fundamentals


def _request_fundamentals():
    TICKERS_URL = "http://fundamentus.com.br/resultado.php"
    HEADERS = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url=TICKERS_URL, headers=HEADERS)
    fundamentals = pd.read_html(response.text)[0]
    return fundamentals


def _preprocess(table):
    table = _rename_columns(table)
    table = _convert_to_float(table)
    table = _rescale(table)
    return _to_list(table)


def _rename_columns(table):
    table = table.rename(columns={
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
    return table


def _convert_to_float(table):
    table = table.replace("%", "", regex=True)
    table = table.replace("\\.", "", regex=True)
    table = table.replace(",", ".", regex=True)
    tickers = table.pop("ticker")
    table = table.astype(float)
    table["ticker"] = tickers
    return table


def _rescale(table):
    COLUMNS = ["price", "priceToEarnings", "priceToBookValue", "priceToWorkingCapital",
               "priceToEbit", "priceToNetCurrentAsset", "enterpriseValueToEbit",
               "enterpriseValueToEbitda", "currentLiquidity", "volume", "netEquity",
               "grossDebtToEquity"]
    for column in COLUMNS:
        table[column] = table[column] / 100
    for column in ["priceToSalesRatio", "priceToAsset"]:
        table[column] = table[column] / 1000
    return table


def _to_list(table):
    table = table.drop(["price", "volume"], axis=1)
    dictionary = table.to_dict(orient="records")
    return dictionary
