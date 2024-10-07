import os
import json
from typing import List
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from database.base_db import BaseDB


# TODO: Move away from JSON to a more robust database
class JsonDB(BaseDB):
    def __init__(self, db_path: str):
        self.db_path = db_path

    def write_to_db(self, data: List[BaseModel], table: str) -> None:
        with open(self.get_path(table), "w") as f:
            parsed = json.dumps(jsonable_encoder(data), indent=4)
            f.write(parsed)

    def read_from_db(self, base_model: BaseModel, table: str) -> List[BaseModel]:
        pth = self.get_path(table)

        if not os.path.exists(pth):
            return []

        with open(pth, "r") as f:
            data = json.loads(f.read())
        return [base_model(**item) for item in data]

    def get_path(self, table: str):
        return os.path.join(self.db_path, table) + ".json"
