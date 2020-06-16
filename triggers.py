#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# System libraries
import traceback
from apscheduler.schedulers.background import BlockingScheduler

# Own libraries
from backend.resources import update_metadata, update_indicators, \
    update_wallets, update_performances, utils


def daily_update():
    print("## DAILY UPDATE ##")
    try:
        update_metadata.run()
        update_indicators.run()
        update_wallets.run()
        update_performances.run()
        utils.send_email("Daily update: Succeeded", "")
    except Exception:
        error = traceback.format_exc()
        print(error)
        utils.send_email("Daily update: Failed!", f"{error}")


# Set triggers
scheduler = BlockingScheduler()
scheduler.add_job(
    daily_update, trigger="cron", day_of_week="mon-fri", hour=21, minute=15, timezone="UTC")
scheduler.start()
