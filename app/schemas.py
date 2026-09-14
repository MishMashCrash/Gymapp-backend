from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
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


class SplitDayExerciseCreate(BaseModel):
    exercise_id: int
    order: int
    target_sets: Optional[int] = None
    target_reps: Optional[str] = None


class SplitDayCreate(BaseModel):
    name: str
    order: int
    exercises: List[SplitDayExerciseCreate]


class SplitCreate(BaseModel):
    name: str
    description: Optional[str] = None
    days: List[SplitDayCreate]


class SplitDayExerciseOut(BaseModel):
    id: int
    exercise: ExerciseOut
    order: int
    target_sets: Optional[int] = None
    target_reps: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class SplitDayOut(BaseModel):
    id: int
    name: str
    order: int
    exercises: List[SplitDayExerciseCreate]
    created_at: datetime

    class Config:
        from_attributes = True


class SplitOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    owner: UserOut
    days: List[SplitDayCreate]
    created_at: datetime

    class Config:
        from_attributes = True

class WorkoutSetCreate(BaseModel):
    exercise_id: int
    set_number: int
    reps: int
    weight: float
    rpe: Optional[float] = None

class WorkoutCreate(BaseModel):
    split_day_id: Optional[int] = None
    notes: Optional[str] = None
    sets: List[WorkoutSetCreate] = Field(min_length=1)

class WorkoutSetOut(BaseModel):
    id: int
    exercise: ExerciseOut
    set_number: int
    reps: int
    weight: float
    rpe: Optional[float]

    class Config:
        from_attributes = True


class WorkoutOut(BaseModel):
    id: int
    owner_id: int
    split_day_id: Optional[int]
    date: datetime
    notes: Optional[str]
    sets: List[WorkoutSetOut]

    class Config:
        from_attributes = True