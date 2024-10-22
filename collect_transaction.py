
from lxml import etree
import peewee
import datetime
import requests
import asyncio
import uuid
import time
import random
import tqdm
import logging
import datetime
from multiprocessing import Queue
from decimal import *
from models import *
import h5py
import csv
import os
import get_proxy

周六 = 6
周日 = 7
csv_dir = "./transaction/"

proxies = { "http": "http://127.0.0.1:10805", "https": "http://127.0.0.1:10805"}
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'}

ips = get_proxy.ProxyPool('ip.txt')

# logging
logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)
handler = logging.FileHandler('transaction_collect.log', mode='a', encoding='utf-8')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def check_data_complete(path):
    # 读取csv至字典
    csvFile = open(path, "r", encoding="utf-8")
    reader = csv.reader(csvFile)

    # 建立空字典
    result = []
    for item in reader:
        # 忽略第一行
        if reader.line_num == 1:
            continue
        result.append(item)

    csvFile.close()

    d = datetime.datetime.strptime(result[-1][1], '%Y-%m-%d %H:%M:%S')
    if d.time() <= datetime.time(9, 30, 0):
        return True
    else:
        return False

def read_data(path):
    # 读取csv
    csvFile = open(path, "r", encoding="utf-8")
    reader = csv.reader(csvFile)

    # 建立空列表
    result = []
    for item in reader:
        # 忽略第一行
        if reader.line_num == 1:
            continue
        result.append(item)

    csvFile.close()
    return result

def is_record_in(record, data):
    for each_record in data:
        if record[0] == each_record[0] and \
            record[1].strftime('%Y-%m-%d %H:%M:%S') == each_record[1] and \
            str(record[1]) == each_record[2]:
            return True

    return False


def 取第一个元素(数组):
    返回值 = None
    if len(数组) > 0:
        返回值 = 数组[0]
    else:
        返回值 = None

    return 返回值

def kind_to_en(kind):
    if kind == '买盘':
        return 'B'
    elif kind == '卖盘':
        return 'S'
    elif kind == '中性盘':
        return 'N'
    else:
        return None


def request_get_wrapper(url, proxies_obj):
    if proxies_obj is None:
        return requests.get(url, headers=headers, timeout=15)
    else:
        return requests.get(url, proxies=proxies_obj, headers=headers, timeout=15)

def async_get(url, proxies_obj=None):
    if proxies_obj is None:
        return requests.get(url, headers=headers, timeout=15)
    else:
        return requests.get(url, proxies=proxies_obj, headers=headers, timeout=15)

def get_stock_number(stock):
    六位编号, 交易所缩写 = stock.symbol.split('.')
    新浪链接股票编号 = 交易所缩写.lower() + 六位编号
    return 新浪链接股票编号

def is_banned(page):
    # 判断封禁
    page.encoding='utf-8'
    if '拒绝访问' in page.text:
        return True
    else:
        return False

async def get_a_stock_transaction(stock):
    新浪链接股票编号 = get_stock_number(stock)

    开始日期 = stock.list_date
    结束日期 = datetime.date.today()

    if 开始日期 < datetime.date(2005, 1, 1):
        开始日期 = datetime.date(2005, 1, 1)
    
    当前日期 = 开始日期
    一天 = datetime.timedelta(days=1)
    while 当前日期 <= 结束日期:
        if 当前日期.isoweekday() in [周六, 周日]:
            当前日期 += 一天
            continue
        csv_filename = csv_dir+f'{新浪链接股票编号}+{当前日期.strftime("%Y-%m-%d")}.csv'
        if os.path.exists(csv_filename) and check_data_complete(csv_filename):
            当前日期 += 一天
            continue
        data = []
        data_complete = False

        页码 = 1
        while True:
            time.sleep(random.randint(1,2))

            链接 = f'http://market.finance.sina.com.cn/transHis.php?symbol={新浪链接股票编号}&date={当前日期.strftime("%Y-%m-%d")}&page={str(页码)}'
            页面 = None
            try:
                proxy_obj = ips.get_url()
                页面 = async_get(链接, {'http': get_proxy.get_proxy_url(proxy_obj)})
            except Exception as e:
                ips.bad_url(proxy_obj)
                logger.error('requests.exceptions.ConnectionError' + str(e))
                continue
            if 页面.status_code != 200:
                if 页面.status_code == 456:
                    # 判断封禁
                    logger.fatal('ip已被新浪封禁')
                else:
                    ips.bad_url(proxy_obj)
                    logger.error('requests.exceptions.ConnectionError with status code:' + str(页面.status_code))
                continue
            if 页面 is None:
                continue
                    
            logger.info(链接)
            页面.encoding='gb2312'
            网页语法树 = etree.HTML(页面.text)

            if 网页语法树 is None:
                logger.error('语法树解析失败')
                continue
            
            # 二次判断封禁
            if is_banned(页面):
                logger.fatal('ip已被新浪封禁')
                continue

            # 没有数据了(可能是假的)
            错误信息 = 取第一个元素(网页语法树.xpath('//div[contains(text(),"输入的代码有误或没有交易数据")]'))
            
            if 错误信息 is not None and 页码 == 1:
                data_complete = True
                break
            elif 错误信息 is not None and 页码 != 1:
                logger.warning('May be fake format error, try again later.')
                continue
            
            # 没有数据了
            数据 = 网页语法树.xpath('//table[@id="datatbl"]/tbody/tr')
            if len(数据) == 0:
                data_complete = True
                break

            for 每一行数据 in 数据:
                成交时间 = 取第一个元素(每一行数据.xpath('./th[1]/text()'))
                成交价 = 取第一个元素(每一行数据.xpath('./td[1]/text()'))
                价格变动 = 取第一个元素(每一行数据.xpath('./td[2]/text()'))
                成交量 = 取第一个元素(每一行数据.xpath('./td[3]/text()'))
                成交额 = 取第一个元素(每一行数据.xpath('./td[4]/text()'))
                性质 = 取第一个元素(每一行数据.xpath('./th[2]/*[name()="h6" or name()="h5" or name()="h1"]/text()'))

                时, 分, 秒 = 成交时间.split(':')
                成交价 = Decimal(成交价)
                if 价格变动 is None:
                    价格变动 = Decimal(0)
                elif '--' in 价格变动:
                    价格变动 = Decimal(0)
                else:
                    价格变动 = Decimal(价格变动)
                成交量 = int(成交量)
                if 成交额 is None:
                    成交额 = Decimal(0)
                else:
                    成交额 = Decimal(成交额.replace(',', ''))

                data.append((
                    新浪链接股票编号,
                    datetime.datetime(
                        当前日期.year,
                        当前日期.month,
                        当前日期.day,
                        int(时), int(分), int(秒)),
                    成交价,
                    价格变动,
                    成交量,
                    成交额,
                    kind_to_en(性质),
                ))

            页码 += 1

        if data_complete and len(data) != 0:
            with open(csv_filename,'w', newline='', encoding='utf-8') as f:
                csv_write = csv.writer(f)
                csv_head = ["stock_symbol","datetime", "price", "price_change", "volume", "turnover", "kind"]
                csv_write.writerow(csv_head)
                csv_write.writerows(data)

        当前日期 += 一天


async def main():
    for 股票 in tqdm.tqdm(iterable=Equities.select(), ascii=True):
        await get_a_stock_transaction(股票)

if __name__ == "__main__":
    asyncio.run(main())


