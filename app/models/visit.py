from sqlalchemy import Column, Integer, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class Visit(Base):
    __tablename__ = "visits"

    id = Column(Integer, primary_key=True, index=True)
    url_id = Column(Integer, ForeignKey("urls.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.now)

    url = relationship("URL", back_populates="visits")

    __table_args__ = (Index("ix_visits_url_id", "url_id"),)