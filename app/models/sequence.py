from sqlalchemy import Column, Integer
from app.core.database import Base

class SlugSequence(Base):
    __tablename__ = "slug_sequence"

    id = Column(Integer, primary_key=True, index=True)
    current_value = Column(Integer, nullable=False)