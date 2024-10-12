import numpy as np
from sqlmodel import SQLModel, Session, create_engine
from database.base_db import BaseDB
from psycopg2.extensions import register_adapter, AsIs


class SqlDB(BaseDB):
    def __init__(self, db_path: str):
        register_adapter(np.int64, AsIs)
        self.engine = create_engine(db_path, echo=False)
        self.create_db_and_tables()

    def create_db_and_tables(self):
        SQLModel.metadata.create_all(self.engine)
        print("Database and tables created")

    def get_session(self):
        with Session(self.engine) as session:
            yield session
