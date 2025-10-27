from pydantic import BaseModel

class User(BaseModel):
    name:str
    password:str
    
class blog(BaseModel):
    title:str
    content:str
    user_id:int 
    
class Comment(BaseModel):
    content:str
    user_id:int
    blog_id:int
    
class CustomResponse(BaseModel):
    status:int
    payload:str
    
class Token(BaseModel):
    access_token:str
    token_type:str 
    

