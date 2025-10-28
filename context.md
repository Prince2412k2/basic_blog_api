

 **hidden : .git** 

 **hidden : .gitignore** 

 **hidden : .pytest_cache** 



--- 
 ## **path**: blog_crud/service.py 
 ```from asyncpg.pool import Pool
from passlib.context import CryptContext
from typing import Optional, Union

pwd_context=CryptContext(schemes=["argon2"],deprecated="auto")
import logging 

logger=logging.getLogger(__name__)

class CreateTables:
    @staticmethod
    async def run(db:Pool):
        await CreateTables.user_table(db)
        await CreateTables.blog_table(db)
        await CreateTables.comment_table(db)

        
    @staticmethod
    async def user_table(db:Pool):
        await db.execute(''' 
                CREATE TABLE IF NOT EXISTS users(
                    id SERIAL PRIMARY KEY,
                    name text,
                    password text
                );            
                ''')
        logger.info("Created USERS table")
        
    @staticmethod
    async def blog_table(db:Pool):
        await db.execute(''' 
                CREATE TABLE IF NOT EXISTS blogs(
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
                    title text NOT NULL,
                    content text,
                    likes bigint DEFAULT 0
                );         
                ''')
        logger.info("Created BLOGs table")
    @staticmethod
    async def comment_table(db:Pool):
        await db.execute(''' 
                CREATE TABLE IF NOT EXISTS comments(
                    id SERIAL PRIMARY KEY,
                    content text,
                    blog_id BIGINT REFERENCES blogs(id) ON DELETE CASCADE,
                    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE
                );            
                ''')
        logger.info("Created COMMENTS table")

class PasswordService:
    @staticmethod
    def hash(password:str)->str:
        return pwd_context.hash(password)
    @staticmethod
    def verify(hashed_pass:str,password:str)->bool:
        return pwd_context.verify(password,hashed_pass)



class UserService:
    @staticmethod
    async def create(name:str,password:str,db:Pool):
        hashed=PasswordService.hash(password)
        row=await db.fetchrow(
            '''INSERT INTO users (name,password)
            Values($1,$2)
            RETURNING id;''',name,hashed
        )
        logger.info(f"Created user with name={name}")
        return row["id"]
    
    @staticmethod
    async def update(user_id:int,name:str,password:str,db:Pool):
        hashed=PasswordService.hash(password)
        result=await db.execute(
            '''UPDATE users 
            SET name=$1 , password=$2
            WHERE id=$3
        ;''',name,hashed,user_id
        )
        if result != "UPDATE 1":
            logger.info(f"User(id={user_id})Failed to Update")
            return False
        
        logger.info(f"User(id={user_id}) Updated successfully")
        return True
        
    
    @staticmethod
    async def delete(user_id:int,db:Pool):
        result=await db.execute('''
            DELETE FROM users
            WHERE id=$1;
            ''',user_id)
        
        if result != "DELETE 1":
            logger.info(f"User(id={user_id})Failed to delete")
            return False
        
        logger.info(f"User(id={user_id}) deleted successfully")
        return True
        
    
    @staticmethod
    async def read(user_id:int,db:Pool):
        result=await db.fetchrow('''
            SELECT * FROM users
            WHERE id=$1;
            ''',user_id)
        return dict(result) if result else False
    
    @staticmethod
    async def exists(user_name:str,db:Pool):
        result=await db.fetchrow('''
            SELECT * FROM users
            WHERE name=$1;
            ''',user_name)
        return dict(result) if result else False
    
    @staticmethod
    async def validate(user_name:str,password:str,db:Pool)->Union[dict,bool]:

        res=await db.fetchrow(''' 
                    SELECT * FROM users
                    WHERE name=$1;
                           ''',
                           user_name)
        if not res:
            return False            
        if PasswordService.verify(res["password"],password):
            return dict(res)
        return False


class BlogService:
    @staticmethod
    async def create(title:str,content:str,user_id:int,db:Pool):
        row=await db.fetchrow(
            '''INSERT INTO blogs (title,content,user_id)
            Values($1,$2,$3)
            RETURNING id;''',title,content,user_id
        )
        logger.info(f"Created blog with {title=}")
        return row["id"]
    
    @staticmethod
    async def update(blog_id:int,title:str,content:str,db:Pool):
        result=await db.execute(
            '''UPDATE blogs 
            SET title=$1 , content=$2
            WHERE id=$3;
            ''',
            title,content,blog_id
        )
        if result != "UPDATE 1":
            logger.info(f"Blog(id={blog_id})Failed to Update")
            return False
        
        logger.info(f"Blog(id={blog_id}) Updated successfully")
        return True
        
    
    @staticmethod
    async def delete(blog_id:int,db:Pool):
        result=await db.execute('''
            DELETE FROM blogs
            WHERE id=$1;
            ''',blog_id)
        if result != "DELETE 1":
            logger.info(f"Blog(id={blog_id})Failed to Delete")
            return False
        
        logger.info(f"Blog(id={blog_id}) Deleted successfully")
        return True
    
    @staticmethod
    async def read(blog_id:int,db:Pool):
        result=await db.fetchrow('''
            SELECT * FROM blogs
            WHERE id=$1;
            ''',blog_id)
        return dict(result) if result else False
    
    @staticmethod
    async def read_all(db:Pool):
        result=await db.fetch('''
            SELECT * FROM blogs
            ''')
        parsed=[dict(i) for i in result]
        return parsed
    
    @staticmethod
    async def read_all_for_user(user_id:int,db:Pool):
        result=await db.fetch('''
            SELECT * FROM blogs
            WHERE user_id=$1;
            ''',user_id)
        parsed=[dict(i) for i in result]
        return parsed
        

class CommentService:
    @staticmethod
    async def create(blog_id:int,content:str,user_id:int,db:Pool):
        row=await db.fetchrow(
            '''INSERT INTO comments (blog_id,content,user_id)
            Values($1,$2,$3)
            RETURNING id;''',blog_id,content,user_id
        )
        return row["id"]
    
    @staticmethod
    async def update(comment_id:int,content:str,db:Pool):
        result=await db.execute(
            '''UPDATE comments 
            SET content=$1
            WHERE id=$2;
            ''',
            content,comment_id
        )
        if result != "UPDATE 1":
            logger.info(f"Comment(id={comment_id})Failed to Update")
            return False
        
        logger.info(f"Comment(id={comment_id}) Updated successfully")
        return True
    
    @staticmethod
    async def delete(comment_id:int,db:Pool):
        result=await db.execute('''
            DELETE FROM comments
            WHERE id=$1;
            ''',comment_id)
        if result != "DELETE 1":
            logger.info(f"Comment(id={comment_id})Failed to Delete")
            return False
        
        logger.info(f"Comment(id={comment_id}) Deleted successfully")
        return True
        
    @staticmethod
    async def read(comment_id:int,db:Pool):
        result=await db.fetchrow('''
            SELECT * FROM comments
            WHERE id=$1;
            ''',comment_id)
        return result
    

    @staticmethod
    async def read_all_from_blog(blog_id:int,db:Pool):
        result=await db.fetch('''
            SELECT * FROM comments
            WHERE blog_id=$1;
            ''',blog_id)
        parsed=[dict(i) for i in result]
        return parsed
    
    @staticmethod
    async def read_all_from_user(user_id:int,db:Pool):
        result=await db.fetch('''
            SELECT * FROM comments
            WHERE user_id=$1;
            ''',user_id)
        parsed=[dict(i) for i in result]
        return parsed 

 ```

--- 
 ## **path**: blog_crud/db.py 
 ```import asyncpg 
from typing import Optional
from dotenv import load_dotenv
import os
load_dotenv()

PG_URL=os.environ.get("DATABASE_URL")

class Database:
    def __init__(self):
        self.pool:Optional[asyncpg.pool.Pool]=None
        
    async def connect(self):
        self.pool=await asyncpg.create_pool(
            dsn=PG_URL
        ) 
    async def disconnect(self):
        if self.pool:
            await self.pool.close()
db=Database()            
def get_db()->asyncpg.pool.Pool:
    if not db.pool:
        raise ValueError("DB is not connected")
    return db.pool
 

 ```

--- 
 ## **path**: blog_crud/__init__.py 
 ``` 

 ```

--- 
 ## **path**: blog_crud/main.py 
 ```from fastapi import FastAPI,Depends,HTTPException,status,Response
from fastapi.security import OAuth2PasswordRequestForm
from contextlib import asynccontextmanager



from blog_crud.db import db,get_db
from blog_crud.service import (
    CreateTables,
    UserService,
    BlogService,
    CommentService
    )
from blog_crud.schema import BlogRequest, CommentRequest, Comments, User,Token,Blogs,Blog
from blog_crud.auth import create_access_token,get_current_user
from typing import Annotated
import logging 

logging.basicConfig(
    level=logging.WARNING,                     # Log everything at INFO or higher
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger=logging.getLogger(__name__)
@asynccontextmanager
async def lifespan(app:FastAPI):
    await db.connect()
    await CreateTables.run(get_db())
    yield
    await db.disconnect()
    
app=FastAPI(lifespan=lifespan)

@app.post("/signup")
async def signup(user:User):
    if await UserService.exists(user.name,get_db()):
        return Response(status_code=403,content=f"User with name={user.name} already exists")
    try:
        await UserService.create(user.name,user.password,get_db())
        return Response(status_code=200,content="User created!!")
    except Exception as e:
        return Response(status_code=400,content=str(e))
    

@app.post("/login")
async def login(form_data:Annotated[OAuth2PasswordRequestForm,Depends()])->Token:
    user=await UserService.validate( form_data.username, form_data.password,get_db())
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
    
@app.get("/blogs",status_code=200)
async def blogs(current_user: Annotated[User, Depends(get_current_user)]):
    try:
        blogs=await BlogService.read_all(get_db())
        return Blogs(blogs=blogs)
    except Exception as e:
        return Response(status_code=400,content=f"Something went wrong error:{e}")

@app.get("/blog/{blog_id}")
async def get_blog(blog_id:int,current_user: Annotated[User, Depends(get_current_user)]):
    try:
        blog=await BlogService.read(blog_id,get_db())
        if not blog:
            raise ValueError("No blog for given blog_id")
        return Blog(**blog)
    except Exception as e:
        return Response(status_code=400,content=str(e))
    
@app.post("/blog")
async def set_blog(blog:BlogRequest,current_user: Annotated[dict, Depends(get_current_user)]):
    try:
        blog=await BlogService.create(user_id=current_user["id"],title=blog.title,content=blog.content,db=get_db())
        return Response(status_code=200,content="Successfully created")
    except Exception as e:
        return Response(status_code=400,content=str(e))
    
@app.delete("/blog/{blog_id}")
async def delete_blog(blog_id:int,current_user: Annotated[dict, Depends(get_current_user)]):
    try:
        blog=await BlogService.read(blog_id=blog_id,db=get_db())
        if blog["user_id"]!=current_user["id"]:
            raise ValueError("cant delete a blog you dont own")
        blog=await BlogService.delete(blog_id,db=get_db())
        return Response(status_code=200,content="Successfully deleted")
    except Exception as e:
        return Response(status_code=400,content=str(e))
    

@app.get("/blog/comments/{blog_id}")
async def comments(blog_id:int,current_user: Annotated[dict, Depends(get_current_user)]):
    try:
        comments=await CommentService.read_all_from_blog(blog_id,get_db())
        return Comments(comments=comments)
    except Exception as e:
        return Response(status_code=400,content=f"Something went wrong error:{e}")

@app.get("/user/comments")
async def my_comments(current_user: Annotated[dict, Depends(get_current_user)]):
    try:
        comments=await CommentService.read_all_from_user(current_user["id"],get_db())
        return Comments(comments=comments)
    except Exception as e:
        return Response(status_code=400,content=f"Something went wrong error:{e}")
    
@app.post("/comment")
async def add_comment(comment:CommentRequest,current_user: Annotated[dict, Depends(get_current_user)]):
    try:
        comment=await CommentService.create(blog_id=comment.blog_id,user_id=current_user["id"],content=comment.content,db=get_db())
        return Response(status_code=200,content="Successfully created")
    except Exception as e:
        return Response(status_code=400,content=str(e))
    
@app.delete("/comment/{comment_id}")
async def delete_comment(comment_id:int,current_user: Annotated[dict, Depends(get_current_user)]):
    try:
        comment=await CommentService.read(comment_id=comment_id,db=get_db())
        if comment["user_id"]!=current_user["id"]:
            raise ValueError("cant delete a blog you dont own")
        await BlogService.delete(comment_id,db=get_db())
        return Response(status_code=200,content="Successfully deleted")
    except Exception as e:
        return Response(status_code=400,content=str(e))
 

 ```

--- 
 ## **path**: blog_crud/schema.py 
 ```from pydantic import BaseModel
from typing import List

##USER SCHEMA
class User(BaseModel):
    name:str
    password:str
    

##BLOG SCHEMA
class BlogRequest(BaseModel):
    title:str
    content:str
    

class Blog(BlogRequest):
    user_id:int 
    
class BlogResponse(Blog):
    id:int
    
    
class Blogs(BaseModel):
    blogs:List[BlogResponse]


##COMMENT SCHEMA
class CommentRequest(BaseModel):
    blog_id:int
    content:str
    
class Comment(CommentRequest):
    user_id:int

class CommentResponse(Comment):
    id:int

class Comments(BaseModel):
    comments:List[CommentResponse]

##CUSTOM SCHEMA
class CustomResponse(BaseModel):
    status:int
    payload:str
    
class Token(BaseModel):
    access_token:str
    token_type:str 
 

 ```

 **hidden : blog_crud/__pycache__** 

--- 
 ## **path**: blog_crud/auth.py 
 ```from fastapi import Depends,  HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import os 
import jwt
from jwt.exceptions import InvalidTokenError
from typing import Annotated



from blog_crud.service import UserService
from blog_crud.db import db
import logging 

logger=logging.getLogger(__name__)
load_dotenv()

EXP_TIME=os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES")
SECRET_KEY=os.environ.get("SECRET_KEY")
ALGORITHM=os.environ.get("ALGORITHM")
# print(SECRET_KEY, ALGORITHM)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

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
        detail="Could not Validate Credentials",
        headers={"WWW-Authenticate":"Bearer"}
    )
    try: 
        payload=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        user_id=payload.get("sub")
        if user_id is None:
            raise cred_exception
    except InvalidTokenError:
        raise cred_exception
    user=await UserService.read(user_id=int(user_id),db=db.pool)

    if not user:
        raise cred_exception
    
    user["id"]=int(user_id)
    return user 

 ```

--- 
 ## **path**: Dockerfile 
 ```FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app
RUN apt-get update && apt-get install -y build-essential

COPY requirements.txt .

RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

#--------------------------------------------------------------------#

FROM python:3.12-slim AS runtime 

RUN useradd -m appuser 
WORKDIR /app

COPY --from=builder /install /usr/local

COPY blog_crud ./blog_crud

EXPOSE 8000

USER appuser 

CMD ["uvicorn", "blog_crud.main:app", "--host", "0.0.0.0", "--port", "8000"]
 

 ```

--- 
 ## **path**: requirements.txt 
 ```fastapi[standard]
pyjwt
passlib
asyncpg
 

 ```

 **hidden : __pycache__** 

 **hidden : .env** 



--- 
 ## **path**: tests/__init__.py 
 ``` 

 ```

--- 
 ## **path**: tests/test_app.py 
 ```import pytest
from fastapi.testclient import TestClient
from blog_crud.main import app
from blog_crud.schema import BlogRequest, CommentRequest

# -----------------------------------------------------------------------------
# Fixtures
# -----------------------------------------------------------------------------
@pytest.fixture(scope="module")
def client():
    # lifespan context triggers DB connect/disconnect
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="module")
def signup_and_login(client):
    """Create a user and return their access token."""
    username = "tester"
    password = "secret"

    # sign up (ignore if already exists)
    client.post("/signup", json={"name": username, "password": password})

    # login to get JWT token
    resp = client.post("/login", data={"username": username, "password": password})
    assert resp.status_code == 200, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

# -----------------------------------------------------------------------------
# Tests: Users
# -----------------------------------------------------------------------------
def test_signup_new_user(client):
    resp = client.post("/signup", json={"name": "unique_user", "password": "pw"})
    assert resp.status_code in (200, 403)  # user may already exist

def test_login_returns_token(client):
    client.post("/signup", json={"name": "tester", "password": "secret"})
    resp = client.post("/login", data={"username": "tester", "password": "secret"})
    assert resp.status_code == 200, resp.text
    assert "access_token" in resp.json()
# -----------------------------------------------------------------------------
# Tests: Blogs
# -----------------------------------------------------------------------------
def test_create_blog(client, signup_and_login):
    payload = BlogRequest(title="title one", content="content one").model_dump()
    resp = client.post("/blog", headers=signup_and_login, json=payload)
    assert resp.status_code == 200, resp.text

def test_get_all_blogs(client, signup_and_login):
    resp = client.get("/blogs", headers=signup_and_login)
    assert resp.status_code == 200
    data = resp.json()
    assert "blogs" in data

def test_get_blog_by_id(client, signup_and_login):
    # create a blog first
    new_blog = BlogRequest(title="temp", content="temp").model_dump()
    create_resp = client.post("/blog", headers=signup_and_login, json=new_blog)
    assert create_resp.status_code == 200
    # read blogs to get an ID
    list_resp = client.get("/blogs", headers=signup_and_login)
    blog_id = list_resp.json()["blogs"][0]["id"]
    resp = client.get(f"/blog/{blog_id}", headers=signup_and_login)
    assert resp.status_code == 200

def test_delete_blog(client, signup_and_login):
    # make a new blog, then delete it
    blog = BlogRequest(title="delete me", content="soon gone").model_dump()
    create_resp = client.post("/blog", headers=signup_and_login, json=blog)
    assert create_resp.status_code == 200
    blogs_resp = client.get("/blogs", headers=signup_and_login)
    blog_id = blogs_resp.json()["blogs"][-1]["id"]
    resp = client.delete(f"/blog/{blog_id}", headers=signup_and_login)
    assert resp.status_code == 200

# -----------------------------------------------------------------------------
# Tests: Comments
# -----------------------------------------------------------------------------
def test_add_comment_and_fetch(client, signup_and_login):
    # create a blog to comment on
    blog = BlogRequest(title="comment target", content="stuff").model_dump()
    client.post("/blog", headers=signup_and_login, json=blog)
    blogs_resp = client.get("/blogs", headers=signup_and_login)
    blog_id = blogs_resp.json()["blogs"][-1]["id"]

    # add comment
    comment_payload = CommentRequest(blog_id=blog_id, content="nice!").model_dump()
    resp = client.post("/comment", headers=signup_and_login, json=comment_payload)
    assert resp.status_code == 200

    # fetch comments for that blog
    resp = client.get(f"/blog/comments/{blog_id}", headers=signup_and_login)
    assert resp.status_code == 200
    assert "comments" in resp.json()

def test_user_comments_endpoint(client, signup_and_login):
    resp = client.get("/user/comments", headers=signup_and_login)
    assert resp.status_code == 200
 

 ```

 **hidden : tests/__pycache__** 

 **hidden : .venv** 