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
        self.table_name = {
            "history_lotto": "history_lotto",
            "llm_lotto_predict": "llm_lotto_predict",
            "buying_history": "buying_history"
        }
        self.initialize_table()

    def initialize_table(self):
        sqls = [
            f"""
            CREATE TABLE IF NOT EXISTS {self.table_name['history_lotto']} (
                tid INTEGER PRIMARY KEY,
                year INTEGER,
                month INTEGER,
                day INTEGER,
                data JSON
            )
            """,
            f"""
            CREATE TABLE IF NOT EXISTS {self.table_name['llm_lotto_predict']} (
                tid INTEGER PRIMARY KEY,
                last_lotto_date TEXT,
                prompt TEXT,
                results TEXT
            )
            """,
            f"""
            CREATE TABLE IF NOT EXISTS {self.table_name['buying_history']} (
                tid INTEGER PRIMARY KEY,
                last_lotto_date TEXT,
                bought_numbers TEXT,
                win_status TEXT
            )
            """
        ]
        for sql in sqls:
            self.cursor.execute(sql)
        self.conn.commit()

    def check_lotto_result_exist(self, *, year, month, day, need_result=False):
        sql = f"SELECT * FROM {self.table_name['history_lotto']} WHERE year = {year}"
        if month:
            sql += f" AND month = {month}"
        if day:
            sql += f" AND day = {day}"
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        result = self._format_result(result)
        if need_result:
            return len(result) > 0, result
        else:
            return len(result) > 0

    def get_recent_lotto_win_numbers(self):
        results = dict()
        sql = f"SELECT * FROM {self.table_name['history_lotto']} ORDER BY year DESC, month DESC, day DESC LIMIT 96"
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
            sql = f"INSERT INTO {self.table_name['history_lotto']} (year, month, day, data) VALUES ({year}, {month}, {day}, '{value}')"
            self.cursor.execute(sql)
            self.conn.commit()

    def get_predict_nums(self, last_lotto_date):
        sql = f"SELECT * FROM {self.table_name['llm_lotto_predict']} WHERE last_lotto_date = ?"
        self.cursor.execute(sql, (last_lotto_date,))
        raw_data = self.cursor.fetchall()
        if len(raw_data) == 0:
            return False

        result = self._format_result(raw_data)
        return result[0]["results"]

    def save_predict_nums(self, last_lotto_date, prompt, response):
        prompt = json.dumps(prompt)
        sql = f"INSERT INTO {self.table_name['llm_lotto_predict']} (last_lotto_date, prompt, results) VALUES (?, ?, ?)"
        self.cursor.execute(sql, (last_lotto_date, prompt, response))
        self.conn.commit()

    def get_last_lotto_date(self):
        sql = f"SELECT * FROM {self.table_name['history_lotto']} ORDER BY year DESC, month DESC, day DESC LIMIT 1"
        self.cursor.execute(sql)
        raw_data = self.cursor.fetchall()
        if len(raw_data) == 0:
            return None
        return f"{raw_data[0][1]}-{raw_data[0][2]:02}-{raw_data[0][3]:02}"

    def _format_result(self, raw_data):
        result = list()
        columns = [col[0] for col in self.cursor.description]

        for data in raw_data:
            result.append({columns[i]: data[i] for i in range(len(columns))})
        return result

    def get_all_buying_history(self):
        sql = f"SELECT * FROM {self.table_name['buying_history']} ORDER BY last_lotto_date DESC"
        self.cursor.execute(sql)
        raw_data = self.cursor.fetchall()
        return self._format_result(raw_data)

    def update_win_status(self, last_lotto_date, win_status):
        sql = f"UPDATE {self.table_name['buying_history']} SET win_status = ? WHERE last_lotto_date = ?"
        self.cursor.execute(sql, (str(win_status), last_lotto_date))
        self.conn.commit()

    def check_buying_history_exist(self, last_lotto_date):
        sql = f"SELECT * FROM {self.table_name['buying_history']} WHERE last_lotto_date = ?"
        self.cursor.execute(sql, (last_lotto_date,))
        raw_data = self.cursor.fetchall()
        return len(raw_data) > 0

    def save_buying_history(self, last_lotto_date, number):
        sql = f"INSERT INTO {self.table_name['buying_history']} (last_lotto_date, bought_numbers, win_status) VALUES (?, ?, ?)"
        self.cursor.execute(sql, (last_lotto_date, number, "empty"))
        self.conn.commit()

    def get_next_date(self, date):
        year, month, day = date.split("-")
        sql = f"SELECT * FROM {self.table_name['history_lotto']} ORDER BY year DESC, month DESC, day DESC LIMIT 24"
        self.cursor.execute(sql)
        raw_data = self.cursor.fetchall()
        raw_data = self._format_result(raw_data)
        raw_data = raw_data[0]
        if raw_data["year"] == int(year) and raw_data["month"] == int(month) and raw_data["day"] == int(day):
            return None
        else:
            return raw_data


if __name__ == "__main__":
    pass
