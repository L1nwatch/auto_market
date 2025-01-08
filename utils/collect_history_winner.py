#!/bin/env python3
# -*- coding: utf-8 -*-
# version: Python3.X
""" Description
"""
import requests
import json
import os
from tqdm import tqdm
from datetime import datetime, timedelta
from utils.common import root
from bs4 import BeautifulSoup
from utils.custom_db import MySQLite

__author__ = '__L1n__w@tch'

MY_DB = MySQLite()


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
                save_results(data, year)
                return True
        pass
    return MY_DB.check_lotto_result_exist(year)


def history_year(end_year):
    data = {}

    for year in tqdm(range(1982, end_year + 1)):
        if is_result_exist(year):
            continue
        base_url = f"https://loteries.lotoquebec.com/en/lotteries/lotto-6-49?annee={year}&widget=resultats-anterieurs&noProduit=212#res"
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
                    data[date][mark_name].append(each_div.text)
            except Exception as e:
                print(e)

        save_results(data, year)


def get_current_results_date():
    result = list()
    for month in range(1, 13):
        start_date = f"2024-{month:02}-01"
        basic_url = f"https://loteries.lotoquebec.com/en/lotteries/lotto-6-49?widget=resultats&action=historique&noproduit=212&date={start_date}"
        response = requests.get(basic_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        dates = soup.find_all("div", class_="dateTirage")
        for each_date in dates:
            result.append(each_date.text)
    return result


def current_year():
    saved_file = "../data/current_winner.json"
    data = dict()
    dates = get_current_results_date()
    for each_date in dates:
        data[each_date] = dict()
        base_url = f"https://loteries.lotoquebec.com/en/lotteries/lotto-6-49?date={each_date}"
        response = requests.get(base_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        divs = soup.find_all("div", class_="lqZoneStructuresDeLots")
        for i, each_div in enumerate(divs):
            data[each_date][i] = each_div.text.strip()

        with open(saved_file, "w") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    # history_year()
    current_year()
