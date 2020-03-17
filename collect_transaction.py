
from lxml import etree
import peewee
import datetime
import requests
import asyncio
import uuid
import time
import random
import tqdm
from multiprocessing import Queue
from decimal import *
from models import *

周六 = 6
周日 = 7
obj_list = Queue()

proxies = { "http": "http://127.0.0.1:10805", "https": "http://127.0.0.1:10805"}
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'}

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


async def get_stock_history_date(obj_list, req):
    股票 = req[0]
    当前日期 = req[1]
    页码 = req[2]
    新浪链接股票编号 = get_stock_number(股票)
    链接 = f'http://market.finance.sina.com.cn/transHis.php?symbol={新浪链接股票编号}&date={当前日期.strftime("%Y-%m-%d")}&page={str(页码)}'
    
    页面 = None
    try:
        页面 = await async_get(链接)
    except Exception as e:
        print('requests.exceptions.ConnectionError' + str(e))
        obj_list.put(req)
        return

    if 页面 is None:
        obj_list.put(req)
        return
    print(链接)
    页面.encoding='gb2312'
    网页语法树 = etree.HTML(页面.text)

    if 网页语法树 is None:
        obj_list.put(req)
        print('语法树解析失败')

        # 判断封禁
        页面.encoding='utf-8'
        网页语法树 = etree.HTML(页面.text)

        if 网页语法树 is None:
            return

        拒绝访问 = 取第一个元素(网页语法树.xpath('//h1[text()="拒绝访问"]'))

        if 拒绝访问 is not None:
            print('ip已被新浪封禁')

        return

    错误信息 = 取第一个元素(网页语法树.xpath('//div[contains(text(),"输入的代码有误或没有交易数据")]'))
    
    if 错误信息 is not None:
        return

    数据 = 网页语法树.xpath('//table[@id="datatbl"]/tbody/tr')
    if len(数据) == 0:
        return

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
        成交额 = Decimal(成交额.replace(',', ''))

        交易对象, 是否创建 = Transaction.get_or_create(
            equity = 股票,
            time = datetime.datetime(
                当前日期.year,
                当前日期.month,
                当前日期.day,
                int(时), int(分), int(秒)),
            defaults = {
                'uuid': uuid.uuid4(),
                'price': 成交价,
                'price_change': 价格变动,
                'volume': 成交量,
                'turnover': 成交额,
                'kind': 性质,
            }
        )

    obj_list.put((股票, 当前日期, 页码 + 1))


async def main():
    tmp_list = []
    for 股票 in tqdm.tqdm(iterable=Equities.select(), ascii=True):
        开始日期 = 股票.list_date
        结束日期 = datetime.date.today()

        if 开始日期 < datetime.date(2005, 1, 1):
            开始日期 = datetime.date(2005, 1, 1)
        
        当前日期 = 开始日期
        一天 = datetime.timedelta(days=1)
        while 当前日期 <= 结束日期:
            
            if 当前日期.isoweekday() in [周六, 周日]:
                当前日期 += 一天
                continue
            页码 = 1
            tmp_list.append((股票, 当前日期, 页码))
            当前日期 += 一天

    random.shuffle(tmp_list)
    for each_obj in tmp_list:
        obj_list.put(each_obj)

    while True:
        # await asyncio.sleep(0.05 * random.random())
        await asyncio.sleep(0)

        # if obj_list.empty():
        #    break
        if obj_list.qsize() % 100 == 0:
            print(f'queue length: {obj_list.qsize()}')
           
        req = obj_list.get()
        if req is None:
            await asyncio.sleep(1)
            print('no new requests')
            continue
        
        asyncio.create_task(get_stock_history_date(obj_list, req))

if __name__ == "__main__":
    asyncio.run(main())


