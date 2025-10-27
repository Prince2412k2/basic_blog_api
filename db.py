import asyncpg 
from typing import Optional
from dotenv import load_dotenv
import os
load_dotenv()

PG_URL=os.environ.get("DATABASE_URL")

class Database:
    def __init__(self):
        self.pool:Optional[asyncpg.pool.pool]=None
        
    async def connect(self):
        self.pool=await asyncpg.create_pool(
            dsn=PG_URL
        ) 
    async def disconnect(self):
        if self.pool:
            await self.pool.close()
            
db=Database()