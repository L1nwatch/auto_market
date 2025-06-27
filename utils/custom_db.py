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
                results TEXT,
                predict_number_sources TEXT DEFAULT 'LLM'
            )
            """,
            f"""
            CREATE TABLE IF NOT EXISTS {self.table_name['buying_history']} (
                tid INTEGER PRIMARY KEY,
                last_lotto_date TEXT,
                bought_numbers TEXT,
                win_status TEXT,
                predict_number_sources TEXT DEFAULT 'LLM'
            )
            """
        ]
        for sql in sqls:
            self.cursor.execute(sql)
        self._add_column_if_not_exists(
            self.table_name['llm_lotto_predict'],
            'predict_number_sources',
            "TEXT DEFAULT 'LLM'"
        )
        self._add_column_if_not_exists(
            self.table_name['buying_history'],
            'predict_number_sources',
            "TEXT DEFAULT 'LLM'"
        )
        self.conn.commit()

    def _add_column_if_not_exists(self, table, column, column_def):
        self.cursor.execute(f"PRAGMA table_info({table})")
        columns = [info[1] for info in self.cursor.fetchall()]
        if column not in columns:
            self.cursor.execute(
                f"ALTER TABLE {table} ADD COLUMN {column} {column_def}")

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

    def get_lotto_numbers_since(self, start_date):
        """Return all lotto numbers from the given date (inclusive)."""
        start_val = start_date.year * 10000 + start_date.month * 100 + start_date.day
        sql = (
            f"SELECT * FROM {self.table_name['history_lotto']} "
            f"ORDER BY year DESC, month DESC, day DESC LIMIT 300"
        )
        self.cursor.execute(sql)
        raw_data = self.cursor.fetchall()
        results = []
        for row in raw_data:
            year, month, day, value = row[1], row[2], row[3], row[4]
            current_val = year * 10000 + month * 100 + day
            if current_val < start_val:
                break
            try:
                data = json.loads(value)
                numbers = re.findall(r"\d{2}", data["0"])
                numbers = [int(n) for n in numbers[:7]]
                if len(numbers) == 7:
                    results.append(numbers)
            except Exception:
                continue
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

    def save_predict_nums(self, last_lotto_date, prompt, response, source="LLM"):
        prompt = json.dumps(prompt)
        sql = f"INSERT INTO {self.table_name['llm_lotto_predict']} (last_lotto_date, prompt, results, predict_number_sources) VALUES (?, ?, ?, ?)"
        self.cursor.execute(sql, (last_lotto_date, prompt, response, source))
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

    def get_history_since(self, start_date):
        """Return draw records from ``start_date`` onward ordered by date descending."""
        start_val = start_date.year * 10000 + start_date.month * 100 + start_date.day
        sql = (
            f"SELECT year, month, day, data FROM {self.table_name['history_lotto']} "
            "WHERE (year * 10000 + month * 100 + day) >= ? "
            "ORDER BY year DESC, month DESC, day DESC"
        )
        self.cursor.execute(sql, (start_val,))
        return self.cursor.fetchall()

    def get_next_record(self, date):
        """Return the draw record immediately after ``date`` if available."""
        year, month, day = [int(x) for x in date.split("-")]
        current_val = year * 10000 + month * 100 + day
        sql = (
            f"SELECT year, month, day, data FROM {self.table_name['history_lotto']} "
            "WHERE (year * 10000 + month * 100 + day) > ? "
            "ORDER BY year ASC, month ASC, day ASC LIMIT 1"
        )
        self.cursor.execute(sql, (current_val,))
        rows = self.cursor.fetchall()
        return self._format_result(rows)[0] if rows else None

    def get_numbers_in_range(self, start_date, end_date):
        """Return lotto numbers between ``start_date`` and ``end_date`` (exclusive)."""
        start_val = start_date.year * 10000 + start_date.month * 100 + start_date.day
        end_val = end_date.year * 10000 + end_date.month * 100 + end_date.day
        sql = (
            f"SELECT data FROM {self.table_name['history_lotto']} "
            "WHERE (year * 10000 + month * 100 + day) >= ? "
            "AND (year * 10000 + month * 100 + day) < ?"
        )
        self.cursor.execute(sql, (start_val, end_val))
        raw = self.cursor.fetchall()
        results = []
        for row in raw:
            try:
                data = json.loads(row[0])
                if "0" in data:
                    text = data["0"]
                else:
                    first = next(iter(data.values()))
                    if isinstance(first, list):
                        first = " ".join(first[0]) if isinstance(first[0], list) else " ".join(first)
                    text = str(first)
                text = re.sub(r"\s+", " ", text.strip())
                numbers = [int(n) for n in re.findall(r"\d+", text)[:7]]
                results.append(numbers)
            except Exception:
                continue
        return results

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

    def save_buying_history(self, last_lotto_date, number, source="LLM"):
        sql = f"INSERT INTO {self.table_name['buying_history']} (last_lotto_date, bought_numbers, win_status, predict_number_sources) VALUES (?, ?, ?, ?)"
        self.cursor.execute(sql, (last_lotto_date, number, "empty", source))
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
