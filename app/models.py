from .database import Base
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    TIMESTAMP,
    text,
    ForeignKey,
    Float,
)
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    is_admin = Column(Boolean, nullable=False, server_default="false")
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )


class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    primary_muscle = Column(String, nullable=False)
    secondary_muscle = Column(String)
    joint_action = Column(String)
    movement_pattern = Column(String, nullable=False)
    type = Column(String, nullable=False, server_default="custom")
    is_public = Column(Boolean, nullable=False, server_default="False")
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    owner = relationship("User")
    notes = Column(String)
    is_active = Column(Boolean, nullable=False, server_default="true")
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )


class Split(Base):
    __tablename__ = "splits"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    owner_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    owner = relationship("User")
    description = Column(String)
    type = Column(String, nullable=False, server_default="custom")
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    days = relationship(
        "SplitDay", back_populates="split", cascade="all, delete-orphan"
    )


class SplitDay(Base):
    __tablename__ = "split_days"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    order = Column(Integer, nullable=False)
    split_id = Column(
        Integer, ForeignKey("splits.id", ondelete="CASCADE"), nullable=False
    )
    split = relationship("Split", back_populates="days")
    exercises = relationship(
        "SplitDayExercise", back_populates="split_day", cascade="all, delete-orphan"
    )
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )


class SplitDayExercise(Base):
    __tablename__ = "split_day_exercises"

    id = Column(Integer, primary_key=True, nullable=False)
    split_day_id = Column(
        Integer, ForeignKey("split_days.id", ondelete="CASCADE"), nullable=False
    )
    exercise_id = Column(
        Integer, ForeignKey("exercises.id", ondelete="CASCADE"), nullable=False
    )
    order = Column(Integer, nullable=False)
    target_sets = Column(Integer)
    target_reps = Column(String)

    split_day = relationship("SplitDay", back_populates="exercises")
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    exercise = relationship("Exercise")


class Workout(Base):
    __tablename__ = "workouts"

    id = Column(Integer, primary_key=True, nullable=False)
    split_day_id = Column(
        Integer, ForeignKey("split_days.id", ondelete="CASCADE"), nullable=True
    )
    owner_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    date = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    notes = Column(String)

    split_day = relationship("SplitDay")
    sets = relationship(
        "WorkoutSet", back_populates="workout", cascade="all, delete-orphan"
    )
    owner = relationship("User")


class WorkoutSet(Base):
    __tablename__ = "workout_sets"

    id = Column(Integer, primary_key=True, index=True)
    workout_id = Column(
        Integer, ForeignKey("workouts.id", ondelete="CASCADE"), nullable=False
    )
    exercise_id = Column(
        Integer, ForeignKey("exercises.id", ondelete="CASCADE"), nullable=False
    )
    set_number = Column(Integer, nullable=False)
    reps = Column(Integer, nullable=False)
    weight = Column(Float, nullable=False)
    rpe = Column(Integer)

    workout = relationship("Workout", back_populates="sets")
    exercise = relationship("Exercise")
