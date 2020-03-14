
from lxml import etree
import peewee
import datetime
import requests
import uuid
import time
import random
from decimal import *
from models import *

周六 = 6
周日 = 7

def 取第一个元素(数组):
    返回值 = None
    if len(数组) > 0:
        返回值 = 数组[0]
    else:
        返回值 = None

    return 返回值

if __name__ == "__main__":
    for 股票 in Equities.select():
        六位编号, 交易所缩写 = 股票.symbol.split('.')
        新浪链接股票编号 = 交易所缩写.lower() + 六位编号

        开始日期 = 股票.list_date
        结束日期 = datetime.date.today()

        if 开始日期 < datetime.date(2005, 1, 1):
            开始日期 = datetime.date(2005, 1, 1)
        
        当前日期 = 开始日期
        一天 = datetime.timedelta(days=1)
        while 当前日期 <= 结束日期:
            time.sleep(random.randint(1,10))
            if 当前日期.isoweekday() in [周六, 周日]:
                当前日期 += 一天
                continue
            页码 = 1
            while True:
                链接 = f'http://market.finance.sina.com.cn/transHis.php?symbol={新浪链接股票编号}&date={当前日期.strftime("%Y-%m-%d")}&page={str(页码)}'
                页面 = requests.get(链接)
                页面.encoding='gb2312'
                print(链接)
                网页语法树 = etree.HTML(页面.text)
                if 网页语法树 is None:
                    continue
                错误信息 = 取第一个元素(网页语法树.xpath('//div[contains(text(),"输入的代码有误或没有交易数据")]'))
                
                if 错误信息 is not None:
                    break

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
                    if '--' in 价格变动:
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
                页码 += 1
            当前日期 += 一天


