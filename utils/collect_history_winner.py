#!/bin/env python3
# -*- coding: utf-8 -*-
# version: Python3.X
""" Description
"""
import requests
import json
import os
from loguru import logger
from tqdm import tqdm
from datetime import datetime, timedelta
from utils.common import root
from bs4 import BeautifulSoup
from utils.custom_db import MySQLite

__author__ = '__L1n__w@tch'

MY_DB = MySQLite()

# proxies = {
#     "http": "http://127.0.0.1:6152",  # HTTP proxy
#     "https": "http://127.0.0.1:6152"  # HTTPS proxy
# }


def is_result_exist(year):
    global MY_DB
    exist = MY_DB.check_lotto_result_exist(year)
    if not exist:
        # try to update db from local file
        local_file = os.path.join(root, "data", "history_winner.json")
        if os.path.exists(local_file):
            with open(local_file, "r") as f:
                data = json.load(f)
            if str(year) in data:
                MY_DB.save_results(data, year)
                return True
        pass
    return MY_DB.check_lotto_result_exist(year)


def history_year(end_year):
    data = {}

    for year in tqdm(range(1982, end_year + 1)):
        if is_result_exist(year):
            logger.info(f"{year} data already exist")
            continue
        logger.info(f"Start to fetch {year} data")
        base_url = f"https://loteries.lotoquebec.com/en/lotteries/lotto-6-49?annee={year}&widget=resultats-anterieurs&noPro" \
                   f"duit=212#res"
        # response = requests.get(base_url, proxies=proxies)
        response = requests.get(base_url)

        soup = BeautifulSoup(response.text, 'html.parser')
        rows = soup.find_all('tr')
        for row in rows:
            try:
                date = row.find('td', class_='date').text
                divs = row.find_all("div")
                mark_name = "default"
                for each_div in divs:
                    if "draw" in each_div.text.lower() or "prize" in each_div.text.lower():
                        mark_name = each_div.text
                        continue

                    data[date] = data.get(date, dict())
                    data[date][mark_name] = data[date].get(mark_name, list())
                    lotto_result = str(each_div.text).strip().split()
                    data[date][mark_name].append(lotto_result)
            except Exception as e:
                print(e)

        MY_DB.save_results(data, year)


def get_current_results_date(year):
    result = list()
    for month in range(1, 13):
        start_date = f"{year}-{month:02}-01"
        basic_url = f"https://loteries.lotoquebec.com/en/lotteries/lotto-6-49?widget=resultats&action=historique&noproduit=212&date={start_date}"
        # response = requests.get(basic_url, proxies=proxies)
        response = requests.get(basic_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        dates = soup.find_all("div", class_="dateTirage")
        if len(dates) < 1:
            break
        for each_date in dates:
            result.append(each_date.text)
    return result


def current_year(year):
    data = dict()
    dates = get_current_results_date(year)
    for each_date in dates:
        data[each_date] = dict()
        base_url = f"https://loteries.lotoquebec.com/en/lotteries/lotto-6-49?date={each_date}"
        # response = requests.get(base_url, proxies=proxies)
        response = requests.get(base_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        divs = soup.find_all("div", class_="lqZoneStructuresDeLots")
        for i, each_div in enumerate(divs):
            data[each_date][i] = each_div.text.strip()

    if len(data) > 0:
        MY_DB.save_results(data, year)


if __name__ == "__main__":
    # history_year(2024)
    current_year(2025)
