#!/bin/env python3
# -*- coding: utf-8 -*-
# version: Python3.X
""" Description
"""
import requests
import json
from tqdm import tqdm
from bs4 import BeautifulSoup

__author__ = '__L1n__w@tch'

if __name__ == "__main__":
    data = {}
    history_winner_file = "history_winner.json"

    for year in tqdm(range(1982, 2024)):
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

        with open(history_winner_file, "w") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
