from asyncpg.pool import Pool
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