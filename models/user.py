import re
from pydantic import BaseModel, EmailStr, field_validator


def check_pwd(pwd):
    re_for_pwd: re.Pattern[str] = re.compile(r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{5,}$")
    if not re_for_pwd.match(pwd):
        raise ValueError(
            "Invalid password - must contain at least 1 letter and 1 number and"
            " be at least 5 characters long"
        )
    return pwd


class RegisterUser(BaseModel):
    email_address: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def regex_match(cls, pwd: str) -> str:
        return check_pwd(pwd)


class LoginUser(BaseModel):
    email_address: EmailStr
    password: str
