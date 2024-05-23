import uuid
from typing import Optional
from pydantic import BaseModel, Field, EmailStr
from typing import List
from datetime import datetime


class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    username: str = Field(...)
    password: str = Field(...)
    email: EmailStr = Field(...)
    country: str = Field(...)
    state: str = Field(...)

    class Config:
        json_schema_extra = {
            "example": {
                "username": "Juan",
                "password": "password",
                "email": "juan@gmail.com",
                "country": "Mexico",
                "state": "CDMX",
            }
        }


class Question(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    question: str = Field(...)
    answer: Optional[str] = Field("", description="Answer to the question")
    userId: str = Field(...)
    date: datetime = Field(default_factory=datetime.now)

    class Config:
        json_schema_extra = {
            "example": {
                "question": "What is NEORIS?",
                "userId": "82d00a97-d923-4c5a-bc8e-e1684eff66a9"
            }
        }

