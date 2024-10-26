from pydantic import BaseModel


class CryptoOrderConf(BaseModel):
    uid_string: str
