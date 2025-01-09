#!/bin/env python3
# -*- coding: utf-8 -*-
# version: Python3.X
""" Description
"""
import datetime
from utils.common import logger
from utils.collect_history_winner import history_year, current_year

__author__ = '__L1n__w@tch'


def update_html_with_win_status_and_predict_number():
    logger.info("Start to update html with win status and predict number")
    pass


def auto_purchase_lotto():
    logger.info("Start to auto purchase lotto")
    pass


def predict_next_lotto():
    logger.info("Start to predict next lotto")
    pass


def check_win_status():
    logger.info("Start to check win status")
    pass


def fetch_history_data():
    today = datetime.datetime.now()

    logger.info("Start to fetch history year lotto data")
    history_year(end_year=today.year - 1)

    logger.info("Start to fetch current year lotto data")
    current_year(today.year)


def main():
    fetch_history_data()
    check_win_status()
    predict_next_lotto()
    auto_purchase_lotto()
    update_html_with_win_status_and_predict_number()


if __name__ == "__main__":
    main()
