import sys
import os
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../.."))

from database.connection import get_db

async def get_database():
    """Dependency to get database session"""
    async for db in get_db():
        yield db