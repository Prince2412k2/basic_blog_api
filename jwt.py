
from fastapi import Depends,  HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import os 
import jwt
from jwt.exceptions import InvalidTokenError
from typing import Annotated

from service import UserService
from db import db

load_dotenv()

EXP_TIME=os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES")
SECRET_KEY=os.environ.get("SECRET_KEY")
ALGORITHM=os.environ.get("ALGORITHM")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(user_id:int, expires_delta: timedelta=timedelta(minutes=15)):
    return(
        jwt.encode(
            {"exp":datetime.now(timezone.utc) + expires_delta,
            "sub":str(user_id),
            },
            SECRET_KEY,algorithm=ALGORITHM
        )
    )
    
async def get_current_user(token:Annotated[str,Depends(oauth2_scheme)]):
    cred_exception=HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="COuld not Validate Credentials",
        headers={"WWW-Authenticate":"Bearer"}
    )
    try:
        payload=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        user_id=payload.get("sub")
        if user_id is None:
            raise cred_exception
    except InvalidTokenError:
        raise cred_exception
    user=await UserService.read(user_id=user_id,db=db.pool)
    if not user:
        raise cred_exception
    return user