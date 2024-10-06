from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from database.json_db import JsonDB
from models.recommender import Recommendation
from models.db import OpportunityDB
from utils.constants import JSON_DB_PATH
from utils.tables import OPPORTUNITY_TABLE

recommender_router = APIRouter(prefix="/recommend")
db = JsonDB(JSON_DB_PATH)


@recommender_router.get("")
async def get_recommendations(limit: int):
    opps = db.read_from_db(OpportunityDB, OPPORTUNITY_TABLE)
    recomms = [convert_to_recom(opp) for opp in opps][:limit]
    return jsonable_encoder(recomms)


# TODO - Do not tighly couple OpportunityDB and Recommendation
def convert_to_recom(opp: OpportunityDB) -> Recommendation:
    return Recommendation(
        ticker=opp.ticker,
        score=opp.metadata.get("score", -1),
        order_type=opp.order_type,
        default_price=opp.default_price,
    )
