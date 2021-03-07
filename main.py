#!/venv/env python3
# -*- coding: utf-8 -*-
# version: Python3.X
""" 主进程，执行循环监控
"""
import time
import easytrader
import datetime
import os
import logging
import sys

import simplejson

today = datetime.datetime.today()
today = today.strftime("%Y-%m-%d")

logger = logging.getLogger('log')
logger.setLevel(logging.DEBUG)
root_path = "log/{}".format(today)
os.makedirs(root_path, exist_ok=True)
path = os.path.join(root_path, '{}.log'.format(os.path.basename(__file__)))

# 文件日志
fh = logging.FileHandler(path, encoding='utf-8', mode='a')
fh.setLevel(logging.INFO)
formatter = logging.Formatter(fmt='[%(asctime)s-%(filename)s-%(levelname)s]:%(message)s',
                              datefmt='%Y-%m-%d_%I:%M:%S_%p')
fh.setFormatter(formatter)
logger.addHandler(fh)

# 控制台日志
formatter = logging.Formatter('[%(levelname)s]：%(message)s')
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)

__author__ = '__L1n__w@tch'


def get_balance(client):
    """
    获取当前的资金情况
    :param client:
    :return:
    """
    logger.debug("获取当前资金情况")
    result = client.balance
    while len(result) <= 0:
        time.sleep(10)
        logger.error("资金情况获取失败：{}".format(result))
        result = client.balance

    return result


def get_position(client):
    """
    获取当前的持仓情况
    :param client:
    :return:
    """
    logger.debug("获取当前持仓情况")
    try:
        result = client.position
    except Exception as e:
        logger.error("API 调用失败，无法获取当前持仓情况：{}".format(e))
    while len(result) <= 0:
        logger.error("持仓情况获取失败：{}".format(result))
        login_system()
        time.sleep(10)
        result = client.position
    return result


def set_sell_cmd(client, code, price, *, amount=100, stock_info=None):
    """
    设置卖出委托
    :return:
    """
    sell_top_price = round(stock_info["当前价"] * 1.1, 2)
    if sell_top_price < price:
        logger.error("股票：{}，期望卖出价格{}超出当天最高价{}，无法交易".format(code, price, sell_top_price))
    else:
        response = client.sell(code, price=price, amount=100)
        logger.warning("股票：{}，以期望卖出价格{}进行了委托".format(code, price))
        return response


def set_buy_cmd(client, code, price, *, amount=100, stock_info=None, count_info=None):
    """
    设置买入委托
    :param client:
    :param code:
    :param price:
    :param amount:
    :return:
    """
    total_cost = price * amount

    if total_cost >= count_info["可用金额"]:
        logger.error("股票：{}，期望买入价格{}，总共需要{}超出目前可用余额{}，无法交易".format(code, price, total_cost, count_info["可用金额"]))
    else:
        response = client.buy(code, price=price, amount=100)
        logger.warning("股票：{}，以期望买入价格{}进行了委托，总共消耗金额{}".format(code, price, total_cost))
        return response


def auto_market(client):
    """
    自动交易
    :return:
    """
    # 获取当天的决策信息
    logger.info("获取日期 {} 的决策信息".format(today))
    final_answer_path = os.path.join(root_path, "final_answer.json")
    if not os.path.exists(final_answer_path):
        import decision
        decision.get_decision()
    with open(final_answer_path, "r") as f:
        final_answer = simplejson.load(f)

    # 观察目前的情况
    balance = get_balance(client)
    logger.warning("日期 {} 的资金情况为：{}".format(today, balance))
    position = get_position(client)
    logger.warning("日期 {} 的持仓情况为：{}".format(today, position))

    logger.warning("所有股票以成本价 * 1.03 卖出，并检查是否已买了决策里的股票")
    done_final_answer = False
    for each_keep in position:
        if each_keep["证券代码"] == final_answer["code"]:
            done_final_answer = True
        sell_price = round(each_keep["参考成本价"] * 1.03, 2)
        logger.warning("股票代码：{}，按照成本价：{} 乘以 1.03 后得到的价格委托卖出：{}".format(
            each_keep["证券代码"], each_keep["参考成本价"], sell_price))
        set_sell_cmd(client, each_keep["证券代码"], sell_price, stock_info=each_keep)
    if not done_final_answer:
        logger.warning("按照决策，委托以 {} 的价格购买股票：{}".format(final_answer["buy"], final_answer["code"]))
        set_buy_cmd(client, final_answer["code"], final_answer["buy"], count_info=balance)
    # print(user.today_trades)
    # print(user.today_entrusts)


def login_system():
    """
    登录同花顺交易系统
    :return:
    """
    logger.debug("开始登录系统")

    user = easytrader.use('ths')
    user.connect(r'C:\Software\同花顺\xiadan.exe')
    user.refresh()
    user.enable_type_keys_for_editor()
    try:
        logger.info("尝试一键打新")
        user.auto_ipo()
        logger.warning("一键打新成功")
    except Exception as e:
        logger.info("一键打新失败：{}".format(e))

    return user


def main_loop():
    """
    无限循环
    1、已有持仓的（除航天信息外），则按买入价格 X，X*1.03 卖出 or x*0.8卖出
    2、没有买的，调用 decision.py，获取 final_answer.json，然后按其中的价格买入
    :return:
    """
    logger.warning("{sep} 登录系统 {sep}".format(sep="=" * 30))
    client = login_system()

    logger.warning("{sep} 开始后台监控，无限循环 {sep}".format(sep="=" * 30))
    while True:
        logger.info("{sep} 开始新的一轮监控 {sep}".format(sep="=" * 30))
        auto_market(client)
        time.sleep(10)


if __name__ == "__main__":
    main_loop()
