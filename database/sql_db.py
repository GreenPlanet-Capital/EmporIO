import os
import json
from typing import List
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlmodel import SQLModel, Session, create_engine, select
from database.base_db import BaseDB


class SqlDB(BaseDB):
    def __init__(self, db_path: str):
        connect_args = {"check_same_thread": False}
        self.engine = create_engine(db_path, echo=False, connect_args=connect_args)
        self.create_db_and_tables()

    def create_db_and_tables(self):
        SQLModel.metadata.create_all(self.engine)
        print("Database and tables created")

    def get_session(self):
        with Session(self.engine) as session:
            yield session
