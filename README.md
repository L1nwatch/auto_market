# 背景

研究量化交易系统ing，其核心就是 策略 + 自动化交易，基于自己的实际情况，实现了【同花顺+平安证券账号】自动化买入卖出股票的代码，再结合自己写的一些简单策略，作为一个量化交易入门。

# 策略

目前还不太懂高深的交易策略，只是简单地挑选近期跌幅较大的股票，买入，成本价记为 x，每天以 `x*1.03` 价格作为止盈条件卖出，每天以 `x*0.8` 价格作为止损条件卖出。
 
# 运行说明

* 环境：Windows10 + Python3.7 + 同花顺-网上股票交易系统5.0

![同花顺-网上股票交易系统5.0](version_info.png)

* 步骤概述：
    * 打开同花顺-网上股票交易系统5.0，手动登录账号
    * 安装好依赖库后，运行 `main.py`
* 逻辑说明：死循环，直到时间段【周一~周五，早上 8:30-9:00】，跑一下策略获取出当天要买入的股票代码，执行下单操作，并按止盈止损条件，将手中可用股票全部委托交易。

# 战绩

截止目前为止，本系统的策略记录如下：


【history_start】

最近一次更新日期为：2021-05-17 20:30:16.963040

| 序号 | 股票代码 | 股票名称 | 买入日期 | 买入价格 | 卖出日期 | 卖出价格 | 持有天数 |
| --- | --- | --- | --- | --- | --- | --- | --- |
|1|603535|嘉诚国际|['2021-04-06', '2021-04-09']|[30.69, 30.6]|2021-04-27|31.62|21|
|2|000728|国元证券|['2021-04-19', '2021-04-20', '2021-04-21']|[7.66, 7.75, 7.75]|2021-05-14|8.0|25|
|3|000525|红 太 阳|['2021-04-27']|[4.76]|?|?|?|
|4|603322|超讯通信|['2021-04-29']|[13.92]|?|?|?|
|5|603238|诺邦股份|['2021-04-30']|[24.43]|?|?|?|
|6|000050|深天马Ａ|['2021-05-07']|[13.62]|?|?|?|
|7|000710|贝瑞基因|['2021-05-10']|[27.12]|2021-05-13|28.04|3|
|8|000712|锦龙股份|['2021-05-11']|[13.91]|2021-05-14|14.35|3|
|9|000049|德赛电池|['2021-05-12']|[46.57]|?|?|?|
|10|000589|贵州轮胎|['2021-05-17']|[6.22]|?|?|?|


【history_end】
    

# ToDo
* 实现自动更新 readme
* 实现每天发邮件，显示 readme 战绩内容