import uuid
from typing import Optional
from pydantic import BaseModel, Field, EmailStr
from typing import List
from datetime import datetime


class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    firstName: str = Field(...)
    lastName: str = Field(...)
    email: EmailStr = Field(...)
    password: str = Field(...)
    age: int = Field(...)
    country: str = Field(...)
    state: str = Field(...)
    role: str = Field(default='user')
    disabled: bool = Field(default=False)

    class Config:
        json_schema_extra = {
            "example": {
                "firstName": "John",
                "lastName": "Doe",
                "email": "example@example.com",
                "password": "123456",
                "age": 30,
                "country": "Mexico",
                "state": "CDMX",
                "role": "user",
                "disabled": False
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
                "userId": "9739f411-76c8-4260-9217-a8b4b32b299a"
            }
        }


class FrequentlyAskedQuestion(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    question: str = Field(...)
    answer: str = Field(...)

    class Config:
        json_schema_extra = {
            "example": {
                "question": "What is NEORIS?",
                "answer": "NEORIS is a global business and IT consulting company"
            }
        }


class EditQuestion(BaseModel):
    question: str = Field(...)
    answer: str = Field(...)

    class Config:
        json_schema_extra = {
            "example": {
                "question": "What is NEORIS?",
                "answer": "NEORIS is a global business and IT consulting company"
            }
        }
