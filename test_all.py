#!/bin/env python3
# -*- coding: utf-8 -*-
# version: Python3.X
""" Description
"""
import unittest
from unittest import TestCase
from unittest.mock import MagicMock

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
