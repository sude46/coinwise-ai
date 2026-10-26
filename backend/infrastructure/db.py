from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from core.config import settings

master_engine = create_async_engine(
    settings.DATABASE_URL_MASTER,
    echo=False,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)
slave_engine = create_async_engine(
    settings.DATABASE_URL_SLAVE,
    echo=False,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

async_session_master = async_sessionmaker(master_engine, class_=AsyncSession, expire_on_commit=False)
async_session_slave = async_sessionmaker(slave_engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()
