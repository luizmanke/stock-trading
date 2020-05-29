#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# System libraries
import datetime as dt


def get_today_date():
    UTC = -3
    today_date = dt.datetime.utcnow() + dt.timedelta(hours=UTC)
    today_date = today_date.replace(hour=0, minute=0, second=0, microsecond=0)
    return today_date
