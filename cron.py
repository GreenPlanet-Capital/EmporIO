from database.json_db import JsonDB
from cronjobs.fetch_opps import FetchOpps
from cronjobs.update_port import UpdatePort


def run():
    db = JsonDB("storage")
    # f_opps = FetchOpps(db)
    # f_opps.execute()
    u_port = UpdatePort(db)
    u_port.execute()


if __name__ == "__main__":
    run()
