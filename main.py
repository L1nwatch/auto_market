#!/venv/env python3
# -*- coding: utf-8 -*-
# version: Python3.X
""" Description
"""
import time
import requests
import re
import easyquotation
import easytrader
import baostock as bs
import pandas as pd



from selenium import webdriver
from selenium.webdriver.chrome.options import Options

__author__ = '__L1n__w@tch'

browser = None

if __name__ == "__main__":

    #### 登陆系统 ####
    lg = bs.login()
    # 显示登陆返回信息
    print('login respond error_code:' + lg.error_code)
    print('login respond  error_msg:' + lg.error_msg)

    quotation = easyquotation.use('sina')  # 新浪 ['sina'] 腾讯 ['tencent', 'qq']
    result = quotation.market_snapshot(prefix=True)  # prefix 参数指定返回的行情字典中的股票代码 key 是否带 sz/sh 前缀
    for each_stock in result:
        each_stock = each_stock.replace("sz","sz.")
        each_stock = each_stock.replace("sh","sh.")
        print(each_stock)
        #### 获取公司业绩预告 ####
        rs_forecast = bs.query_forecast_report(each_stock, start_date="2021-01-01", end_date="2021-03-06")
        print('query_forecast_reprot respond error_code:' + rs_forecast.error_code)
        print('query_forecast_reprot respond  error_msg:' + rs_forecast.error_msg)
        rs_forecast_list = []
        while (rs_forecast.error_code == '0') & rs_forecast.next():
            # 分页查询，将每页信息合并在一起
            rs_forecast_list.append(rs_forecast.get_row_data())
        result_forecast = pd.DataFrame(rs_forecast_list, columns=rs_forecast.fields)
        response = result_forecast.to_dict()
        print(response)



    #### 登出系统 ####
    bs.logout()
    exit()


    user = easytrader.use('ths')
    user.connect(r'C:\Software\同花顺\xiadan.exe')
    # print(user.balance)
    # print(user.position)
    # user.auto_ipo()
    # print(user.today_trades)
    user.refresh()
    user.enable_type_keys_for_editor()

    print(quotation.stocks(['000001', '162411']))  # prefix 参数指定返回的行情字典中的股票代码 key 是否带 sz/sh 前缀)

    # response = user.buy('603367', price=10.69, amount=100)
    # print(response)

    # response = user.sell('600271', price=0.55, amount=100)
    # print(response)
    # print(user.today_entrusts)
    time.sleep(10)
