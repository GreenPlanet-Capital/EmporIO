# Global DB instance
from fastapi import Depends
from fastapi_login import LoginManager
from sqlmodel import Session
from database.sql_db import SqlDB
from models.db import UserDB
from utils.constants import SQL_DB_PATH
from typing import Annotated
from sqlmodel import SQLModel


global_db = SqlDB(SQL_DB_PATH)
SessionDep = Annotated[Session, Depends(global_db.get_session)]

auth_manager = LoginManager("SECRET_KEY", "/login")
AuthDep = Annotated[UserDB, Depends(auth_manager)]


@auth_manager.user_loader()
def query_user(email_address: str):
    session = next(global_db.get_session())
    return session.get(UserDB, email_address)


def add_entity(session: SessionDep, entity: SQLModel):
    session.add(entity)
    session.commit()
    session.refresh(entity)
    return entity


def remove_entity(session: SessionDep, entity: SQLModel):
    session.delete(entity)
    session.commit()
    return entity
