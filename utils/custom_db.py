#!/bin/env python3
# -*- coding: utf-8 -*-
# version: Python3.X
""" Description
"""
import os
import json
import re
import sqlite3
from utils.common import root

__author__ = '__L1n__w@tch'


class MyLottoDB:
    def __init__(self):
        self.conn = sqlite3.connect(os.path.join(root, "data", "lotto.db"))
        self.cursor = self.conn.cursor()
        self.initialize_table()

    def initialize_table(self):
        sql = """
        CREATE TABLE IF NOT EXISTS history_lotto (
            tid INTEGER PRIMARY KEY,
            year INTEGER,
            month INTEGER,
            day INTEGER,
            data JSON
        )
        """
        self.cursor.execute(sql)
        self.conn.commit()

    def check_lotto_result_exist(self, *, year, month, day):
        sql = f"SELECT * FROM history_lotto WHERE year = {year}"
        if month:
            sql += f" AND month = {month}"
        if day:
            sql += f" AND day = {day}"
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        return len(result) > 0

    def get_recent_lotto_win_numbers(self):
        results = dict()
        sql = "SELECT * FROM history_lotto ORDER BY year DESC, month DESC, day DESC LIMIT 24"
        self.cursor.execute(sql)
        raw_data = self.cursor.fetchall()
        for data in raw_data:
            year, month, day, value = data[1], data[2], data[3], data[4]
            value = json.loads(value)
            value = re.findall(r"\d{2}", value["0"])
            results[f"{year}-{month:02}-{day:02}"] = value
        return results

    def save_results(self, data, expected_year):
        for date, value in data.items():
            year, month, day = date.split("-")
            if str(year) != str(expected_year):
                continue
            if self.check_lotto_result_exist(year=year, month=month, day=day):
                continue
            value = json.dumps(value)
            sql = f"INSERT INTO history_lotto (year, month, day, data) VALUES ({year}, {month}, {day}, '{value}')"
            self.cursor.execute(sql)
            self.conn.commit()


if __name__ == "__main__":
    pass
