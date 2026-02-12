from pydantic import BaseModel
from datetime import datetime

class ReviewCreate(BaseModel):
    name: str
    phone: str
    rating: int
    review: str

class ReviewResponse(ReviewCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class AdminLogin(BaseModel):
    username: str
    password: str
