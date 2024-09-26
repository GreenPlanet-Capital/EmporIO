from database.json_db import JsonDB
from cronjobs.fetch_opps import FetchOpps

db = JsonDB("storage")
f_opps = FetchOpps(db)
f_opps.execute()
