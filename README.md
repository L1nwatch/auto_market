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

最近一次更新日期为：2021-10-19 20:30:15.323493

总体情况为：目前共交易过 63 只股票，其中 51 只已卖出，平均持有 23 天，平均价格差为 0.97%，详见下表：

| 序号 | 股票代码 | 股票名称 | 买入日期 | 买入价格 | 卖出日期 | 卖出价格 | 持有天数 | 价格比 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
|1|000518|四环生物|['2021-03-29']|[4.07]|2021-04-26|4.36|28|7.13%|
|2|603535|嘉诚国际|['2021-04-06', '2021-04-09']|[30.69, 30.6]|2021-04-27|31.62|21|3.18%|
|3|000728|国元证券|['2021-04-19', '2021-04-20', '2021-04-21']|[7.66, 7.75, 7.75]|2021-05-14|8.0|25|3.63%|
|4|000525|红 太 阳|['2021-04-27']|[4.76]|2021-06-04|4.02|38|-15.55%|
|5|603322|超讯通信|['2021-04-29']|[13.92]|2021-05-18|14.36|19|3.16%|
|6|603238|诺邦股份|['2021-04-30']|[24.43]|2021-08-06|13.19|98|-46.01%|
|7|000050|深天马Ａ|['2021-05-07']|[13.62]|2021-06-18|14.17|42|4.04%|
|8|000710|贝瑞基因|['2021-05-10']|[27.12]|2021-05-13|28.04|3|3.39%|
|9|000712|锦龙股份|['2021-05-11']|[13.91]|2021-05-14|14.35|3|3.16%|
|10|000049|德赛电池|['2021-05-12']|[46.57]|2021-07-07|47.99|56|3.05%|
|11|000589|贵州轮胎|['2021-05-17', '2021-05-21', '2021-05-25']|[6.22, 5.93, 6.02]|2021-07-02|6.11|46|0.88%|
|12|603161|科华控股|['2021-05-18', '2021-05-27']|[14.57, 14.39]|2021-06-08|14.88|21|2.76%|
|13|000526|学大教育|['2021-05-19', '2021-05-24']|[31.17, 30.05]|2021-06-01|31.55|13|3.07%|
|14|603377|东方时尚|['2021-05-20']|[9.9]|2021-05-21|10.22|1|3.23%|
|15|000732|泰禾集团|['2021-05-26']|[2.52]|2021-05-27|2.62|1|3.97%|
|16|000403|派林生物|['2021-06-02']|[35.16]|2021-06-28|31.0|26|-11.83%|
|17|000401|冀东水泥|['2021-06-03', '2021-06-04', '2021-06-07', '2021-07-13']|[13.37, 13.38, 13.04, 12.02]|2021-09-01|13.37|90|3.22%|
|18|000157|中联重科|['2021-06-09', '2021-06-11', '2021-06-16']|[10.07, 9.9, 9.39]|2021-07-27|7.74|48|-20.91%|
|19|600488|天药股份|['2021-06-10']|[4.66]|?|?|?|?|
|20|000518|四环生物|['2021-06-15', '2021-07-08']|[3.85, 3.55]|?|?|?|?|
|21|000581|威孚高科|['2021-06-21', '2021-07-07']|[21.59, 20.47]|2021-08-09|21.69|49|3.14%|
|22|000046|泛海控股|['2021-06-29']|[2.41]|2021-07-28|1.98|29|-17.84%|
|23|000416|民生控股|['2021-06-30', '2021-07-02']|[3.99, 3.89]|2021-07-06|4.08|6|3.55%|
|24|600800|渤海化学|['2021-07-01']|[4.33]|2021-07-13|4.49|12|3.70%|
|25|000607|华媒控股|['2021-07-05']|[3.56]|2021-08-23|3.69|49|3.65%|
|26|000096|广聚能源|['2021-07-09']|[9.11]|2021-07-14|9.41|5|3.29%|
|27|000042|中洲控股|['2021-07-12']|[8.12]|?|?|?|?|
|28|603377|东方时尚|['2021-07-14']|[9.2]|2021-07-15|9.5|1|3.26%|
|29|000166|申万宏源|['2021-07-15']|[4.45]|2021-07-23|4.51|8|1.35%|
|30|002022|科华生物|['2021-07-16']|[14.08]|2021-08-03|14.53|18|3.20%|
|31|000543|皖能电力|['2021-07-19']|[3.63]|2021-08-17|3.76|29|3.58%|
|32|000759|中百集团|['2021-07-20']|[5.03]|2021-09-14|5.21|56|3.58%|
|33|000899|赣能股份|['2021-07-21']|[4.76]|2021-08-31|4.93|41|3.57%|
|34|603898|好莱客|['2021-07-23']|[12.32]|2021-09-06|12.72|45|3.25%|
|35|000402|金 融 街|['2021-07-26']|[6.06]|2021-08-31|6.27|36|3.47%|
|36|000026|飞亚达|['2021-07-28']|[12.21]|2021-08-03|12.6|6|3.19%|
|37|000038|深大通|['2021-07-29']|[9.63]|2021-09-03|9.94|36|3.22%|
|38|000540|中天金融|['2021-07-30']|[2.25]|2021-08-02|2.34|3|4.00%|
|39|600897|厦门空港|['2021-08-02']|[15.2]|2021-08-17|15.68|15|3.16%|
|40|600377|宁沪高速|['2021-08-04']|[8.46]|2021-08-19|8.74|15|3.31%|
|41|002905|金逸影视|['2021-08-06']|[6.71]|2021-08-12|6.94|6|3.43%|
|42|000429|粤高速Ａ|['2021-08-09', '2021-08-13', '2021-08-16', '2021-08-17']|[6.67, 6.67, 6.67, 6.69]|2021-08-25|6.9|16|3.37%|
|43|002610|爱康科技|['2021-08-10']|[2.14]|2021-08-11|2.23|1|4.21%|
|44|002925|盈趣科技|['2021-08-12', '2021-08-26']|[36.4, 34.57]|?|?|?|?|
|45|000620|新华联|['2021-08-18']|[1.94]|2021-08-19|2.02|1|4.12%|
|46|603301|振德医疗|['2021-08-19']|[34.09]|2021-09-29|35.14|41|3.08%|
|47|002069|獐子岛|['2021-08-20']|[2.9]|2021-08-25|3.01|5|3.79%|
|48|000516|国际医学|['2021-08-23']|[10.76]|2021-08-24|11.13|1|3.44%|
|49|600521|华海药业|['2021-08-24']|[17.4]|2021-09-06|17.95|13|3.16%|
|50|600604|市北高新|['2021-08-31']|[5.05]|2021-09-01|5.54|1|9.70%|
|51|603355|莱克电气|['2021-09-02']|[26.4]|2021-09-07|27.22|5|3.11%|
|52|002612|朗姿股份|['2021-09-03']|[30.61]|2021-09-06|31.55|3|3.07%|
|53|002212|天融信|['2021-09-07', '2021-09-08', '2021-09-09']|[17.27, 17.0, 17.06]|2021-10-14|17.65|37|3.16%|
|54|000403|派林生物|['2021-09-13', '2021-09-13']|[28.47, 28.47]|?|?|?|?|
|55|002968|新大正|['2021-09-14']|[35.05]|2021-09-27|36.13|13|3.08%|
|56|000608|阳光股份|['2021-09-17']|[3.15]|?|?|?|?|
|57|002414|高德红外|['2021-09-28']|[24.5]|?|?|?|?|
|58|000810|创维数字|['2021-09-29']|[6.95]|2021-10-11|7.18|12|3.31%|
|59|002439|启明星辰|['2021-10-11', '2021-10-14']|[27.01, 25.87]|?|?|?|?|
|60|002250|联化科技|['2021-10-12']|[18.17]|?|?|?|?|
|61|000918|嘉凯城|['2021-10-15']|[3.18]|?|?|?|?|
|62|000038|深大通|['2021-10-18']|[8.8]|?|?|?|?|
|63|002563|森马服饰|['2021-10-19']|[7.53]|?|?|?|?|


【history_end】
    

# ToDo
* 实现自动更新 readme
* 实现每天发邮件，显示 readme 战绩内容