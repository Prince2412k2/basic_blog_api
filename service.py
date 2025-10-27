from asyncpg.pool import pool
from passlib.context import CryptContext
from typing import Optional

pwd_context=CryptContext(schemes=["bcrypt"],deprecated="auto")


class CreateTables:
    @staticmethod
    async def run(db:pool):
        await CreateTables.user_table(db)
        await CreateTables.blog_table(db)
        await CreateTables.comment_table(db)

        
    @staticmethod
    async def user_table(db:pool):
        await db.execute(''' 
                CREATE TABLE IF NOT EXISTS users(
                    id SERIAL PRIMARY KEY,
                    name text,
                    password text
                );            
                ''')
        
    @staticmethod
    async def blog_table(db:pool):
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
    async def comment_table(db:pool):
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
    async def create(name:str,password:str,db:pool):
        hashed=PasswordService.hash(password)
        row=await db.fetchrow(
            '''INSERT INTO users (name,password)
            Values($1,$2)
            RETURNING id;''',name,hashed
        )
        return row["id"]
    
    @staticmethod
    async def update(user_id:int,name:str,password:str,db:pool):
        hashed=PasswordService.hash(password)
        result=await db.execute(
            '''UPDATE users 
            SET name=$1 , password=$2
            WHERE id=$3
        ;''',name,hashed,user_id
        )
        return result == "UPDATE 1"
    
    @staticmethod
    async def delete(user_id:int,db:pool):
        result=await db.execute('''
            DELETE FROM users
            WHERE id=$1;
            ''',user_id)
        return result == "DELETE 1"
    
    @staticmethod
    async def read(user_id:int,db:pool):
        result=await db.fetchrow('''
            SELECT * FROM users
            WHERE id=$1;
            ''',user_id)
        return dict(result) if result else False
    
    @staticmethod
    async def exists(user_name:int,db:pool):
        result=await db.fetchrow('''
            SELECT * FROM users
            WHERE id=$1;
            ''',user_name)
        return dict(result) if result else False
    
    @staticmethod
    async def validate(user_name:str,password:str,db:pool)->Optional[dict]:

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
    async def create(title:str,content:str,user_id:int,db:pool):
        row=await db.fetchrow(
            '''INSERT INTO blogs (title,content,user_id)
            Values($1,$2,$3)
            RETURNING id;''',title,content,user_id
        )
        return row["id"]
    
    @staticmethod
    async def update(blog_id:int,title:str,content:str,db:pool):
        result=await db.execute(
            '''UPDATE blogs 
            SET title=$1 , content=$2
            WHERE id=$3;
            ''',
            title,content,blog_id
        )
        return result=="UPDATE 1"
    
    @staticmethod
    async def delete(blog_id:int,db:pool):
        result=await db.execute('''
            DELETE FROM blogs
            WHERE id=$1;
            ''',blog_id)
        return result == "DELETE 1"
    
    @staticmethod
    async def read(blog_id:int,db:pool):
        result=await db.fetchrow('''
            SELECT * FROM blogs
            WHERE id=$1;
            ''',blog_id)
        return dict(result) if result else False
    
    @staticmethod
    async def read_all_for_user(user_id:int,db:pool):
        result=await db.fetch('''
            SELECT * FROM blogs
            WHERE user_id=$1;
            ''',user_id)
        return result
        

class CommentService:
    @staticmethod
    async def create(blog_id:int,content:str,user_id:int,db:pool):
        row=await db.fetchrow(
            '''INSERT INTO comments (blog_id,content,user_id)
            Values($1,$2,$3)
            RETURNING id;''',blog_id,content,user_id
        )
        return row["id"]
    
    @staticmethod
    async def update(comment_id:int,content:str,db:pool):
        result=await db.execute(
            '''UPDATE comments 
            SET content=$1
            WHERE id=$2;
            ''',
            content,comment_id
        )
        return result=="UPDATE 1"
    
    @staticmethod
    async def delete(comment_id:int,db:pool):
        result=await db.execute('''
            DELETE FROM comments
            WHERE id=$1;
            ''',comment_id)
        return result == "DELETE 1"
    
    @staticmethod
    async def read(comment_id:int,db:pool):
        result=await db.fetchrow('''
            SELECT * FROM comments
            WHERE id=$1;
            ''',comment_id)
        return result
    

    @staticmethod
    async def read_all_from_blog(blog_id:int,db:pool):
        result=await db.fetch('''
            SELECT * FROM comments
            WHERE blog_id=$1;
            ''',blog_id)
        return result
    
    @staticmethod
    async def read_all_from_user(user_id:int,db:pool):
        result=await db.fetch('''
            SELECT * FROM comments
            WHERE user_id=$1;
            ''',user_id)
        return result