import uuid
from models import *

if __name__ == "__main__":
    db.connect()
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