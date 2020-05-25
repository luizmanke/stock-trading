#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# System libraries
from apscheduler.schedulers.background import BackgroundScheduler

# Own libraries
from backend.resources import daily_update


# Set triggers
scheduler = BackgroundScheduler()
scheduler.add_job(
    daily_update.run, trigger="cron", day_of_week="mon-fri", hour=23, timezone="UTC")
scheduler.start()
