#!/venv/env python3
# -*- coding: utf-8 -*-
# version: Python3.X
""" 主进程，执行循环监控
"""
import datetime
import os
import time

import easytrader
import simplejson

from common import get_today, get_root_log_path, get_logger, send_result_using_email, update_readme_history

__author__ = '__L1n__w@tch'

logger = None
old_root_path = None
trades_log_path = "log/trades_log.json"


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
    try:
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
    except Exception as e:
        logger.error("设置卖出委托失败：{}".format(e))


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
    # TODO: 这里写死了只买 n 手，因为策略还不确定有效性，一手一手地加
    amount = 200
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


def get_today_trades(client):
    global logger
    logger.debug("获取当天交易情况")
    while True:
        try:
            login_system()
            client.refresh()
            result = client.today_trades
            return result
        except Exception as e:
            logger.error("API 调用失败，无法获取当天交易情况：{}".format(e))
            login_system()
            time.sleep(10)


def get_today_decision(client):
    global logger, old_root_path
    final_answer_path = os.path.join(get_root_log_path(), "final_answer.json")
    if not os.path.exists(final_answer_path):
        import decision
        decision.get_decision(logger, old_root_path)
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
        if each_keep["可用数量"] == 0:
            logger.debug("股:{}，可用数量为0".format(each_keep["证券代码"]))
            continue
        if each_keep["证券代码"] == "600271":
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
                logger.info("已完成决策股票的购买")
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
    logger.info("决策股票的购买情况：{} 和委托情况：{}".format(done_final_answer, has_set_buy_cmd))

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


def is_right_commission_time():
    """
    判断是否为合适的委托时间，一天就运行一个时间段：周一~周五，早上 8:30-9:00
    """
    now = datetime.datetime.today()
    # 周一到周五
    if not (1 <= now.isoweekday() <= 5):
        return False
    # 小时 && 分钟
    if now.hour == 8 and 30 <= now.minute <= 59:
        return True
    return False


def is_right_update_history_time():
    """
    Old-before-2021-05-16: 判断是否为合适的分析时间，一天就运行一个时间段：周一~周五，晚上 8:30-9:00
    判断是否为合适的分析时间，一天就运行一个时间段：每天晚上 8:30-9:00
    :return:
    """
    now = datetime.datetime.today()
    # 周一到周五
    # if not (1 <= now.isoweekday() <= 5):
    #     return False
    # 小时 && 分钟
    if now.hour == 20 and 30 <= now.minute <= 59:
        return True
    return False


def push_to_github():
    """
    将更新内容上传到 github 上
    :return:
    """
    git_path = os.path.abspath(os.path.dirname(__file__))
    # os.system("cd {} && git add log/trades_log.json".format(git_path))
    os.system("cd {} && git add README.md".format(git_path))
    os.system('cd {} && git commit -m "{} update readme.md "'.format(git_path, get_today()))
    os.system('cd {} && git push'.format(git_path))


def update_trades_log(client):
    global trades_log_path
    # 保存当天的交易情况
    today_trades_info = get_today_trades(client)
    logger.info("获取当天的交易情况：{}".format(today_trades_info))

    with open(trades_log_path, "r", encoding="utf8") as f:
        total_trades_info = simplejson.load(f, encoding="utf8")
    total_trades_info["update_time"] = str(datetime.datetime.today())
    if len(today_trades_info) > 0:
        today_trades_info.insert(0, get_today())
        total_trades_info["trades"].append(today_trades_info)
    with open(trades_log_path, "w", encoding="utf8") as f:
        simplejson.dump(total_trades_info, f, ensure_ascii=False)
    logger.info("已将当天的交易情况，更新到 trades_log.json 文件当中".format(today_trades_info))


def update_history_content(client):
    """
    获取当天的交易情况，并更新 readme
    :return:
    """
    update_trades_log(client)
    update_readme_history()


def main_loop():
    """
    无限循环
    1、已有持仓的（除航天信息外），则按买入价格 X，X*1.03 卖出 or x*0.8卖出
    2、没有买的，调用 decision.py，获取 final_answer.json，然后按其中的价格买入
    :return:
    """
    global logger, old_root_path
    logger, old_root_path = get_logger(logger, old_root_path)
    logger.warning("{sep} 登录系统 {sep}".format(sep="=" * 30))
    client = login_system()

    logger.warning("{sep} 开始后台监控，无限循环 {sep}".format(sep="=" * 30))
    while True:
        if is_right_commission_time():
            if os.path.exists("send_mail.lock"):
                os.remove("send_mail.lock")
            logger, old_root_path = get_logger(logger, old_root_path)
            try:
                logger.info("{sep} 开始新的一轮监控 {sep}".format(sep="=" * 30))
                auto_market(client)
            except Exception as e:
                logger.error("{sep} 本轮存在异常：{error} {sep}".format(sep="=" * 30, error=e))
            finally:
                time.sleep(10)
        elif is_right_update_history_time() and not os.path.exists("send_mail.lock"):
            logger.info("已到了指定的分析时间，开始分析当天的交易情况")
            logger, old_root_path = get_logger(logger, old_root_path)
            try:
                update_history_content(client)
                logger.info("分析完毕，已更新 README.md 以及 trades_log.json")
                push_to_github()
                logger.info("已将结果上传到 GitHub 上")
                send_result_using_email()
                logger.info("已将结果用邮件发送周知")
                with open("send_mail.lock", "w") as f:
                    logger.info("当天的分析已完成，创建 lock 锁")
                    pass
            except Exception as e:
                logger.error("{sep} 记录异常：{error} {sep}".format(sep="=" * 30, error=e))
            finally:
                time.sleep(60 * 5)
        else:
            logger.info("{sep} 还未到指定时间 {sep}".format(sep="=" * 30))
            time.sleep(60 * 5)
            continue


if __name__ == "__main__":
    main_loop()
