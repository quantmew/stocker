import peewee
import datetime

from playhouse.db_url import connect

# Connect to the database URL defined in the environment, falling
# back to a local Sqlite database if no database URL is specified.
db = connect('mysql://root:@localhost:3306/stoker')

class BaseModel(peewee.Model):
    """A base model that will use our MySQL database"""
    class Meta:
        database = db

# 交易所（上证）
class Exchange(BaseModel):
    uuid = peewee.CharField(primary_key=True, unique=True, max_length=36)
    name = peewee.CharField(max_length=64)
    enname = peewee.CharField(max_length=128)
    symbol = peewee.CharField(max_length=128)

# 
class Currency(BaseModel):
    uuid = peewee.CharField(primary_key=True, unique=True, max_length=36)
    name = peewee.CharField(max_length=64)
    enname = peewee.CharField(max_length=64)
    symbol = peewee.CharField(max_length=16)

# 市场（主板/中小板/创业板/科创板）
class Market(BaseModel):
    uuid = peewee.CharField(primary_key=True, unique=True, max_length=36)
    name = peewee.CharField(max_length=64)
    enname = peewee.CharField(max_length=128)
    symbol = peewee.CharField(max_length=128)


# 股票
class Equities(BaseModel):
    uuid = peewee.CharField(primary_key=True, unique=True, max_length=36)
    market = peewee.ForeignKeyField(Market, backref='equities') # 所属市场
    symbol = peewee.CharField(max_length=128) # 股票代码
    name = peewee.CharField(max_length=64) # 股票名称
    area = peewee.CharField(max_length=64) # 所在地域
    industry = peewee.CharField(max_length=64) # 所属行业
    list_status = peewee.CharField(max_length=16) # 上市信息 L上市 D退市 P暂停上市
    list_date = peewee.DateTimeField() # 上市日期
    delist_date = peewee.DateTimeField() # 退市日期



'''
class Tweet(BaseModel):
    user = ForeignKeyField(User, backref='tweets')
    message = TextField()
    created_date = DateTimeField(default=datetime.datetime.now)
    is_published = BooleanField(default=True)
'''