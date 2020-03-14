import logging
from models import *


if __name__ == "__main__":
    # logger = logging.getLogger('peewee')
    # logger.addHandler(logging.StreamHandler())
    # logger.setLevel(logging.DEBUG)

    db.create_tables([
        Exchange,
        Currency,
        Market,
        ShenWanIndustry,
        ConceptMarket,
        Person,
        Company,
        Tenure,
        Equities,
        EquitiesConceptMarket,
        Transaction,
        ]
    )