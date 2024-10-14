from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from sqlmodel import select
from models.db import OpportunityDB
from utils.db_conn import SessionDep, AuthDep

recommender_router = APIRouter(prefix="/recommend")


@recommender_router.get("")
async def get_recommendations(limit: int, session: SessionDep):
    opps = session.exec(
        select(OpportunityDB).limit(limit).order_by(OpportunityDB.metadata_score.desc())
    ).all()
    return jsonable_encoder(opps)
