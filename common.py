#!/venv/env python3
# -*- coding: utf-8 -*-
# version: Python3.X
""" 主进程，执行循环监控
"""
import logging
import os

import sys
import datetime


def get_root_path():
    today = get_today()
    root_path = "log/{}".format(today)
    os.makedirs(root_path, exist_ok=True)
    return root_path


def get_today():
    today = datetime.datetime.today()
    today = today.strftime("%Y-%m-%d")
    return today


def get_logger(logger, old_root_path):
    root_path = get_root_path()
    if root_path != old_root_path:
        logger = logging.getLogger('log')
        for each_handler in logger.handlers:
            logger.removeHandler(each_handler)

        old_root_path = root_path
        logger.setLevel(logging.DEBUG)

        # 文件日志
        path = os.path.join(root_path, '{}.log'.format(os.path.basename(__file__)))
        fh = logging.FileHandler(path, encoding='utf-8', mode='a')
        fh.setLevel(logging.INFO)
        formatter = logging.Formatter(fmt='[%(asctime)s-%(filename)s-%(levelname)s]:%(message)s',
                                      datefmt='%Y-%m-%d_%I:%M:%S_%p')
        fh.setFormatter(formatter)
        logger.addHandler(fh)

        # 重要文件日志
        dl = logging.FileHandler(os.path.join(root_path, "deal.log"), encoding='utf-8', mode='a')
        dl.setLevel(logging.CRITICAL)
        formatter = logging.Formatter(fmt='[%(asctime)s-%(filename)s-%(levelname)s]:%(message)s',
                                      datefmt='%Y-%m-%d_%I:%M:%S_%p')
        dl.setFormatter(formatter)
        logger.addHandler(dl)

        # 控制台日志
        formatter = logging.Formatter('[%(levelname)s]：%(message)s')
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(formatter)
        logger.addHandler(ch)

    return logger, old_root_path
