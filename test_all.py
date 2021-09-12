#!/bin/env python3
# -*- coding: utf-8 -*-
# version: Python3.X
""" Description
"""
import unittest
from unittest import TestCase
from unittest.mock import MagicMock

import common
import main

__author__ = '__L1n__w@tch'


class TestMain_loop(TestCase):
    def test_when_right_update_history_time_come(self):
        """
        假设晚上的时间已到，用于调试脚本用的
        :return:
        """
        with unittest.mock.patch("main.is_right_update_history_time") as my_mock:
            my_mock.return_value = True
            main.main_loop()

    def test_when_right_commission_come(self):
        """
        假设 morning 的时间已到，用于调试脚本用的
        :return:
        """
        with unittest.mock.patch("main.is_right_commission_time") as my_mock:
            my_mock.return_value = True
            main.main_loop()


class TestCommon(TestCase):
    def test_update_readme_history(self):
        common.update_readme_history()

    def test_analysis_trades_log(self):
        common.analysis_trades_log()

