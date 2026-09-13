from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: EmailStr

    class Config:
        from_attributes = True


class TokenData(BaseModel):
    id: Optional[int]


class Token(BaseModel):
    access_token: str
    token_type: str

class ExerciseCreate(BaseModel):
    name: str
    primary_muscle: str
    secondary_muscle: Optional[str] = None
    joint_action: Optional[str] = None
    movement_pattern: str
    notes: Optional[str] = None

class ExerciseOut(BaseModel):
    id: int
    name: str
    primary_muscle: str
    secondary_muscle: Optional[str]
    joint_action: Optional[str]
    movement_pattern: str
    type: str
    is_public: bool
    owner: UserOut
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
