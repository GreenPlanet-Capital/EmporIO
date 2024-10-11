from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from sqlmodel import select
from models.recommender import Recommendation
from models.db import OpportunityDB
from utils.db_conn import SessionDep, AuthDep

recommender_router = APIRouter(prefix="/recommend")


@recommender_router.get("")
async def get_recommendations(limit: int, session: SessionDep, user: AuthDep):
    opps = session.exec(
        select(OpportunityDB).limit(limit).order_by(OpportunityDB.metadata_score.desc())
    ).all()
    recomms = [convert_to_recom(opp) for opp in opps]
    return jsonable_encoder(recomms)


# TODO - Do not tighly couple OpportunityDB and Recommendation
def convert_to_recom(opp: OpportunityDB) -> Recommendation:
    return Recommendation(
        ticker=opp.ticker,
        score=opp.metadata_score,
        order_type=int.from_bytes(opp.order_type, byteorder="little"),
        default_price=opp.default_price,
    )
