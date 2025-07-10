from sqlalchemy import Column, Integer, String, DateTime, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class URL(Base):
    __tablename__ = "urls"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(20), unique=True, index=True, nullable=False)
    long_url = Column(String, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.now)

    visits = relationship("Visit", back_populates="url", cascade="all, delete")

    __table_args__ = (
        Index("ix_slug", "slug"),
        Index("ix_long_url", "long_url"),
    )