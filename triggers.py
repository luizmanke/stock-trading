#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# System libraries
import traceback
from apscheduler.schedulers.background import BlockingScheduler

# Own libraries
from backend.resources import update_metadata, update_indicators, utils


def daily_update():
    print("## DAILY UPDATE ##")
    try:
        update_metadata.run()
        update_indicators.run()
        # TODO: update_performance()
        utils.send_email("Daily update: Succeeded", "")
    except Exception:
        error = traceback.format_exc()
        print(error)
        utils.send_email("Daily update: Failed!", f"{error}")


# Set triggers
scheduler = BlockingScheduler()
scheduler.add_job(daily_update, trigger="cron", day_of_week="mon-fri", hour=21, timezone="UTC")
scheduler.start()
