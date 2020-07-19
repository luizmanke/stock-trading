#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# System libraries
import dotenv

# Own libraries
from .. import replace_database

# Configurations
dotenv.load_dotenv()


def test_run():
    replace_database.run()
