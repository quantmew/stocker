
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
from multiprocessing import Queue
from decimal import *
from models import *
import h5py
import csv
import os

周六 = 6
周日 = 7
csv_dir = "./transaction/"
obj_list = Queue()

proxies = { "http": "http://127.0.0.1:10805", "https": "http://127.0.0.1:10805"}
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'}

# logging
logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)
handler = logging.FileHandler('transaction_collect.log', mode='a', encoding='utf-8')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def 取第一个元素(数组):
    返回值 = None
    if len(数组) > 0:
        返回值 = 数组[0]
    else:
        返回值 = None

    return 返回值


def request_get_wrapper(url):
    return requests.get(url, proxies=proxies, headers=headers, timeout=15)

async def async_get(url):
    loop = asyncio.get_running_loop()

    future = loop.run_in_executor(
        None,
        request_get_wrapper,
        url)
    response = await future

    return response

def get_stock_number(stock):
    六位编号, 交易所缩写 = stock.symbol.split('.')
    新浪链接股票编号 = 交易所缩写.lower() + 六位编号
    return 新浪链接股票编号

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
        csv_filename = csv_dir+f'{新浪链接股票编号}+{当前日期.strftime("%y-%m-%d")}.csv'
        if os.path.exists(csv_filename):
            当前日期 += 一天
            continue
        data = []

        页码 = 1
        while True:
            链接 = f'http://market.finance.sina.com.cn/transHis.php?symbol={新浪链接股票编号}&date={当前日期.strftime("%Y-%m-%d")}&page={str(页码)}'
            页面 = None
            try:
                页面 = await async_get(链接)
            except Exception as e:
                logger.error('requests.exceptions.ConnectionError' + str(e))
                break
            if 页面 is None:
                break
                    
            logger.info(链接)
            页面.encoding='gb2312'
            网页语法树 = etree.HTML(页面.text)

            if 网页语法树 is None:
                logger.error('语法树解析失败')

                # 判断封禁
                页面.encoding='utf-8'
                if '拒绝访问' in 页面.text:
                    logger.fatal('ip已被新浪封禁')
                break

            # 真的没有数据了
            错误信息 = 取第一个元素(网页语法树.xpath('//div[contains(text(),"输入的代码有误或没有交易数据")]'))
            
            if 错误信息 is not None:
                break
            
            # 没有数据了
            数据 = 网页语法树.xpath('//table[@id="datatbl"]/tbody/tr')
            if len(数据) == 0:
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
                    性质,
                ))

            页码 += 1

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


