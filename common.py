#!/venv/env python3
# -*- coding: utf-8 -*-
# version: Python3.X
""" 各种辅助函数
"""
import datetime
import logging
import os
import re
import smtplib
import sys
from email.header import Header
from email.mime.text import MIMEText

import simplejson


def send_result_using_email():
    """
    把结果通过邮件发出来
    :param pic_path:
    :return:
    """
    today = get_today()
    sender = 'watch@watch0.top'
    receivers = ['490772448@qq.com', "watch@watch0.top"]

    with open("README.md", "r", encoding="utf8") as f:
        message_content = re.findall("【history_start】([\s\S]*)【history_end】", f.read())[0]

    message = MIMEText(message_content, 'plain', 'utf-8')
    message['From'] = Header(sender, 'utf-8')
    message['To'] = Header(",".join(receivers), 'utf-8')
    subject = '【auto_market】{} 交易结果'.format(today)
    message['Subject'] = Header(subject, 'utf-8')

    with open("information.json", "r") as f:
        data = simplejson.load(f)

    with smtplib.SMTP_SSL("hwsmtp.exmail.qq.com", 465) as server:
        server.set_debuglevel(1)
        server.login(data["account"], data["password"])
        server.sendmail(sender, receivers, message.as_string())


def get_root_log_path():
    today = get_today()
    root_path = "../temp_auto_market_log/{}".format(today)
    os.makedirs(root_path, exist_ok=True)
    return root_path


def get_today():
    today = datetime.datetime.today()
    today = today.strftime("%Y-%m-%d")
    return today


def get_logger(logger, old_root_path):
    root_path = get_root_log_path()
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


def analysis_trades_log():
    """
    分析交易记录，生成 readme.md 中的战绩表格
    :return:
    """
    history = list()
    with open("log/trades_log.json", "r", encoding="utf8") as f:
        data = simplejson.load(f)
    trade_index = dict()
    for each_day_trades in data["trades"]:
        trade_date = each_day_trades.pop(0)
        trade_date_code = list()
        for each_trade in each_day_trades:
            if "证券代码" not in each_trade or (each_trade.get("备注") == "未成交"):
                continue
            code = each_trade["证券代码"]
            if code in trade_date_code:
                continue
            else:
                trade_date_code.append(code)

            if code not in trade_index.keys():
                trade_index[each_trade["证券代码"]] = len(history)
                history.append({"股票代码": each_trade["证券代码"], "股票名称": each_trade["证券名称"], "序号": len(history) + 1})
                if each_trade["操作"] == "证券买入":
                    history[trade_index[each_trade["证券代码"]]].update(
                        {"买入日期": [trade_date], "买入价格": [each_trade["成交均价"]]})
                elif each_trade["操作"] == "证券卖出":
                    history[trade_index[each_trade["证券代码"]]].update(
                        {"卖出日期": trade_date, "卖出价格": each_trade["成交均价"]})
            elif each_trade["操作"] == "证券买入":
                index = trade_index[each_trade["证券代码"]]
                history[index]["买入日期"].append(trade_date)
                history[index]["买入价格"].append(each_trade["成交均价"])
            elif each_trade["操作"] == "证券卖出":
                index = trade_index[each_trade["证券代码"]]
                keep_date_end = datetime.datetime.strptime(trade_date, "%Y-%m-%d")
                keep_date_start = datetime.datetime.strptime(history[index]["买入日期"][0], "%Y-%m-%d")
                keep_date = str((keep_date_end - keep_date_start).days)
                update_dict = {"卖出日期": trade_date, "卖出价格": each_trade["成交均价"],
                               "持有天数": keep_date}
                history[index].update(update_dict)
                del trade_index[each_trade["证券代码"]]

    return [data["update_time"], history]


def generate_md_content(history_content):
    result = """【history_start】

最近一次更新日期为：{}

| 序号 | 股票代码 | 股票名称 | 买入日期 | 买入价格 | 卖出日期 | 卖出价格 | 持有天数 |
| --- | --- | --- | --- | --- | --- | --- | --- |
{}

【history_end】"""
    update_date = history_content[0]
    history_table = str()
    for each_trade in history_content[1]:
        trade_data = list()
        for each_field in ["序号", "股票代码", "股票名称", "买入日期", "买入价格", "卖出日期", "卖出价格", "持有天数"]:
            trade_data.append(str(each_trade.get(each_field, "?")))

        content = "|".join(trade_data)
        history_table += "|" + content + "|\n"
    return result.format(update_date, history_table)


def update_readme_history():
    """
    更新 readme.md 中的战绩内容
    :return:
    """
    analysis_result = analysis_trades_log()
    with open("README.md", "r", encoding="utf8") as f:
        data = f.read()
    update_data = generate_md_content(analysis_result)
    result = re.sub("【history_start】([\s\S]+)【history_end】", update_data, data)
    with open("README.md", "w", encoding="utf8") as f:
        f.write(result)
