#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# System libraries
import pandas as pd

# Configurations
DESCENDING_KEY = "returnOnInvestedCapital"
ASCENDING_KEY = "priceToEarnings"


# TODO: Improve market trend
# TODO: Use companies trends
class Strategy():

    def __init__(self):
        super(Strategy, self).__init__()

    def get_indicators(self, fundamentals, quotations):
        fundamentals, quotations = self._preprocess(fundamentals, quotations)
        volumes = self._get_volumes(quotations)
        fundamentals = self._update_fundamentals(fundamentals, volumes)
        fundamentals = self._filter(fundamentals)
        rates = self._get_rates(fundamentals)
        market_indicator = self._get_market_indicator(quotations)
        indicators = self._to_list(rates, market_indicator)
        return indicators

    @staticmethod
    def _preprocess(fundamentals, quotations):
        fundamentals = pd.DataFrame(fundamentals)
        fundamentals = fundamentals.set_index("ticker")
        quotations = pd.DataFrame(quotations)
        return fundamentals, quotations

    @staticmethod
    def _get_volumes(quotations):
        volumes = quotations.groupby("ticker")["volume"].rolling(window=40).mean()
        return volumes

    @staticmethod
    def _update_fundamentals(fundamentals, volumes):
        for ticker in set(fundamentals.index):
            volume = 0
            if ticker in volumes:
                volume = volumes[ticker].iloc[-1]
            fundamentals.loc[ticker, "volume"] = volume
        return fundamentals

    @staticmethod
    def _filter(fundamentals):
        fundamentals = fundamentals[fundamentals["volume"] > 100000]
        fundamentals = fundamentals[fundamentals["cagr"] > 0.05]
        fundamentals = fundamentals[fundamentals[DESCENDING_KEY] > 0]
        fundamentals = fundamentals[fundamentals[ASCENDING_KEY] > 0]
        return fundamentals

    @staticmethod
    def _get_rates(fundamentals):
        new_descending_key = f"{DESCENDING_KEY}_rate"
        new_ascending_key = f"{ASCENDING_KEY}_rate"
        rates_list = range(fundamentals.shape[0])

        fundamentals = fundamentals.sort_values(DESCENDING_KEY, ascending=False)
        fundamentals[new_descending_key] = rates_list
        fundamentals = fundamentals.sort_values(ASCENDING_KEY)
        fundamentals[new_ascending_key] = rates_list

        rates = fundamentals[new_descending_key] + fundamentals[new_ascending_key]
        return rates.to_frame("rate")

    @staticmethod
    def _get_market_indicator(quotations):
        MARKET_TICKER = "IBOV"
        WINDOW = 100
        market_quotation = quotations[quotations["ticker"] == MARKET_TICKER]
        market_mean = market_quotation["close"].ewm(span=WINDOW, min_periods=WINDOW).mean()
        difference = market_mean - market_mean.shift(1)
        trend = difference.where(difference < 0, 1)
        trend = trend.where(trend >= 0, -1)
        market_trend = trend.iloc[-1]
        market_indicator = {"ticker": MARKET_TICKER, "rate": None, "trend": market_trend}
        return market_indicator

    @staticmethod
    def _to_list(rates, market_indicator):
        indicators = rates.copy()
        indicators["trend"] = None
        indicators.index.name = "ticker"
        indicators = indicators.reset_index().to_dict(orient="records")
        indicators = indicators + [market_indicator]
        return indicators
