import peewee
import datetime

from playhouse.db_url import connect

# Connect to the database URL defined in the environment, falling
# back to a local Sqlite database if no database URL is specified.
db = connect('mysql://root:QAZqaz1234@localhost:3306/stocker')

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

# 公司高管
class Person(BaseModel):
    uuid = peewee.UUIDField(primary_key=True, unique=True)
    name = peewee.CharField(max_length=64) # 姓名
    gender = peewee.CharField(max_length=32) # 性别
    birth = peewee.CharField(max_length=32, null=True) # 出生日期
    education = peewee.CharField(max_length=32, null=True) # 学历
    nationality = peewee.CharField(max_length=64, null=True) # 国籍
    resume  = peewee.TextField(null=True) # 简历

# 公司信息
class Company(BaseModel):
    uuid = peewee.UUIDField(primary_key=True, unique=True)
    name = peewee.CharField(max_length=256) # 公司名
    enname = peewee.CharField(max_length=256) # 公司英文名
    market = peewee.CharField(max_length=128, null=True) # 上市市场
    list_date = peewee.DateField(null=True) # 上市日期
    init_price = peewee.CharField(max_length=128, null=True) # 发行价格
    lead_underwriter = peewee.CharField(max_length=256, null=True) # 主承销商
    create_date = peewee.DateField(null=True) # 成立日期
    reg_capital = peewee.IntegerField(null=True) # 注册资本(元)
    organization_type = peewee.CharField(max_length=128, null=True) # 机构类型
    organization_form = peewee.CharField(max_length=128, null=True) # 组织形式

    board_secretary = peewee.CharField(max_length=128, null=True) # 董事会秘书
    board_secretary_telephone = peewee.CharField(max_length=128, null=True) # 董秘电话
    board_secretary_fax = peewee.CharField(max_length=128, null=True) # 董秘传真
    board_secretary_mail = peewee.CharField(max_length=128, null=True) # 董秘电子邮件

    company_telephone = peewee.CharField(max_length=128, null=True) # 公司电话
    company_fax = peewee.CharField(max_length=128, null=True) # 公司传真
    company_mail = peewee.CharField(max_length=128, null=True) # 公司邮件
    company_website = peewee.CharField(max_length=128, null=True) # 公司网站

    zip_code = peewee.CharField(max_length=64, null=True) # 公司邮编
    register_address = peewee.CharField(max_length=256, null=True) # 注册地址
    office_address = peewee.CharField(max_length=256, null=True) # 办公地址
    description = peewee.TextField(null=True) # 公司简介
    business_scope = peewee.TextField(null=True) # 经营范围

# 任职情况
class Tenure(BaseModel):
    uuid = peewee.UUIDField(primary_key=True, unique=True)
    person = peewee.ForeignKeyField(Person, backref='tenure') # 高管
    company = peewee.ForeignKeyField(Company, backref='tenure') # 任职公司
    position = peewee.CharField(max_length=64) # 职务
    appointment_date = peewee.DateField(null=True) # 任职日期
    departure_date = peewee.DateField(null=True) # 离职日期
    remuneration = peewee.IntegerField(null=True) # 报酬(元)
    period = peewee.IntegerField(null=True) # 第几届

# 股票
class Equities(BaseModel):
    uuid = peewee.UUIDField(primary_key=True, unique=True)
    # 基本信息
    exchange = peewee.ForeignKeyField(Exchange, backref='equities', null=True) # 所属市场
    market = peewee.ForeignKeyField(Market, backref='equities', null=True) # 所属板块
    symbol = peewee.CharField(max_length=128) # 股票代码
    name = peewee.CharField(max_length=64) # 股票名称
    area = peewee.CharField(max_length=64, null=True) # 所在地域
    industry = peewee.ForeignKeyField(ShenWanIndustry, backref='equities', null=True)
    list_status = peewee.CharField(max_length=16) # 上市信息 L上市 D退市 P暂停上市
    list_date = peewee.DateField(null=True) # 上市日期
    delist_date = peewee.DateField(null=True) # 退市日期

    # 公司信息
    company = peewee.ForeignKeyField(Company, backref='equities', null=True) # 公司详细信息
    company_name = peewee.CharField(max_length=128) # 公司名称
    main_business = peewee.CharField(max_length=512) # 主营业务
    telephone = peewee.CharField(max_length=64, null=True) # 电话
    fax = peewee.CharField(max_length=64, null=True) # 传真
    setup_date = peewee.DateField(null=True) # 成立日期
    chairman = peewee.CharField(max_length=128, null=True) # 法人代表
    manager = peewee.CharField(max_length=128, null=True) # 总经理
    reg_capital = peewee.IntegerField(null=True) # 注册资本(元)

# 概念板块链接
class EquitiesConceptMarket(BaseModel):
    equity = peewee.ForeignKeyField(Equities, backref='equities')
    concept = peewee.ForeignKeyField(ConceptMarket, backref='concepts')

    class Meta:
        primary_key = peewee.CompositeKey('equity', 'concept')

# 成交明细
class Transaction(BaseModel):
    uuid = peewee.UUIDField(primary_key=True, unique=True)
    equity = peewee.ForeignKeyField(Equities, backref='transaction', index = True)
    time = peewee.DateTimeField(index = True)
    price = peewee.DecimalField(max_digits=14, decimal_places=3) # 成交价
    price_change = peewee.DecimalField(max_digits=14, decimal_places=3) # 价格变动
    volume = peewee.IntegerField() # 成交量(手)
    turnover = peewee.DecimalField(max_digits=14, decimal_places=3) # 成交额(元)
    kind = peewee.CharField(max_length=16)# 性质(买盘、买盘、中性盘)

# k线数据
class KDataDay(BaseModel):
    uuid = peewee.UUIDField(primary_key=True, unique=True)
    date = peewee.DateField(index = True) # 日期
    equity = peewee.ForeignKeyField(Equities, backref='kdata', index = True) # 股票代码
    open_price = peewee.DecimalField(max_digits=14, decimal_places=3) # 开盘价
    high_price = peewee.DecimalField(max_digits=14, decimal_places=3) # 最高价
    low_price = peewee.DecimalField(max_digits=14, decimal_places=3) # 最低价
    close_price = peewee.DecimalField(max_digits=14, decimal_places=3) # 今收盘价
    volume = peewee.IntegerField()	# 成交数量
    amount = peewee.DecimalField(max_digits=14, decimal_places=3)	# 成交金额
    adjustflag = peewee.IntegerField() # 复权状态, 复权类型，默认不复权：1；2：后复权；3：前复权
    turn = peewee.DecimalField(max_digits=12, decimal_places=6, null=True) # 换手率
    tradestatus = peewee.IntegerField(null=True) # 交易状态 (1：正常交易 0：停牌）
    pctChg = peewee.DecimalField(max_digits=12, decimal_places=6, null=True) # 涨跌幅
    peTTM = peewee.DecimalField(max_digits=12, decimal_places=6, null=True) # 滚动市盈率
    pbMRQ = peewee.DecimalField(max_digits=12, decimal_places=6, null=True) # 市净率
    psTTM = peewee.DecimalField(max_digits=12, decimal_places=6, null=True) # 滚动市销率
    pcfNcfTTM = peewee.DecimalField(max_digits=12, decimal_places=6, null=True) # 滚动市现率
    isST = peewee.IntegerField(null=True) # 是否ST股，1是，0否
