"""Database connection and lightweight SQLAlchemy/SQLite persistence."""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, String, Integer, DateTime, Text, JSON, Boolean, Float
from datetime import datetime
from app.core.config import settings
from app.core.logging import logger

Base = declarative_base()


class SessionRecord(Base):
    """Database model for recording sessions."""

    __tablename__ = "sessions"

    id = Column(String, primary_key=True, index=True)
    target_url = Column(String, nullable=False)
    title = Column(String, default="Untitled Workflow")
    description = Column(Text, nullable=True)
    status = Column(String, default="idle")
    action_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    session_metadata = Column(JSON, default=dict)


class DocumentRecord(Base):
    """Database model for generated documentation."""

    __tablename__ = "documents"

    id = Column(String, primary_key=True, index=True)
    session_id = Column(String, index=True)
    title = Column(String, nullable=False)
    executive_summary = Column(Text)
    prerequisites = Column(JSON, default=list)
    steps = Column(JSON, default=list)
    raw_markdown = Column(Text)
    quality_report = Column(JSON, nullable=True)
    version = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


engine = create_async_engine(settings.DATABASE_URL, echo=False)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def init_db():
    """Initialize database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables initialized.")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for obtaining async DB session."""
    async with async_session_maker() as session:
        yield session
