#!/bin/env python3
# -*- coding: utf-8 -*-
# version: Python3.X
""" Description
"""
import os
from loguru import logger

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def github_sink(message):
    record = message.record
    level = record["level"].name
    log_message = record["message"]

    if level == "ERROR":
        print(f"::error::{log_message}")
    elif level == "WARNING":
        print(f"::warning::{log_message}")
    else:
        print(log_message)  # Default to standard output


# Configure Loguru to use the custom sink
logger.remove()  # Remove the default sink
logger.add(github_sink)
