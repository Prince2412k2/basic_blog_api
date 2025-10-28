

--- 
 ## **path**: /service.py 
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
        return result == "UPDATE 1"
    
    @staticmethod
    async def delete(user_id:int,db:Pool):
        result=await db.execute('''
            DELETE FROM users
            WHERE id=$1;
            ''',user_id)
        return result == "DELETE 1"
    
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
        return result=="UPDATE 1"
    
    @staticmethod
    async def delete(blog_id:int,db:Pool):
        result=await db.execute('''
            DELETE FROM blogs
            WHERE id=$1;
            ''',blog_id)
        return result == "DELETE 1"
    
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
        return result=="UPDATE 1"
    
    @staticmethod
    async def delete(comment_id:int,db:Pool):
        result=await db.execute('''
            DELETE FROM comments
            WHERE id=$1;
            ''',comment_id)
        return result == "DELETE 1"
    
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
 ## **path**: /db.py 
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

 ```

--- 
 ## **path**: /main.py 
 ```from fastapi import FastAPI,Depends,HTTPException,status
from fastapi.security import OAuth2PasswordRequestForm
from contextlib import asynccontextmanager



from db import db
from service import (
    CreateTables,
    UserService,
    BlogService,
    CommentService
    )
from schema import BlogRequest, CommentRequest, Comments, User,CustomResponse,Token,Blogs,Blog,Comment
from auth import create_access_token,get_current_user
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
    await CreateTables.run(db.pool)
    yield
    await db.disconnect()
    
app=FastAPI(lifespan=lifespan)

@app.post("/signup")
async def signup(user:User):
    if await UserService.exists(user.name,db.pool):
        return CustomResponse(status=403,payload=f"User with name={user.name} already exists")
    try:
        await UserService.create(user.name,user.password,db.pool)
        return CustomResponse(status=200,payload="User created!!")
    except Exception as e:
        return CustomResponse(status=400,payload=str(e))
    

@app.post("/login")
async def login(form_data:Annotated[OAuth2PasswordRequestForm,Depends()])->Token:
    user=await UserService.validate( form_data.username, form_data.password,db.pool)
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
    
@app.get("/blogs")
async def blogs(current_user: Annotated[User, Depends(get_current_user)]):
    try:
        blogs=await BlogService.read_all(db.pool)
        return Blogs(blogs=blogs)
    except Exception:
        raise

@app.get("/blog/{blog_id}")
async def get_blog(blog_id:int,current_user: Annotated[User, Depends(get_current_user)]):
    try:
        blog=await BlogService.read(blog_id,db.pool)
        if not blog:
            raise ValueError("No blog for given blog_id")
        return Blog(**blog)
    except Exception as e:
        return CustomResponse(status=400,payload=str(e))
    
@app.post("/blog")
async def set_blog(blog:BlogRequest,current_user: Annotated[dict, Depends(get_current_user)]):
    try:
        blog=await BlogService.create(user_id=current_user["id"],title=blog.title,content=blog.content,db=db.pool)
        return CustomResponse(status=200,payload="Successfully created")
    except Exception as e:
        return CustomResponse(status=400,payload=str(e))
    
@app.delete("/blog/{blog_id}")
async def delete_blog(blog_id:int,current_user: Annotated[dict, Depends(get_current_user)]):
    try:
        blog=await BlogService.read(blog_id=blog_id,db=db.pool)
        if blog["user_id"]!=current_user["id"]:
            raise ValueError("cant delete a blog you dont own")
        blog=await BlogService.delete(blog_id,db=db.pool)
        return CustomResponse(status=200,payload="Successfully deleted")
    except Exception as e:
        return CustomResponse(status=400,payload=str(e))
    

@app.get("/blog/comments/{blog_id}")
async def comments(blog_id:int,current_user: Annotated[dict, Depends(get_current_user)]):
    try:
        comments=await CommentService.read_all_from_blog(blog_id,db.pool)
        return Comments(comments=comments)
    except Exception:
        raise

@app.get("/user/comments")
async def my_comments(current_user: Annotated[dict, Depends(get_current_user)]):
    try:
        comments=await CommentService.read_all_from_user(current_user["id"],db.pool)
        return Comments(comments=comments)
    except Exception:
        raise
    
@app.post("/comment")
async def add_comment(comment:CommentRequest,current_user: Annotated[dict, Depends(get_current_user)]):
    try:
        comment=await CommentService.create(blog_id=comment.blog_id,user_id=current_user["id"],content=comment.content,db=db.pool)
        return CustomResponse(status=200,payload="Successfully created")
    except Exception as e:
        return CustomResponse(status=400,payload=str(e))
    
@app.delete("/comment/{comment_id}")
async def delete_comment(comment_id:int,current_user: Annotated[dict, Depends(get_current_user)]):
    try:
        comment=await CommentService.read(comment_id=comment_id,db=db.pool)
        if comment["user_id"]!=current_user["id"]:
            raise ValueError("cant delete a blog you dont own")
        await BlogService.delete(comment_id,db=db.pool)
        return CustomResponse(status=200,payload="Successfully deleted")
    except Exception as e:
        return CustomResponse(status=400,payload=str(e))
 

 ```

 **hidden : /.git** 

 **hidden : /.gitignore** 

--- 
 ## **path**: /schema.py 
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

 **hidden : /context.md** 

 **hidden : /__pycache__** 

--- 
 ## **path**: /auth.py 
 ```from fastapi import Depends,  HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import os 
import jwt
from jwt.exceptions import InvalidTokenError
from typing import Annotated

from pydantic_core.core_schema import int_schema

from service import UserService
from db import db
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

 **hidden : /.env** 