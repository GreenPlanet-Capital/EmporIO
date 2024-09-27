from database.json_db import JsonDB
from cronjobs.fetch_opps import FetchOpps


def run():
    db = JsonDB("storage")
    f_opps = FetchOpps(db)
    f_opps.execute()


if __name__ == "__main__":
    run()
