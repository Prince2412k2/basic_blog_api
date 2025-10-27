from fastapi import FastAPI,Depends,HTTPException,status
from fastapi.security import OAuth2PasswordRequestForm
from contextlib import asynccontextmanager

from db import db
from service import (
    CreateTables,
    UserService
    )
from schema import User,CustomResponse,Token
from jwt import create_access_token
from typing import Annotated


@asynccontextmanager
async def lifespan(app:FastAPI):
    await db.connect()
    await CreateTables(db.pool)
    yield
    await db.disconnect()
    
app=FastAPI(lifespan=lifespan)

@app.post("/signup")
async def signup(user:User):
    if await UserService.exists(user):
        return CustomResponse(status=403,payload=f"User with name={user.name} already exists")
    try:
        await UserService.create(user.name,user.password)
    except Exception as e:
        return CustomResponse(status=400,payload=str(e))
    

@app.post("/login")
async def login(form_data:Annotated[OAuth2PasswordRequestForm,Depends()])->Token:
    user=await UserService.validate( form_data.username, form_data.password)
    if not user:
            raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token=create_access_token(
            user_id=(user["id"])
        )
    return Token(access_token=access_token,token_type="bearer")
    
