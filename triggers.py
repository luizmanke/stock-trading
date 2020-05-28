#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# System libraries
from apscheduler.schedulers.background import BlockingScheduler

# Own libraries
from backend.resources import daily_update

# Set triggers
scheduler = BlockingScheduler()
scheduler.add_job(
    daily_update.run, trigger="cron", day_of_week="mon-fri", hour=21, timezone="UTC")
scheduler.start()
