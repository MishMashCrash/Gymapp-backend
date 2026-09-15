from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import oauth2, schemas, database, models, utils
from sqlalchemy import or_
from typing import List

router = APIRouter(prefix="/workout", tags=["Workouts"])


@router.post(
    "/", response_model=schemas.WorkoutOut, status_code=status.HTTP_201_CREATED
)
def create_workout_nested(
    workout: schemas.WorkoutCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    requested_exercise_ids = {
        requested_set.exercise_id for requested_set in workout.sets
    }
    invalid_ids = utils.get_inaccessible_exercise_ids(
        requested_exercise_ids, current_user, db
    )
    if invalid_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Could not fetch exercise ids: {sorted(invalid_ids)}",
        )
    if workout.split_day_id is not None:
        split_day = (
            db.query(models.SplitDay)
            .join(models.Split)
            .filter(
                models.SplitDay.id == workout.split_day_id,
                or_(
                models.Split.owner_id == current_user.id,
                models.Split.type == "staple",
            )
            )
            .first()
        )
        if split_day is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid or inaccessible split_day_id",
            )
    new_workout = models.Workout(
        owner_id=current_user.id,
        split_day_id=workout.split_day_id,
        notes=workout.notes,
    )
    db.add(new_workout)
    db.flush()

    for set_data in workout.sets:
        new_set = models.WorkoutSet(
            workout_id=new_workout.id,
            exercise_id=set_data.exercise_id,
            set_number=set_data.set_number,
            reps=set_data.reps,
            weight=set_data.weight,
            rpe=set_data.rpe,
        )
        db.add(new_set)

    db.commit()
    db.refresh(new_workout)
    return new_workout


@router.get("/", response_model=List[schemas.WorkoutOut])
def get_exercises(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    workouts = (
        db.query(models.Workout)
        .filter(models.Workout.owner_id == current_user.id)
        .all()
    )
    return workouts


@router.get("/{id}", response_model=schemas.WorkoutOut)
def get_workout_by_ID(
    id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    workout = (
        db.query(models.Workout)
        .filter(models.Workout.id == id, models.Workout.owner_id == current_user.id)
        .first()
    )

    if workout is not None:
        return workout
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"workout with id: {id} was not found",
        )


@router.patch("/{id}", response_model=schemas.WorkoutOut)
def update_workout(
    id: int,
    updates: schemas.WorkoutUpdate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    workout = (
        db.query(models.Workout)
        .filter(models.Workout.id == id, models.Workout.owner_id == current_user.id)
        .first()
    )
    if workout is None:
        raise HTTPException(
            status_code=404, detail=f"workout with id: {id} was not found"
        )

    update_data = updates.model_dump(exclude_unset=True)

    if "split_day_id" in update_data and update_data["split_day_id"] is not None:
        split_day = (
            db.query(models.SplitDay)
            .join(models.Split)
            .filter(
                models.SplitDay.id == update_data["split_day_id"],
                or_(
                models.Split.owner_id == current_user.id,
                models.Split.type == "staple",
            )
            )
            .first()
        )
        if split_day is None:
            raise HTTPException(
                status_code=403, detail="Invalid or inaccessible split_day_id"
            )

    for key, value in update_data.items():
        setattr(workout, key, value)

    db.commit()
    db.refresh(workout)
    return workout


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workout(
    id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    workout = (
        db.query(models.Workout)
        .filter(models.Workout.id == id, models.Workout.owner_id == current_user.id)
        .first()
    )
    if workout is None:
        raise HTTPException(
            status_code=404, detail=f"workout with id: {id} was not found"
        )

    db.delete(workout)
    db.commit()


@router.post(
    "/{workout_id}/sets",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.WorkoutSetOut,
)
def add_workout_set(
    workout_id: int,
    set_data: schemas.WorkoutSetAdd,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    workout = (
        db.query(models.Workout)
        .filter(
            models.Workout.id == workout_id, models.Workout.owner_id == current_user.id
        )
        .first()
    )
    if workout is None:
        raise HTTPException(status_code=404, detail="Workout not found")

    invalid_ids = utils.get_inaccessible_exercise_ids(
        {set_data.exercise_id}, current_user, db
    )
    if invalid_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Could not fetch exercise ids: {sorted(invalid_ids)}",
        )

    new_set = models.WorkoutSet(
        workout_id=workout.id,
        exercise_id=set_data.exercise_id,
        set_number=set_data.set_number,
        reps=set_data.reps,
        weight=set_data.weight,
        rpe=set_data.rpe,
    )
    db.add(new_set)
    db.commit()
    db.refresh(new_set)
    return new_set


@router.get("/{workout_id}/sets/{set_id}", response_model=schemas.WorkoutSetOut)
def get_workout_set(
    workout_id: int,
    set_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    workout_set = (
        db.query(models.WorkoutSet)
        .join(models.Workout)
        .filter(
            models.WorkoutSet.id == set_id,
            models.WorkoutSet.workout_id == workout_id,
            models.Workout.owner_id == current_user.id,
        )
        .first()
    )
    if workout_set is None:
        raise HTTPException(status_code=404, detail="Workout set not found")
    return workout_set


@router.patch("/{workout_id}/sets/{set_id}", response_model=schemas.WorkoutSetOut)
def update_workout_set(
    workout_id: int,
    set_id: int,
    updates: schemas.WorkoutSetUpdate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    workout_set = (
        db.query(models.WorkoutSet)
        .join(models.Workout)
        .filter(
            models.WorkoutSet.id == set_id,
            models.WorkoutSet.workout_id == workout_id,
            models.Workout.owner_id == current_user.id,
        )
        .first()
    )
    if workout_set is None:
        raise HTTPException(status_code=404, detail="Workout set not found")

    update_data = updates.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(workout_set, key, value)

    db.commit()
    db.refresh(workout_set)
    return workout_set

@router.delete("/{workout_id}/sets/{set_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workout_set(
    workout_id: int,
    set_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    workout_set = (
        db.query(models.WorkoutSet)
        .join(models.Workout)
        .filter(
            models.WorkoutSet.id == set_id,
            models.WorkoutSet.workout_id == workout_id,
            models.Workout.owner_id == current_user.id,
        )
        .first()
    )
    if workout_set is None:
        raise HTTPException(status_code=404, detail="Workout set not found")

    db.delete(workout_set)
    db.commit()