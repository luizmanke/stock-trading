#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# System libraries
import pandas as pd
import warnings

# Configurations
warnings.filterwarnings('ignore')


# TODO: Filter companies using volume
class Strategy():

    def __init__(self):
        super(Strategy, self).__init__()
        self.indicators_ = pd.DataFrame(columns=["ticker"])

        # Private variables
        self._market_trend = pd.DataFrame()

    def update_indicators(self, data):
        self._compute_market_trend(data)
        signs = self._get_signs(data)
        strengths = self._get_strengths(data)
        stops = self._get_stops(data)

        # Remove market
        signs = signs[signs["ticker"] != "IBOV"]
        strengths = strengths[strengths["ticker"] != "IBOV"]
        stops = stops[stops["ticker"] != "IBOV"]

        # Concatenate indicators
        for ticker in set(data["ticker"]):
            ticker_sign = signs[signs["ticker"] == ticker]
            ticker_strength = strengths[strengths["ticker"] == ticker]
            ticker_stop = stops[stops["ticker"] == ticker]
            ticker_indicators = pd.concat([ticker_sign["sign"],
                                           ticker_strength["strength"],
                                           ticker_stop["stop"],
                                           ticker_sign["start"],
                                           ticker_sign["trend"]], axis=1)
            ticker_indicators["ticker"] = ticker

            # Loop indicators
            for index, indicator in ticker_indicators.iterrows():
                if indicator["sign"] == "buy":

                    # Remove long stops
                    STOP_THRESHOLD = 0.1
                    stop = indicator["stop"]
                    start = indicator["start"]
                    stop_range = abs(start - stop) / start
                    stop_flag = stop_range > STOP_THRESHOLD

                    # Remove weak strengths
                    STRENGTH_THRESHOLD = 0
                    strength_flag = indicator["strength"] < STRENGTH_THRESHOLD

                    # Change indicators
                    if stop_flag or strength_flag:
                        location = ((ticker_indicators.index == index) &
                                    (ticker_indicators["ticker"] == indicator["ticker"]))
                        ticker_indicators.loc[location, "sign"] = "hold"

            # Update indicators
            ticker_data = self.indicators_[self.indicators_["ticker"] == ticker]
            ticker_data = pd.concat([ticker_data, ticker_indicators])
            ticker_data = ticker_data[~ticker_data.index.duplicated(keep="last")]
            remaining_data = self.indicators_[self.indicators_["ticker"] != ticker]
            self.indicators_ = pd.concat([remaining_data, ticker_data])

        self.indicators_ = self.indicators_.sort_index()

    def _compute_market_trend(self, data):
        market_data = data[data["ticker"] == "IBOV"]
        mean = market_data["close"].rolling(window=21).mean()
        difference = mean - mean.shift(1)
        trend = difference.where(difference < 0, 1)
        trend = trend.where(trend >= 0, -1)
        self._market_trend = trend

    def _get_signs(self, data):
        WINDOW = 16

        # Loop tickers
        signs = pd.DataFrame()
        tickers = set(data["ticker"])
        for ticker in tickers:
            ticker_data = data[data["ticker"] == ticker]

            # Compute moving average
            ticker_mean = ticker_data.ewm(span=WINDOW, min_periods=WINDOW).mean()

            # Compute sign
            difference = ticker_mean["close"] - ticker_mean["close"].shift(1)
            positive_trend = difference.where(difference < 0, 1)
            positive_trend = positive_trend.where(positive_trend >= 0, 0) - 1
            positive_trigger = positive_trend.diff()
            positive_sign = positive_trend.where(positive_trigger != 1, 1)

            negative_trend = positive_trend.replace({0: -1, -1: 0})
            negative_trigger = negative_trend.diff()
            negative_sign = negative_trend.where(negative_trigger != 1, 1)

            # Check if value is greater than moving average
            ticker_close = ticker_data["close"].copy()
            ticker_close[~positive_sign.isin([1])] = float("inf")
            positive_sign = positive_sign.where(ticker_close > ticker_mean["close"], 0)

            ticker_close = ticker_data["close"].copy()
            ticker_close[~negative_sign.isin([1])] = float("-inf")
            negative_sign = negative_sign.where(ticker_close < ticker_mean["close"], 0)

            # Rename signs
            positive_sign = positive_sign.replace({-1: "sell", 0: "hold", 1: "buy"})
            negative_sign = negative_sign.replace({-1: "sell", 0: "hold", 1: "buy"})

            # Add starts
            positive_price = ticker_data["high"] + 0.01
            negative_price = ticker_data["low"] - 0.01
            ticker_positive_sign = positive_sign.to_frame(name="sign")
            ticker_positive_sign["start"] = positive_price.where(
                ticker_positive_sign["sign"] == "buy", negative_price)
            ticker_positive_sign["trend"] = "positive"

            ticker_negative_sign = negative_sign.to_frame(name="sign")
            ticker_negative_sign["start"] = negative_price.where(
                ticker_negative_sign["sign"] == "buy", positive_price)
            ticker_negative_sign["trend"] = "negative"

            # Create sign based on market trend
            condition = [index in positive_sign.index for index in self._market_trend.index]
            market_trend_filtered = self._market_trend[condition]
            ticker_sign = ticker_positive_sign.copy()
            ticker_sign["sign"] = ticker_positive_sign["sign"].where(
                market_trend_filtered > 0, "sell")

            # Update signs
            ticker_sign["ticker"] = ticker
            signs = pd.concat([signs, ticker_sign])
        signs = signs.sort_index()
        return signs

    def _get_strengths(self, data):
        WINDOW = 15

        # Loop tickers
        strengths = pd.DataFrame()
        tickers = set(data["ticker"])
        for ticker in tickers:
            ticker_data = data[data["ticker"] == ticker]

            # Strength
            ticker_close = ticker_data["close"].copy()
            change = ticker_close - ticker_close.shift(WINDOW)
            ticker_strength = round(100 * change / ticker_close, 2)

            # Create sign based on market trend
            condition = [index in ticker_strength.index for index in self._market_trend.index]
            market_trend_filtered = self._market_trend[condition]
            ticker_strength = ticker_strength.where(market_trend_filtered > 0,
                                                    ticker_strength * -1)

            # Update strengths
            ticker_strength = ticker_strength.to_frame(name="strength")
            ticker_strength["ticker"] = ticker
            strengths = pd.concat([strengths, ticker_strength])
        strengths = strengths.sort_index()
        return strengths

    def _get_stops(self, data):
        WINDOW = 14

        # Loop tickers
        stops = pd.DataFrame()
        tickers = set(data["ticker"])
        for ticker in tickers:
            ticker_data = data[data["ticker"] == ticker]

            # Compute ATR
            close = ticker_data["close"]
            high = ticker_data["high"]
            low = ticker_data["low"]
            previous_close = close.shift(1)
            case_1 = high - low
            case_2 = abs(high - previous_close)
            case_3 = abs(low - previous_close)
            concatenated = pd.concat([case_1, case_2, case_3], axis=1)
            true_range = concatenated.max(axis=1)
            avg_true_range = true_range.rolling(window=WINDOW).mean()

            # Stop
            positive_stop = ticker_data["high"] - 2 * avg_true_range
            negative_stop = ticker_data["low"] + 2 * avg_true_range

            # Create sign based on market trend
            condition = [index in positive_stop.index for index in self._market_trend.index]
            market_trend_filtered = self._market_trend[condition]
            ticker_stop = positive_stop.where(market_trend_filtered > 0, negative_stop)
            ticker_stop = round(ticker_stop, 2)

            # Update stops
            ticker_stop = ticker_stop.to_frame(name="stop")
            ticker_stop["ticker"] = ticker
            stops = pd.concat([stops, ticker_stop])
        stops = stops.sort_index()
        return stops
