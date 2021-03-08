#!/bin/env python3
# -*- coding: utf-8 -*-
# version: Python3.X
""" 做出股票相关的决策
"""
import easyquotation
import baostock as bs
import pandas as pd
import simplejson
import datetime
import tushare
import logging
import sys
import os

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


def prepare():
    """
    相关依赖的准备
    :return:
    """
    lg = bs.login()
    return lg


def get_market_snapshot():
    result = list()
    quotation = easyquotation.use('sina')  # 新浪 ['sina'] 腾讯 ['tencent', 'qq']
    logger.info("过滤创业板代码")

    for each_stock in quotation.market_snapshot(prefix=True):
        if each_stock.startswith("sz300"):
            logger.debug("跳过创业板股票代码：{}".format(each_stock))
            continue
        stock_info = quotation.real(each_stock, prefix=True)
        if "ST" in stock_info[each_stock]["name"].upper():
            logger.debug("跳过ST股票：{}".format(stock_info[each_stock]))
            continue
        result.append(each_stock)
    logger.info("总共得到 {} 个股票代码".format(len(result)))
    return result


def get_report(stock_number):
    """
    获取单只股票的公告信息
    :param stock_number: sz000001
    :return:
    """
    stock_number = stock_number.replace("sz", "sz.")
    stock_number = stock_number.replace("sh", "sh.")
    #### 获取公司业绩预告 ####
    end_date = datetime.datetime.today()
    start_date = datetime.datetime.today() - datetime.timedelta(days=31 * 3)
    end_date = end_date.strftime("%Y-%m-%d")
    start_date = start_date.strftime("%Y-%m-%d")
    rs_forecast = bs.query_forecast_report(stock_number, start_date=start_date, end_date=end_date)
    rs_forecast.get_row_data()
    rs_forecast_list = []
    while (rs_forecast.error_code == '0') & rs_forecast.next():
        # 分页查询，将每页信息合并在一起
        rs_forecast_list.append(rs_forecast.get_row_data())
    result_forecast = pd.DataFrame(rs_forecast_list, columns=rs_forecast.fields)
    result = result_forecast.to_dict()
    logger.debug("股票：{}，近期的公告为：{}".format(stock_number, result))
    return result


def get_stock_number_with_condition():
    """
    通过分析公告情况，获取合适的股票代码
    通过分析股票的价格，得出决策
    :param lq:
    :param quotation:
    :return:
    """
    logger.info("获取所有股票的代码")
    result = get_market_snapshot()
    result_list = list()
    report_list = list()
    for i, each_stock in enumerate(result):
        if (i + 1) % 100 == 0:
            logger.debug("统计到第 {} 只股票".format(i))
        logger.debug("获取股票代码：{} 近期的公告信息".format(each_stock))
        report = get_report(each_stock)
        if len(report["code"]) <= 0:
            logger.debug("股票代码：{} 近期没有公告".format(each_stock))
            continue
        report_list.append(report)
        result_list.append(each_stock)
    logger.info("总共 {} 只股票，筛选出 {} 只股票".format(i, len(result_list)))
    with open(os.path.join(root_path, "report.json"), "w", encoding="utf8") as f:
        simplejson.dump(report_list, f, ensure_ascii=False)
    with open(os.path.join(root_path, "result.json"), "w", encoding="utf8") as f:
        simplejson.dump(result_list, f, ensure_ascii=False)
    return result_list


def get_price_info_with_stock_number(stock_list):
    """
    根据股票代码，获取最近的最高最低价格
    :param stock_list:
    :return:
    """
    result = list()
    for i, each_stock in enumerate(stock_list):
        data = tushare.get_hist_data(each_stock)
        high_price = data.iloc[:100].loc[:, "high"].max()
        low_price = data.iloc[:100].loc[:, "low"].min()
        cur_price = data.iloc[0, 2]
        sep_low = (cur_price - low_price) * 1.0 / low_price
        sep_high = (high_price - cur_price) * 1.0 / cur_price
        result.append({"high": high_price, "low": low_price, "current": cur_price, "sep_low": sep_low,
                       "sep_high": sep_high, "code": each_stock})
        logger.info("股票代码: {}, 离最低点差值: {:.2%}, 离最高点差值: {:.2%}, 当前价格: {}, 最低价格: {}, 最高价格: {}"
                    .format(each_stock, sep_low, sep_high, cur_price, low_price, high_price))
    result = sorted(result, key=lambda x: float(x["sep_low"]))
    with open(os.path.join(root_path, "low_result.json"), "w", encoding="utf8") as f:
        simplejson.dump(result, f)
    return result


def get_final_answer(newest_price_info):
    """
    获取最终决策信息
    :param newest_price_info:
    :return:
    """
    stock = newest_price_info[0]
    answer = {
        "buy": round(stock["current"], 2),
        "buy_range": (round(stock["current"] * 0.99, 2), round(stock["current"] * 1.01, 2)),  # 购买价格（当前价格±1%）
        "sell": round(stock["current"] * 1.03, 2),  # 卖出价格，买入价格 * 1.03 就可以考虑卖出了
        # 止盈价格，min(最高价格 * 0.8 or 当前价格 * 1.4)
        "stop_earn": round(min(stock["high"] * 0.8, stock["current"] * 1.4), 2),
        # 止损价格，max(最低价格 or 当前价格 * 0.7）
        "stop_lose": round(max(stock["low"], stock["current"] * 0.7), 2),
    }
    answer.update(stock)

    return answer


def get_decision():
    """
    获取要购买哪些股票，买多少等相关决策信息
    :return:
    """

    # 准备工作
    lq = prepare()

    logger.critical("{sep} 获取所有近期有公告的股票代码 {sep}".format(sep="=" * 30))
    all_code = get_stock_number_with_condition()
    with open(os.path.join(root_path, "result.json"), "r", encoding="utf8") as f:
        all_code = simplejson.load(f)

    logger.critical("{sep} 获取股票代码对应的，近期的最高最低价格 {sep}".format(sep="=" * 30))
    all_price = get_price_info_with_stock_number(all_code)

    logger.critical("{sep} 得出最终的决策 {sep}".format(sep="=" * 30))
    with open(os.path.join(root_path, "low_result.json"), "r", encoding="utf8") as f:
        all_price = simplejson.load(f)
    final_answer = get_final_answer(all_price)
    message = "推荐股票/买价/卖价：{}/{}/{}".format(final_answer["code"], final_answer["buy"], final_answer["sell"])
    logger.critical("{sep} {message} {sep}".format(sep="=" * 30, message=message))
    logger.critical("全部信息：{message}".format(sep="=" * 30, message=final_answer))
    with open(os.path.join(root_path, "final_answer.json"), mode="w", encoding="utf8") as f:
        simplejson.dump(final_answer, f)

    # 收尾工作
    bs.logout()


if __name__ == "__main__":
    get_decision()
