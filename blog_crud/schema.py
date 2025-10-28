from pydantic import BaseModel
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
