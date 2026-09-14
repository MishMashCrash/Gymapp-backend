from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import oauth2, schemas, database, models, utils
from fastapi.security.oauth2 import OAuth2PasswordRequestFormStrict
from typing import Optional, List
from sqlalchemy import or_

router = APIRouter(prefix="/exercise", tags=["Exercises"])


@router.get("/", response_model=List[schemas.ExerciseOut])
def get_exercises(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
    muscle_group: Optional[str] = None,
    joint_action: Optional[str] = None,
    movement_pattern: Optional[str] = None,
    mine: Optional[bool] = False,
):
    if mine:
        query = db.query(models.Exercise).filter(
            models.Exercise.owner_id == current_user.id,
        )
    else:
        query = db.query(models.Exercise).filter(
            or_(
                models.Exercise.owner_id == current_user.id,
                models.Exercise.type == "staple",
            )
        )

    if muscle_group:
        query = query.filter(
            or_(
                models.Exercise.primary_muscle == muscle_group,
                models.Exercise.secondary_muscle == muscle_group,
            )
        )
    if joint_action:
        query = query.filter(
            models.Exercise.joint_action == joint_action,
        )
    if movement_pattern:
        query = query.filter(
            models.Exercise.movement_pattern == movement_pattern,
        )
    return query.all


@router.get("/{id}", response_model=schemas.ExerciseOut)
def get_exercise_by_ID(
    id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
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


@router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=schemas.ExerciseOut
)
def create_exercise(
    exercise: schemas.ExerciseCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):

    new_exercise = models.Exercise(**exercise.model_dump())
    new_exercise.owner_id = current_user.id
    new_exercise.type = "custom"

    db.add(new_exercise)
    db.commit()
    db.refresh(new_exercise)

    return new_exercise
