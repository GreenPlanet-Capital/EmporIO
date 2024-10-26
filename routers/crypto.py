from fastapi import APIRouter, HTTPException
from sqlmodel import update
from models.crypto import CryptoOrderConf
from models.db import CryptoOrderConfDB
from utils.db_conn import SessionDep, add_entity, remove_entity

crypto_router = APIRouter(prefix="/crypto")


@crypto_router.post("/confirm-order")
async def confirm_order(order: CryptoOrderConf, session: SessionDep):
    uid = parse_uid_from_str(order.uid_string)
    crypto_order = session.get(CryptoOrderConfDB, uid)

    if not crypto_order:
        raise HTTPException(status_code=404, detail="Order not found")

    session.exec(
        update(CryptoOrderConfDB)
        .where(CryptoOrderConfDB.uid == uid)
        .values(confirmed=True)
    )
    session.commit()
    return {"message": "Order confirmed"}


@crypto_router.get("/init-order")
async def init_order(uid: str, session: SessionDep):
    prev_order = session.get(CryptoOrderConfDB, uid)
    if prev_order:
        raise HTTPException(status_code=400, detail="Order already exists")
    add_entity(session, CryptoOrderConfDB(uid=uid, confirmed=False))
    return {"message": "Order initialized"}


@crypto_router.get("/get-order")
async def get_order(uid: str, session: SessionDep):
    crypto_order = session.get(CryptoOrderConfDB, uid)

    if not crypto_order:
        raise HTTPException(status_code=404, detail="Order not found")

    return {"order": crypto_order}


@crypto_router.get("/delete-order")
async def delete_order(uid: str, session: SessionDep):
    crypto_order = session.get(CryptoOrderConfDB, uid)

    if not crypto_order:
        raise HTTPException(status_code=404, detail="Order not found")

    remove_entity(session, crypto_order)
    return {"message": "Order deleted"}


def parse_uid_from_str(uid_string: str) -> str:
    parts = uid_string.split(":")
    if len(parts) != 4:
        raise HTTPException(
            status_code=400,
            detail="Invalid UID string format. Please directly paste the UID string from sms.",
        )
    return parts[-1].split()[-1][:-1]
