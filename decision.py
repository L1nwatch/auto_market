#!/bin/env python3
# -*- coding: utf-8 -*-
# version: Python3.X
""" 做出股票相关的决策
"""
import datetime
import os

import baostock as bs
import easyquotation
import simplejson
import tushare

from common import get_logger, get_root_log_path, get_today

__author__ = '__L1n__w@tch'


def prepare():
    """
    相关依赖的准备
    :return:
    """
    lg = bs.login()
    return lg


def get_market_snapshot(logger):
    result = list()
    quotation = easyquotation.use('sina')  # 新浪 ['sina'] 腾讯 ['tencent', 'qq']
    logger.info("过滤创业板代码")
    stock_list = list()
    for each_stock in quotation.market_snapshot(prefix=True):
        if each_stock.startswith("sz300"):
            logger.debug("跳过创业板股票代码：{}".format(each_stock))
            continue
        stock_list.append(each_stock)

    stock_info = quotation.real(stock_list, prefix=True)
    for each_stock_code, each_stock_info in stock_info.items():
        if "ST" in each_stock_info["name"].upper():
            logger.debug("跳过ST股票：{}".format(each_stock_info))
            continue
        if "退市" in each_stock_info["name"]:
            logger.debug("跳过退市股票：{}".format(each_stock_info))
            continue
        if each_stock_info["now"] > 48:
            logger.debug("跳过价格超过 48 的股票：{}".format(each_stock_info))
            continue
        result.append(each_stock_code)
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
    # rs_forecast_list = []
    # while (rs_forecast.error_code == '0') & rs_forecast.next():
    #     分页查询，将每页信息合并在一起
    # rs_forecast_list.append(rs_forecast.get_row_data())
    # result_forecast = pd.DataFrame(rs_forecast_list, columns=rs_forecast.fields)
    # result = result_forecast.to_dict()
    # logger.debug("股票：{}，近期的公告为：{}".format(stock_number, result))
    # return result
    if len(rs_forecast.get_row_data()) > 0:
        return True
    else:
        return False


def get_stock_number_with_condition(logger):
    """
    通过分析公告情况，获取合适的股票代码
    通过分析股票的价格，得出决策
    :param lq:
    :param quotation:
    :return:
    """
    logger.info("获取所有股票的代码")
    result = get_market_snapshot(logger)
    result_list = list()
    report_list = list()
    for i, each_stock in enumerate(result):
        if (i + 1) % 100 == 0:
            logger.debug("统计到第 {} 只股票".format(i))
        logger.debug("获取股票代码：{} 近期的公告信息".format(each_stock))
        report = get_report(each_stock)
        if not report:
            logger.debug("股票代码：{} 近期没有公告".format(each_stock))
            continue
        report_list.append(report)
        result_list.append(each_stock)
    logger.info("总共 {} 只股票，筛选出 {} 只股票".format(i, len(result_list)))
    with open(os.path.join(get_root_log_path(), "report.json"), "w", encoding="utf8") as f:
        simplejson.dump(report_list, f, ensure_ascii=False)
    with open(os.path.join(get_root_log_path(), "result.json"), "w", encoding="utf8") as f:
        simplejson.dump(result_list, f, ensure_ascii=False)
    return result_list


def get_price_info_with_stock_number(stock_list, logger):
    """
    根据股票代码，获取最近的最高最低价格
    :param stock_list:
    :return:
    """
    result = list()
    for i, each_stock in enumerate(stock_list):
        logger.debug("获取股票代码：{} 近期的价格信息".format(each_stock))
        try:
            data = tushare.get_hist_data(each_stock)
        except Exception as e:
            logger.error("股票代码：{} 获取失败，直接跳过了".format(each_stock))
            continue
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
    with open(os.path.join(get_root_log_path(), "low_result.json"), "w", encoding="utf8") as f:
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


def get_decision(logger=None,old_root_path=None):
    """
    获取要购买哪些股票，买多少等相关决策信息
    :return:
    """
    if not logger or not old_root_path:
        logger, old_root_path = get_logger(logger, old_root_path)

    # 准备工作
    lq = prepare()

    logger.info("{sep} 获取所有近期有公告的股票代码 {sep}".format(sep="=" * 30))
    all_code = get_stock_number_with_condition(logger)
    with open(os.path.join(get_root_log_path(), "result.json"), "r", encoding="utf8") as f:
        all_code = simplejson.load(f)

    logger.info("{sep} 获取股票代码对应的，近期的最高最低价格 {sep}".format(sep="=" * 30))
    all_price = get_price_info_with_stock_number(all_code, logger)

    logger.info("{sep} 得出最终的决策 {sep}".format(sep="=" * 30))
    with open(os.path.join(get_root_log_path(), "low_result.json"), "r", encoding="utf8") as f:
        all_price = simplejson.load(f)
    final_answer = get_final_answer(all_price)
    message = "推荐股票/买价/卖价：{}/{}/{}".format(final_answer["code"], final_answer["buy"], final_answer["sell"])
    logger.critical("{sep} 今天的日期为：{today_date} {sep}".format(sep="=" * 30, today_date=get_today()))
    logger.critical("{sep} {message} {sep}".format(sep="=" * 30, message=message))
    logger.critical("全部信息：{message}".format(sep="=" * 30, message=final_answer))
    with open(os.path.join(get_root_log_path(), "final_answer.json"), mode="w", encoding="utf8") as f:
        simplejson.dump(final_answer, f)

    # 收尾工作
    # bs.logout()


if __name__ == "__main__":
    get_decision()
