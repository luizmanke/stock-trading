#!/usr/bin/env python3
# -*- coding: utf-8 -*-


def compute_performance(records):
    performance = {}
    _compute_profit(performance, records["patrimony"])
    _compute_sharp_ratio(performance, records["patrimony"])
    _compute_drawdown(performance, records["patrimony"])
    _compute_number_of_trades(performance, records)
    _compute_payoff(performance, records)
    _compute_factors(performance, records)
    return performance


def _compute_profit(performance, patrimony):

    # Profit
    profit = _get_profit(patrimony)
    profit_in_percentage = 100 * profit / patrimony.iloc[0]

    # Annual profit
    indexes = patrimony.index
    delta = indexes[-1] - indexes[0]
    delta_years = delta.days / 365
    annual_profit_percentage = 0
    if delta_years:
        annual_profit_percentage = 100 * (((1 + profit_in_percentage/100) **
                                           (1/delta_years)) - 1)

    performance["profit"] = float(profit)
    performance["profit_in_percentage"] = float(profit_in_percentage)
    performance["annual_profit_in_percentage"] = float(annual_profit_percentage)


def _compute_sharp_ratio(performance, patrimony):
    daily_returns = patrimony.pct_change(1)
    avg_daily_returns = daily_returns.mean()
    std_daily_returns = daily_returns.std()
    daily_sharpe_ratio = avg_daily_returns / std_daily_returns
    sharpe_ratio = (252 ** 0.5) * daily_sharpe_ratio
    performance["sharpe_ratio"] = float(sharpe_ratio)


def _compute_drawdown(performance, patrimony):
    drawdown = _get_drawdown(patrimony)
    performance["maximum_drawdown_in_percentage"] = float(drawdown)


def _compute_number_of_trades(performance, records):
    n_trades_with_gain = records["n_trades_with_gain"].sum()
    n_trades_with_loss = records["n_trades_with_loss"].sum()

    # Total trades
    total_trades = _get_total_trades(records)

    # Trades percentage
    percentage_of_gain_trades = 100 * n_trades_with_gain / total_trades
    percentage_of_loss_trades = 100 * n_trades_with_loss / total_trades

    # Mean profit
    gain_tmp = n_trades_with_gain if n_trades_with_gain else 1
    loss_tmp = n_trades_with_loss if n_trades_with_loss else 1
    avg_gain_per_trade = records["gain_profit"].sum() / gain_tmp
    avg_loss_per_trade = records["loss_profit"].sum() / loss_tmp
    avg_gain_in_percentage = ((n_trades_with_gain *
                               records["avg_gain_profit_percentage"]).sum() /
                              gain_tmp) * 100
    avg_loss_in_percentage = ((n_trades_with_loss *
                               records["avg_loss_profit_percentage"]).sum() /
                              loss_tmp) * 100

    performance["total_trades"] = int(total_trades)
    performance["percentage_of_gain_trades"] = float(percentage_of_gain_trades)
    performance["percentage_of_loss_trades"] = float(percentage_of_loss_trades)
    performance["avg_gain_per_trade"] = float(avg_gain_per_trade)
    performance["avg_loss_per_trade"] = float(avg_loss_per_trade)
    performance["avg_gain_in_percentage"] = float(avg_gain_in_percentage)
    performance["avg_loss_in_percentage"] = float(avg_loss_in_percentage)


def _compute_payoff(performance, records):
    total_trades = _get_total_trades(records)
    profit = records["patrimony"].iloc[-1] - records["patrimony"].iloc[0]
    payoff = profit / total_trades
    performance["payoff"] = float(payoff)


def _compute_factors(performance, records):
    profit = _get_profit(records["patrimony"])
    loss_profit = records["loss_profit"].sum()
    loss_profit = loss_profit if loss_profit else 1
    profit_factor = abs(records["gain_profit"].sum() / loss_profit)
    recuperation_factor = abs(profit / _get_drawdown(records["patrimony"]))
    performance["profit_factor"] = float(profit_factor)
    performance["recuperation_factor"] = float(recuperation_factor)


def _get_profit(patrimony):
    initial_patrimony = patrimony.iloc[0]
    final_patrimony = patrimony.iloc[-1]
    profit = final_patrimony - initial_patrimony
    return profit


def _get_total_trades(records):
    n_trades_with_gain = records["n_trades_with_gain"].sum()
    n_trades_with_loss = records["n_trades_with_loss"].sum()
    total_trades = n_trades_with_gain + n_trades_with_loss
    return total_trades


def _get_drawdown(patrimony):
    rolling_maximum = patrimony.cummax()
    drawdowns = 100 * (patrimony - rolling_maximum) / rolling_maximum
    drawdowns = drawdowns.dropna()
    maximum_drawdown_percentage = min(drawdowns)
    return maximum_drawdown_percentage
