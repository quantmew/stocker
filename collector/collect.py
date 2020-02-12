import uuid
import models


if __name__ == "__main__":
    models.db.connect()
    models.db.create_tables([models.Exchange, models.Market, models.Currency])