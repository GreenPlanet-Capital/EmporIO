from fastapi import APIRouter, Body, Depends, HTTPException
from models.db import TokenDB, UserDB
from models.user import (
    RegisterUser,
    LoginUser,
)
from passlib.context import CryptContext
from datetime import timedelta
from utils.db_conn import (
    SessionDep,
    AuthDep,
    add_entity,
    remove_entity,
    auth_manager,
)

user_router = APIRouter(prefix="/user")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_token(email_address: str, session: SessionDep):
    existing_token = session.get(TokenDB, email_address)

    if existing_token:
        remove_entity(session, existing_token)

    access_token = auth_manager.create_access_token(
        data={"sub": email_address}, expires=timedelta(days=14)
    )

    token = TokenDB(email_address=email_address, token=access_token)
    add_entity(session, token)
    return access_token


@user_router.post("/register")
async def register_user(session: SessionDep, reg_user: RegisterUser = Body(...)):
    exists_user = session.get(UserDB, reg_user.email_address)

    if exists_user:
        raise HTTPException(status_code=401, detail="Email already registered")
    elif reg_user.email_address == "":
        raise HTTPException(status_code=401, detail="Email address cannot be empty")

    user_data = UserDB(email_address=reg_user.email_address, password=reg_user.password)
    user_data.hashed_password = pwd_context.hash(reg_user.password)
    add_entity(session, user_data)

    return {
        "message": "User created",
        "token": create_token(reg_user.email_address, session),
    }


@user_router.post("/login")
async def login(session: SessionDep, data: LoginUser = Body(...)):
    exists_user = session.get(UserDB, data.email_address)

    if not exists_user:
        raise HTTPException(status_code=401, detail="User not found")

    if not pwd_context.verify(data.password, exists_user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect password")

    return {"message": "Logged in", "token": create_token(data.email_address, session)}


@user_router.get("/view")
async def view_user(user: AuthDep):
    return {
        "message": "User is logged in",
        "user": user,
    }
