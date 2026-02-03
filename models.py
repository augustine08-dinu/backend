from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from database import Base

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False)
    rating = Column(Integer, nullable=False)
    review = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
