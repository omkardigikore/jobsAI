# utils/db.py
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

from config.settings import DATABASE_URL

logger = logging.getLogger(__name__)

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    pool_size=20,
    max_overflow=20,
    pool_timeout=60,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# Create async session factory
async_session_factory = async_sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession,
    autoflush=False,
)

@asynccontextmanager
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Get database session as an async context manager
    Usage:
        async with get_db() as db:
            result = await db.execute(query)
    """
    session = async_session_factory()
    try:
        yield session
        await session.commit()
    except Exception as e:
        await session.rollback()
        logger.error(f"Database session error: {str(e)}")
        raise
    finally:
        await session.close()

async def execute_in_transaction(callback, *args, **kwargs):
    """
    Execute a callback within a database transaction
    
    Args:
        callback: Async function that takes a db session as first argument
        *args: Additional positional arguments for the callback
        **kwargs: Additional keyword arguments for the callback
        
    Returns:
        The result of the callback
    """
    async with get_db() as db:
        return await callback(db, *args, **kwargs)

async def get_or_create(db: AsyncSession, model, **kwargs):
    """
    Get or create a model instance
    
    Args:
        db: Database session
        model: Model class
        **kwargs: Attributes to query for and create with
        
    Returns:
        Tuple of (instance, created) where created is a boolean
    """
    from sqlalchemy.future import select
    
    # Separate filter_kwargs from defaults
    defaults = kwargs.pop('defaults', {})
    
    # Query for the instance
    query = select(model).filter_by(**kwargs)
    result = await db.execute(query)
    instance = result.scalar_one_or_none()
    
    if instance:
        return instance, False
    else:
        # Update kwargs with defaults for creation
        kwargs.update(defaults)
        instance = model(**kwargs)
        db.add(instance)
        await db.flush()
        return instance, True

async def bulk_create(db: AsyncSession, model, objects):
    """
    Bulk create model instances
    
    Args:
        db: Database session
        model: Model class
        objects: List of dictionaries with model attributes
        
    Returns:
        List of created instances
    """
    instances = [model(**obj) for obj in objects]
    db.add_all(instances)
    await db.flush()
    return instances

async def bulk_update(db: AsyncSession, model, objects, update_fields):
    """
    Bulk update model instances
    
    Args:
        db: Database session
        model: Model class
        objects: List of model instances to update
        update_fields: List of field names to update
        
    Returns:
        List of updated instances
    """
    from sqlalchemy import update
    from sqlalchemy.future import select
    
    if not objects:
        return []
    
    # Get primary key column
    pk_column = model.__table__.primary_key.columns.values()[0]
    
    # Group objects by primary key
    object_dict = {getattr(obj, pk_column.name): obj for obj in objects}
    
    # Get existing objects
    query = select(model).filter(pk_column.in_(object_dict.keys()))
    result = await db.execute(query)
    existing_objects = result.scalars().all()
    
    # Update each object
    for obj in existing_objects:
        pk_value = getattr(obj, pk_column.name)
        source_obj = object_dict[pk_value]
        
        for field in update_fields:
            setattr(obj, field, getattr(source_obj, field))
    
    await db.flush()
    return existing_objects