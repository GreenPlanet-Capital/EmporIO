from utils.db_conn import global_db
from cronjobs.fetch_opps import FetchOpps
from cronjobs.update_port import UpdatePort


def run():
    # f_opps = FetchOpps(global_db)
    # f_opps.execute()
    u_port = UpdatePort(global_db)
    u_port.execute()


if __name__ == "__main__":
    run()
