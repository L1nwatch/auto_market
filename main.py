#!/venv/env python3
# -*- coding: utf-8 -*-
# version: Python3.X
""" 主进程，执行循环监控
"""
import os
import time
import easytrader
import simplejson
from common import get_today, get_root_path, get_logger

__author__ = '__L1n__w@tch'

logger = None
old_root_path = None


def get_balance(client):
    """
    获取当前的资金情况
    :param client:
    :return:
    """
    global logger
    logger.debug("获取当前资金情况")
    while True:
        try:
            result = client.balance
            while len(result) <= 0:
                time.sleep(10)
                logger.error("资金情况获取失败：{}".format(result))
                result = client.balance
            return result
        except Exception as e:
            logger.error("API 调用失败，无法获取当前资金情况：{}".format(e))


def get_position(client):
    """
    获取当前的持仓情况
    :param client:
    :return:
    """
    global logger
    logger.debug("获取当前持仓情况")
    while True:
        try:
            result = client.position
            while len(result) <= 0 or "参考成本价" not in result[0]:
                logger.error("持仓情况获取失败：{}".format(result))
                login_system()
                time.sleep(10)
                result = client.position
            return result
        except Exception as e:
            logger.error("API 调用失败，无法获取当前持仓情况：{}".format(e))


def set_sell_cmd(client, code, price, *, amount=100, stock_info=None):
    """
    设置卖出委托
    :return:
    """
    global logger
    sell_top_price = round(stock_info["当前价"] * 1.1, 2)
    if sell_top_price < price:
        logger.error("股票：{}，期望卖出价格{}超出当天最高价{}，无法交易".format(code, price, sell_top_price))
    elif stock_info["可用数量"] == 0:
        logger.error("股票：{} 可用数量为 0，无法交易".format(code))
    else:
        response = client.sell(code, price=price, amount=amount)
        logger.warning("股票：{}，以期望卖出价格{}进行了委托".format(code, price))
        logger.critical("目前资产情况为：{}".format(get_balance(client)))
        logger.critical("目前持仓情况为：{}".format(get_position(client)))
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
    global logger
    # TODO: 这里写死了只买一手
    amount = 100
    total_cost = price * amount

    if total_cost >= count_info["可用金额"]:
        logger.error("股票：{}，期望买入价格{}，总共需要{}超出目前可用余额{}，无法交易".format(code, price, total_cost, count_info["可用金额"]))
    else:
        try:
            response = client.buy(code, price=price, amount=amount)
            logger.critical("股票：{}，以期望买入价格{}进行了委托，总共消耗金额{}".format(code, price, total_cost))
            logger.critical("目前资产情况为：{}".format(get_balance(client)))
            logger.critical("目前持仓情况为：{}".format(get_position(client)))
            return response
        except Exception as e:
            logger.error("无法完成购买：{}".format(e))


def get_today_entrusts(client):
    global logger
    logger.debug("获取当日委托情况")
    while True:
        try:
            result = list()
            today_entrusts = client.today_entrusts
            for each_entrust in today_entrusts:
                if each_entrust["备注"] != "全部撤单":
                    logger.info("委托：{} 全部撤单了".format(each_entrust))
                    result.append(each_entrust)
            return result
        except Exception as e:
            logger.error("API 调用失败，无法获取当前委托情况：{}".format(e))
            login_system()
            time.sleep(10)


def get_today_decision(client):
    global logger
    final_answer_path = os.path.join(get_root_path(), "final_answer.json")
    if not os.path.exists(final_answer_path):
        import decision
        decision.get_decision()
    with open(final_answer_path, "r") as f:
        final_answer = simplejson.load(f)

    balance = get_balance(client)
    logger.warning("日期 {} 的资金情况为：{}".format(get_today(), balance))
    position = get_position(client)
    logger.warning("日期 {} 的持仓情况为：{}".format(get_today(), position))
    return final_answer, position, balance


def set_sell_stop_cmd(client, position):
    """
    卖出所有需要止损的股票
    :param client:
    :return:
    """
    global logger
    # TODO：检查之前是否已设置过 1.03 止损的委托
    logger.info("观察持仓情况里，哪些需要卖出的")
    for each_keep in position:
        if each_keep["证券代码"] != "600271":
            logger.debug("跳过 航天信息 股")
            continue
        sell_price = round(each_keep["参考成本价"] * 0.8, 2)
        # if each_keep["当前价"] < sell_price:
        logger.warning("【止损】股票代码：{}，按照成本价：{} 乘以 0.8 后得到的价格委托卖出：{}".format(
            each_keep["证券代码"], each_keep["参考成本价"], sell_price))
        set_sell_cmd(client, each_keep["证券代码"], sell_price, stock_info=each_keep, amount=each_keep["可用数量"])
        # else:
        #     logger.info("股票代码：{}，止损价格为{}，目前价格{}还不需要止损".format(each_keep["证券代码"], sell_price, each_keep["当前价"]))


def set_sell_earn_cmd(client, position, final_answer):
    """
    按照预期赚钱的价格进行售出
    :param client:
    :return:
    """
    global logger
    done_final_answer = False
    has_set_buy_cmd = False

    for each_keep in position:
        if each_keep["证券代码"] == final_answer["code"].strip("szh"):
            if str(each_keep["参考成本价"]) == str(final_answer["buy"]):
                done_final_answer = True
        sell_price = round(each_keep["参考成本价"] * 1.03, 2)
        logger.warning("股票代码：{}，按照成本价：{} 乘以 1.03 后得到的价格委托卖出：{}".format(
            each_keep["证券代码"], each_keep["参考成本价"], sell_price))
        amount = each_keep["可用数量"]
        set_sell_cmd(client, each_keep["证券代码"], sell_price, stock_info=each_keep, amount=amount)

    if not done_final_answer:
        logger.info("检查是否已提交委托")
        today_entrusts = get_today_entrusts(client)
        if len(today_entrusts) > 0:
            for each_entrust in today_entrusts:
                if (each_entrust["证券代码"] == final_answer["code"].strip("szh")) \
                        and (each_entrust["操作"] == "证券买入"):
                    logger.info("已设置委托")
                    has_set_buy_cmd = True
                    break
    return done_final_answer, has_set_buy_cmd


def auto_market(client):
    """
    自动交易
    :return:
    """
    global logger
    logger.info("获取日期 {} 的决策信息".format(get_today()))

    final_answer, position, balance = get_today_decision(client)
    logger.info("所有股票以成本价 * 1.03 卖出，并检查是否已买了决策里的股票")
    done_final_answer, has_set_buy_cmd = set_sell_earn_cmd(client, position, final_answer)

    logger.info("卖出所有需要止损的股票")
    set_sell_stop_cmd(client, position)
    if not done_final_answer and not has_set_buy_cmd:
        logger.info("按照决策，委托以 {} 的价格购买股票：{}".format(final_answer["buy"], final_answer["code"]))
        amount = balance["可用金额"] // (final_answer["buy"] * 100)
        set_buy_cmd(client, final_answer["code"], final_answer["buy"], count_info=balance, amount=amount * 100)


def login_system():
    """
    登录同花顺交易系统
    :return:
    """
    global logger
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
    # TODO： 日志重复记录了
    global logger, old_root_path
    logger, old_root_path = get_logger(logger, old_root_path)
    logger.warning("{sep} 登录系统 {sep}".format(sep="=" * 30))
    client = login_system()

    logger.warning("{sep} 开始后台监控，无限循环 {sep}".format(sep="=" * 30))
    while True:
        logger, old_root_path = get_logger(logger, old_root_path)
        try:
            logger.info("{sep} 开始新的一轮监控 {sep}".format(sep="=" * 30))
            auto_market(client)
        except Exception as e:
            logger.error("{sep} 本轮存在异常：{error} {sep}".format(sep="=" * 30, error=e))
        finally:
            time.sleep(10)


if __name__ == "__main__":
    main_loop()
