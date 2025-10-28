from fastapi import FastAPI,Depends,HTTPException,status,Response
from fastapi.security import OAuth2PasswordRequestForm
from contextlib import asynccontextmanager



from db import db,get_db
from service import (
    CreateTables,
    UserService,
    BlogService,
    CommentService
    )
from schema import BlogRequest, CommentRequest, Comments, User,Token,Blogs,Blog
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
    
@app.get("/blogs")
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
