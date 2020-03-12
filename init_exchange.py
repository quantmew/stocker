import uuid
from models import *

if __name__ == "__main__":
    db.connect()
    # 获取人民币
    rmb, created = Currency.get_or_create(
        symbol='CNY',
        defaults={
            'uuid': uuid.uuid4(),
            'name': '人民币',
            'enname': 'RMB',
        })

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