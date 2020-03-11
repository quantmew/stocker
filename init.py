import uuid
from collector.models import *

if __name__ == "__main__":
    db.connect()
    db.create_tables([Equities, Exchange, Currency, Market])
    # 添加人名币
    rmb = Currency.create(
        uuid=uuid.uuid4(),
        name='人民币',
        enname='RMB',
        symbol='CNY')
    rmb.save()
    # 添加美元
    dollar = Currency.create(
        uuid=uuid.uuid4(),
        name='美元',
        enname='dollar',
        symbol='USD')
    dollar.save()
    # 添加上证
    sse = Exchange.create(
        uuid=uuid.uuid4(),
        name='上海证券交易所',
        enname='shanghai composite',
        symbol='SSE',
        currency=rmb)
    sse.save()

    # 添加主板
    zb = Market.create(
        uuid=uuid.uuid4(),
        name='主板',
        enname='ZhuBan')
    sse.save()