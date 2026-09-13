from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import ouath2, schemas, database, models, utils
from fastapi.security.oauth2 import OAuth2PasswordRequestFormStrict
from typing import List
from sqlalchemy import or_

router = APIRouter(prefix="/exercise", tags=["Exercises"])


@router.get("/", response_model=List[schemas.ExerciseOut])
def get_exercises(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(ouath2.get_current_user),
):
    exercises = (
        db.query(models.Exercise)
        .filter(
            or_(
                models.Exercise.owner_id == current_user.id,
                models.Exercise.type == "staple",
            )
        )
        .all()
    )
    return exercises


@router.get("/{id}", response_model=schemas.ExerciseOut)
def get_exercise_by_ID(
    id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(ouath2.get_current_user),
):
    exercise = (
        db.query(models.Exercise)
        .filter(
            models.Exercise.id == id,
            or_(
                models.Exercise.owner_id == current_user.id,
                models.Exercise.type == "staple",
            ),
        )
        .first()
    )

    if exercise is not None:
        return exercise
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"exercise with id: {id} was not found",
        )
