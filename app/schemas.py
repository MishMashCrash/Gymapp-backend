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
    id: Optional[int] = None


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
    secondary_muscle: Optional[str] = None
    joint_action: Optional[str] = None
    movement_pattern: str
    type: str
    is_public: bool
    owner: Optional[UserOut] = None
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ExerciseUpdate(BaseModel):
    name: Optional[str] = None
    primary_muscle: Optional[str] = None
    secondary_muscle: Optional[str] = None
    joint_action: Optional[str] = None
    movement_pattern: Optional[str] = None
    notes: Optional[str] = None


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
    exercises: List[SplitDayExerciseOut]
    created_at: datetime

    class Config:
        from_attributes = True


class SplitOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    owner: UserOut
    days: List[SplitDayOut]
    created_at: datetime

    class Config:
        from_attributes = True


class SplitPut(BaseModel):
    name: str
    description: Optional[str] = None
    days: List[SplitDayCreate] = []


class SplitUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class SplitDayAdd(BaseModel):
    name: str
    order: int
    exercises: List[SplitDayExerciseCreate] = []


class SplitDayUpdate(BaseModel):
    name: Optional[str] = None
    order: Optional[int] = None


class SplitDayExerciseAdd(BaseModel):
    exercise_id: int
    order: int
    target_sets: Optional[int] = None
    target_reps: Optional[str] = None


class SplitDayExerciseUpdate(BaseModel):
    order: Optional[int] = None
    target_sets: Optional[int] = None
    target_reps: Optional[str] = None


class WorkoutSetCreate(BaseModel):
    exercise_id: int
    set_number: int
    reps: int
    weight: float
    rpe: Optional[float] = None


class WorkoutCreate(BaseModel):
    split_day_id: Optional[int] = None
    notes: Optional[str] = None
    sets: List[WorkoutSetCreate] = []


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
    owner: UserOut
    split_day_id: Optional[int]
    date: datetime
    notes: Optional[str]
    sets: List[WorkoutSetOut]

    class Config:
        from_attributes = True

class WorkoutUpdate(BaseModel):
    split_day_id: Optional[int] = None
    notes: Optional[str] = None

class WorkoutSetAdd(BaseModel):
    exercise_id: int
    set_number: int
    reps: int
    weight: float
    rpe: Optional[float] = None


class WorkoutSetUpdate(BaseModel):
    set_number: Optional[int] = None
    reps: Optional[int] = None
    weight: Optional[float] = None
    rpe: Optional[float] = None