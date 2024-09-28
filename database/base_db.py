from typing import List
from pydantic import BaseModel


class BaseDB:
    def write_to_db(self, data: List[BaseModel], table: str) -> None:
        raise NotImplementedError

    def read_from_db(self, base_model: BaseModel, table: str) -> List[BaseModel]:
        raise NotImplementedError
