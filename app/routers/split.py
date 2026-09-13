from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import oauth2, schemas, database, models, utils
from sqlalchemy import or_
from typing import List

router = APIRouter(prefix="/split", tags=["Splits"])


@router.post("/", response_model=schemas.SplitOut, status_code=status.HTTP_201_CREATED)
def create_split_nested(
    split: schemas.SplitCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    requested_exercise_ids = {
        requested_exercise.exercise_id
        for requested_day in split.days
        for requested_exercise in requested_day.exercises
    }

    if requested_exercise_ids:
        accessible_exercises = (
            db.query(models.Exercise.id)
            .filter(
                models.Exercise.id.in_(requested_exercise_ids),
                or_(
                    models.Exercise.id == current_user.id,
                    models.Exercise.type == "staple",
                ),
            )
            .all()
        )
        accessible_ids = {row.id for row in accessible_exercises}
        invalid_ids = requested_exercise_ids - accessible_ids

        if invalid_ids:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Could not fetch exercise ids: {sorted(invalid_ids)}",
            )

    new_split = models.Split(
        name=split.name, description=split.description, owner_id=current_user.id
    )
    db.add(new_split)
    db.flush()

    for day in split.days:
        new_day = models.SplitDay(name=day.name, order=day.order, split_id=new_split.id)
        db.add(new_day)
        db.flush()

        for exercise in day.exercises:
            new_exercise = models.SplitDayExercise(
                split_day_id=new_day.id,
                exercise_id=exercise.exercise_id,
                order=exercise.order,
                target_sets=exercise.target_sets,
                target_reps=exercise.target_reps,
            )
            db.add(new_exercise)
    db.commit()
    db.refresh(new_split)
    return new_split


@router.get("/", response_model=List[schemas.SplitOut])
def get_exercises(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    splits = (
        db.query(models.Split).filter(models.Split.owner_id == current_user.id).all()
    )
    return splits
