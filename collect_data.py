import baostock as bs
import pandas as pd
import tqdm
import uuid
import datetime
from models import *

def get_day_history(name):
    #### 获取沪深A股历史K线数据 ####
    # 详细指标参数，参见“历史行情指标参数”章节；“分钟线”参数与“日线”参数不同。
    # 分钟线指标：date,time,code,open,high,low,close,volume,amount,adjustflag
    rs = bs.query_history_k_data_plus(name,
        "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,peTTM,pbMRQ,psTTM,pcfNcfTTM,isST",
        start_date='2006-01-01', end_date=None,
        frequency="d", adjustflag="3")
    if rs.error_code != '0' or rs.error_msg != 'success':
        print('query_history_k_data_plus respond error_code:'+rs.error_code)
        print('query_history_k_data_plus respond error_msg:'+rs.error_msg)
        return None

    #### 打印结果集 ####
    data_list = []
    while (rs.error_code == '0') & rs.next():
        # 获取一条记录，将记录合并在一起
        data_list.append(rs.get_row_data())
    result = pd.DataFrame(data_list, columns=rs.fields)
    return result

def get_stock_number(stock):
    六位编号, 交易所缩写 = stock.symbol.split('.')
    证券宝股票编号 = 交易所缩写.lower()+ '.' + 六位编号
    return 证券宝股票编号

if __name__ == "__main__":
    db.connect()
    
    #### 登陆系统 ####
    lg = bs.login()
    # 显示登陆返回信息
    print('login respond error_code:'+lg.error_code)
    print('login respond error_msg:'+lg.error_msg)

    for stock in tqdm.tqdm(iterable=Equities.select(), ascii=True):
        data = get_day_history(get_stock_number(stock))
        if data is None:
            continue
        for index, row in data.iterrows():
            KDataDay.get_or_create(
                date = datetime.datetime.strptime(row['date'], '%Y-%m-%d'),
                equity = stock,
                defaults={
                    'uuid': uuid.uuid4(),
                    'open_price': row['open'],
                    'high_price': row['high'],
                    'low_price': row['low'],
                    'close_price': row['close'],
                    'preclose_price': row['preclose'],
                    'volume': row['volume'],
                    'amount': row['amount'],
                    'adjustflag': 3,
                    'turn': row['turn'],
                    'tradestatus': row['tradestatus'],
                    'pctChg': row['pctChg'],
                    'peTTM': row['peTTM'],
                    'pbMRQ': row['pbMRQ'],
                    'psTTM': row['psTTM'],
                    'pcfNcfTTM': row['pcfNcfTTM'],
                    'isST': row['isST'],
                }
            )

    #### 登出系统 ####
    bs.logout()