#!/bin/env python3
# -*- coding: utf-8 -*-
# version: Python3.X
""" Description
"""
import datetime
from utils.common import logger
from utils.llm_predict import LargeLanguageModel
from utils.collect_history_winner import history_year, current_year
from utils.custom_db import MyLottoDB

__author__ = '__L1n__w@tch'


def update_html_with_win_status_and_predict_number():
    logger.info("Start to update html with win status and predict number")
    pass


def auto_purchase_lotto(number):
    logger.info("Start to auto purchase lotto")
    print(number)
    pass


def predict_next_lotto():
    logger.info("Start to predict next lotto")

    llm = LargeLanguageModel()
    my_db = MyLottoDB()
    recent_win = my_db.get_recent_lotto_win_numbers()
    numbers = llm.predict(recent_win)
    return numbers


def check_win_status():
    logger.info("Start to check win status -- Not implemented yet")
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
    number = predict_next_lotto()
    auto_purchase_lotto(number)
    update_html_with_win_status_and_predict_number()


if __name__ == "__main__":
    main()
