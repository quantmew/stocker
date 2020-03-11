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

# 货币
class Currency(BaseModel):
    uuid = peewee.UUIDField(primary_key=True, unique=True)
    name = peewee.CharField(max_length=64)
    enname = peewee.CharField(max_length=64)
    symbol = peewee.CharField(max_length=16)

# 交易所（上证）
class Exchange(BaseModel):
    uuid = peewee.UUIDField(primary_key=True, unique=True)
    name = peewee.CharField(max_length=64)
    enname = peewee.CharField(max_length=128)
    symbol = peewee.CharField(max_length=128)
    currency = peewee.ForeignKeyField(Currency, backref='exchanges') # 交易所使用何种货币

# 市场（主板/中小板/创业板/科创板）
class Market(BaseModel):
    uuid = peewee.UUIDField(primary_key=True, unique=True)
    name = peewee.CharField(max_length=64)
    enname = peewee.CharField(max_length=128)
    symbol = peewee.CharField(max_length=128)

# 申万分类
class ShenWanIndustry(BaseModel):
    uuid = peewee.UUIDField(primary_key=True, unique=True)
    industry_name = peewee.CharField(max_length=128) # 行业名称
    level = peewee.IntegerField() # 分类等级
    industry_code = peewee.CharField(max_length=64) # 行业代码

# 概念板块
class ConceptMarket(BaseModel):
    uuid = peewee.UUIDField(primary_key=True, unique=True)
    name = peewee.CharField(max_length=64) # 概念板块名

# 公司信息
class Company(BaseModel):
    uuid = peewee.UUIDField(primary_key=True, unique=True)
    name = peewee.CharField(max_length=256) # 公司名
    enname = peewee.CharField(max_length=256) # 公司英文名
    market = peewee.CharField(max_length=128) # 上市市场
    list_date = peewee.DateField() # 上市日期
    init_price = peewee.IntegerField() # 发行价格(厘)
    create_date = peewee.DateField() # 成立日期

# 股票
class Equities(BaseModel):
    uuid = peewee.UUIDField(primary_key=True, unique=True)
    # 基本信息
    exchange = peewee.ForeignKeyField(Exchange, backref='equities') # 所属市场
    market = peewee.ForeignKeyField(Market, backref='equities') # 所属板块
    symbol = peewee.CharField(max_length=128) # 股票代码
    name = peewee.CharField(max_length=64) # 股票名称
    area = peewee.CharField(max_length=64, null=True) # 所在地域
    industry = peewee.ForeignKeyField(ShenWanIndustry, backref='equities', null=True)
    list_status = peewee.CharField(max_length=16) # 上市信息 L上市 D退市 P暂停上市
    list_date = peewee.DateField(null=True) # 上市日期
    delist_date = peewee.DateField(null=True) # 退市日期

    # 公司信息
    company_name = peewee.CharField(max_length=128) # 公司名称
    main_business = peewee.CharField(max_length=512) # 主营业务
    telephone = peewee.CharField(max_length=64, null=True) # 电话
    fax = peewee.CharField(max_length=64, null=True) # 传真
    setup_date = peewee.DateField() # 成立日期
    chairman = peewee.CharField(max_length=128) # 法人代表
    manager = peewee.CharField(max_length=128, null=True) # 总经理
    reg_capital = peewee.IntegerField() # 注册资本(元)


# 概念板块链接
class EquitiesConceptMarket(BaseModel):
    equity = peewee.ForeignKeyField(Equities, backref='equities')
    concept = peewee.ForeignKeyField(ConceptMarket, backref='concepts')

    class Meta:
        primary_key = peewee.CompositeKey('equity', 'concept')