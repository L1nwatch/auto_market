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

MY_DB = MyLottoDB()


def update_html_with_win_status_and_predict_number(last_lotto_date):
    logger.info("Start to update html with win status and predict number")

    all_buying_history = MY_DB.get_all_buying_history()
    for each_data in all_buying_history:
        predict_nums = MY_DB.get_predict_nums(each_data["last_lotto_date"])
        each_data["predict_nums"] = predict_nums

    # format to html
    format_buying_history = []
    for each_data in all_buying_history:
        one_row = list()
        one_row.append(f"<td>{each_data['last_lotto_date']}</td>")
        one_row.append(f"<td>{each_data['bought_numbers']}</td>")
        one_row.append(f"<td>{each_data['win_status']}</td>")
        one_row.append(f"<td>{each_data['predict_nums']}</td>")
        format_buying_history.append(f"<tr>{''.join(one_row)}</tr>")

    # update to html
    with open("docs/index_template.html", "r") as f:
        html = f.read()
        html = html.replace("{{ need_to_be_replaced }}", "\n".join(format_buying_history))
    with open("docs/index.html", "w") as f:
        f.write(html)


def auto_purchase_lotto(last_lotto_date, number):
    logger.info("Start to auto purchase lotto")
    if not MY_DB.check_buying_history_exist(last_lotto_date):
        logger.info(f"Start to buy lotto: {number}")
        # do_buying(last_lotto_date, number) # TODO: manual buying for now
        MY_DB.save_buying_history(last_lotto_date, number) # TODO: manual buying for now
    else:
        logger.info(f"Already bought lotto for {last_lotto_date}")


def predict_next_lotto(last_lotto_date):
    logger.info("Start to predict next lotto")
    # check if already have numbers
    predict_nums = MY_DB.get_predict_nums(last_lotto_date)
    if predict_nums:
        logger.info(f"Already have predict numbers: {predict_nums}")
        return predict_nums

    llm = LargeLanguageModel(model="openai")
    recent_win = MY_DB.get_recent_lotto_win_numbers()
    numbers = llm.predict(recent_win, last_lotto_date)
    return numbers


def check_win_status():
    logger.info("Start to check win status")
    all_buying_history = MY_DB.get_all_buying_history()
    for each_data in all_buying_history:
        if each_data["win_status"] != "empty":
            continue
        logger.info(f"Check win status for {each_data['last_lotto_date']}")
        next_date = MY_DB.get_next_date(each_data["last_lotto_date"])
        if not next_date:
            logger.info(f"still waiting for {each_data['last_lotto_date']} result")
            continue
        year, month, day = next_date["year"], next_date["month"], next_date["day"]
        check, result = MY_DB.check_lotto_result_exist(year=year, month=month, day=day, need_result=True)
        if not check:
            continue
        MY_DB.update_win_status(each_data["last_lotto_date"], win_status="empty")  # TODO: check win status


def fetch_history_data():
    today = datetime.datetime.now()

    logger.info("Start to fetch history year lotto data")
    history_year(end_year=today.year - 1)

    logger.info("Start to fetch current year lotto data")
    current_year(today.year)

    last_lotto_date = MY_DB.get_last_lotto_date()
    return last_lotto_date


def git_commit_and_push():
    logger.info("Start to git commit and push")
    import os
    os.system("git add .")
    os.system("git commit -m 'auto commit'")
    os.system("git push")


def main():
    last_lotto_date = fetch_history_data()
    check_win_status()
    number = predict_next_lotto(last_lotto_date)
    auto_purchase_lotto(last_lotto_date, number)
    update_html_with_win_status_and_predict_number(last_lotto_date)
    git_commit_and_push()


if __name__ == "__main__":
    main()
