#!/bin/env python3
# -*- coding: utf-8 -*-
# version: Python3.X
""" Description
"""
import os
import sqlite3
from utils.common import root

__author__ = '__L1n__w@tch'


class MySQLite:
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

    def check_lotto_result_exist(self, year):
        sql = f"SELECT * FROM history_lotto WHERE year = {year}"
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        return len(result) > 0


if __name__ == "__main__":
    pass
