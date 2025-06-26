#!/bin/env python3
# -*- coding: utf-8 -*-
# version: Python3.X
""" Description
"""
import datetime
import re
import os
import json
from utils.common import logger
from utils.llm_predict import LargeLanguageModel
from utils.random_predict import RandomLottoNumberGenerator
from utils.frequency_predict import FrequencyWeightedPredictor
from utils.collect_history_winner import history_year, current_year
from utils.custom_db import MyLottoDB
from utils.purchase_lotto_tickets import do_buying

__author__ = '__L1n__w@tch'

MY_DB = MyLottoDB()


def update_html_with_win_status_and_predict_number():
    logger.info("Start to update html with win status and predict number")

    all_buying_history = MY_DB.get_all_buying_history()
    group_summary = {}
    for each_data in all_buying_history:
        predict_nums = MY_DB.get_predict_nums(each_data["last_lotto_date"])
        each_data["predict_nums"] = predict_nums
        # ensure predict_number_sources always has a value
        if not each_data.get("predict_number_sources"):
            each_data["predict_number_sources"] = "LLM"
        source = each_data["predict_number_sources"]
        if source not in group_summary:
            group_summary[source] = {
                "total_tickets": 0,
                "total_win_numbers": 0,
                "distribution": {i: 0 for i in range(7)}
            }

        group_summary[source]["total_tickets"] += 1

        matched = re.search(r"match (\d+) number", each_data["win_status"])
        if matched:
            count = int(matched.group(1))
            group_summary[source]["total_win_numbers"] += count
            if count in group_summary[source]["distribution"]:
                group_summary[source]["distribution"][count] += 1

    # build summary and distribution tables
    summary_tables = []
    matched_distribution_tables = []
    for source, data in group_summary.items():
        summary_tables.append(f"<h3>{source}</h3>")
        avg_hit_rate = 0
        if data["total_tickets"] > 0:
            avg_hit_rate = data["total_win_numbers"] / (data["total_tickets"] * 6)

        summary_tables.append(
            f"<table><tr><th>Total Tickets Bought</th><td>{data['total_tickets']}</td></tr>"
            f"<tr><th>Total Win Numbers</th><td>{data['total_win_numbers']}</td></tr>"
            f"<tr><th>Average Hit Rate</th><td>{avg_hit_rate:.2%}</td></tr></table>"
        )

        matched_distribution_tables.append(f"<h3>{source}</h3>")
        rows = []
        for i in range(7):
            rows.append(f"<tr><td>{i}</td><td>{data['distribution'][i]}</td></tr>")
        matched_distribution_tables.append(
            "<table><thead><tr><th>Matched Numbers</th><th>Ticket Count</th></tr></thead><tbody>"
            + "".join(rows) + "</tbody></table>"
        )

    # format buying history
    format_buying_history = []
    for each_data in all_buying_history:
        one_row = list()
        one_row.append(f"<td>{each_data['last_lotto_date']}</td>")
        one_row.append(f"<td>{each_data['bought_numbers']}</td>")
        one_row.append(f"<td>{each_data['win_status']}</td>")
        one_row.append(f"<td>{each_data['predict_nums']}</td>")
        one_row.append(f"<td>{each_data['predict_number_sources']}</td>")
        format_buying_history.append(f"<tr>{''.join(one_row)}</tr>")

    # update to html
    with open("docs/index_template.html", "r") as f:
        html = f.read()
        html = html.replace("{{ need_to_be_replaced }}", "\n".join(format_buying_history))
        html = html.replace("{{ summary_tables }}", "\n".join(summary_tables))
        html = html.replace("{{ matched_distribution_tables }}", "\n".join(matched_distribution_tables))
    with open("docs/index.html", "w") as f:
        f.write(html)


def auto_purchase_lotto(last_lotto_date, number, source="LLM"):
    logger.info(f"Start to auto purchase lotto: {number}")
    if not MY_DB.check_buying_history_exist(last_lotto_date):
        logger.info(f"Start to buy lotto")
        do_buying(number)
        MY_DB.save_buying_history(last_lotto_date, number, source=source)
    else:
        logger.info(f"Already bought lotto for {last_lotto_date}")


def format_number(number: str):
    """
    {'generate_nums': ['01', '02', '03, '04', '05', '06']}
    """
    # skip string before {'generate_nums': ['
    try:
        number = re.findall(r"generate_nums[\s\S]+", number)[0]
        numbers = re.findall(r"\d+", number)
        return "-".join(numbers)
    except Exception as e:
        logger.error(f"Extra number Error: {e}")
        return number


def predict_next_lotto(last_lotto_date, source="LLM"):
    """Return predicted lotto numbers.

    Parameters
    ----------
    last_lotto_date : str
        Last draw date from the database.
    source : str, optional
        Prediction method to use. If "RANDOM", numbers are generated at random;
        otherwise the LLM-based method is used. Default "LLM".
    """

    logger.info("Start to predict next lotto")

    predict_nums = MY_DB.get_predict_nums(last_lotto_date)
    if predict_nums:
        logger.info(f"Already have predict numbers: {predict_nums}")
        # stored LLM results might need formatting
        if "generate_nums" in predict_nums:
            predict_nums = format_number(predict_nums)
        return predict_nums

    if source.upper() == "RANDOM":
        generator = RandomLottoNumberGenerator()
        return generator.predict(last_lotto_date)
    if source.upper() == "FREQ":
        generator = FrequencyWeightedPredictor()
        return generator.predict(last_lotto_date)

    llm = LargeLanguageModel(model="openai")
    recent_win = MY_DB.get_recent_lotto_win_numbers()
    predict_nums = llm.predict(recent_win, last_lotto_date)
    logger.info(f"Predict numbers: {predict_nums}")
    return format_number(predict_nums)


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

        bought_numbers = re.findall(r"\d+", each_data["bought_numbers"])
        win_number = json.loads(result[0]["data"])["0"]
        count = sum([1 for each_bought_number in bought_numbers if each_bought_number in win_number])
        MY_DB.update_win_status(each_data["last_lotto_date"],
                                win_status=f"match {count} number, win number: {win_number}")


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
    os.system("git add .")
    os.system("git commit -m 'auto commit'")
    os.system("git push")


def main():
    last_lotto_date = fetch_history_data()
    check_win_status()
    source = "RANDOM"
    number = predict_next_lotto(last_lotto_date, source=source)
    auto_purchase_lotto(last_lotto_date, number, source=source)
    update_html_with_win_status_and_predict_number()
    git_commit_and_push()


if __name__ == "__main__":
    main()
