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

    invalid_ids = utils.get_inaccessible_exercise_ids(
        requested_exercise_ids, current_user, db
    )

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
def get_splits(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    splits = (
        db.query(models.Split).filter(models.Split.owner_id == current_user.id).all()
    )
    return splits


@router.get("/{id}", response_model=schemas.SplitOut)
def get_split_by_ID(
    id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    split = (
        db.query(models.Split)
        .filter(models.Split.id == id, models.Split.owner_id == current_user.id)
        .first()
    )

    if split is not None:
        return split
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"split with id: {id} was not found",
        )


@router.put("/{id}", response_model=schemas.SplitOut)
def replace_split(
    id: int,
    split: schemas.SplitPut,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    split = (
        db.query(models.Split)
        .filter(models.Split.id == id, models.Split.owner_id == current_user.id)
        .first()
    )
    if split is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"split with id: {id} was not found",
        )

    requested_exercise_ids = {
        ex.exercise_id for day in split.days for ex in day.exercises
    }
    invalid_ids = utils.get_inaccessible_exercise_ids(
        requested_exercise_ids, current_user, db
    )
    if invalid_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Could not fetch exercise ids: {sorted(invalid_ids)}",
        )

    split.name = split.name
    split.description = split.description

    split.days.clear()
    db.flush()

    for day in split.days:
        new_day = models.SplitDay(
            name=day.name, order=day.order, split_id=split.id
        )
        db.add(new_day)
        db.flush()

        for new_exercise in day.exercises:
            db.add(
                models.SplitDayExercise(
                    split_day_id=new_day.id,
                    exercise_id=new_exercise.exercise_id,
                    order=new_exercise.order,
                    target_sets=new_exercise.target_sets,
                    target_reps=new_exercise.target_reps,
                )
            )

    db.commit()
    db.refresh(split)
    return split


@router.patch("/{id}", response_model=schemas.SplitOut)
def update_split(
    id: int,
    updates: schemas.SplitUpdate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    split = (
        db.query(models.Split)
        .filter(models.Split.id == id, models.Split.owner_id == current_user.id)
        .first()
    )
    if split is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"split with id: {id} was not found",
        )

    update_data = updates.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(split, key, value)

    db.commit()
    db.refresh(split)
    return split


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_split(
    id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    split = (
        db.query(models.Split)
        .filter(models.Split.id == id, models.Split.owner_id == current_user.id)
        .first()
    )
    if split is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"split with id: {id} was not found",
        )

    db.delete(split)
    db.commit()

#---------------SplitDays---------------

@router.get("/{split_id}/days/{day_id}", response_model=schemas.SplitDayOut)
def get_split_day(
    split_id: int,
    day_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    day = (
        db.query(models.SplitDay)
        .join(models.Split)
        .filter(
            models.SplitDay.id == day_id,
            models.SplitDay.split_id == split_id,
            models.Split.owner_id == current_user.id,
        )
        .first()
    )
    if day is None:
        raise HTTPException(status_code=404, detail="Split day not found")
    return day


@router.post(
    "/{split_id}/days",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.SplitDayOut,
)
def add_split_day(
    split_id: int,
    day: schemas.SplitDayAdd,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    split = (
        db.query(models.Split)
        .filter(models.Split.id == split_id, models.Split.owner_id == current_user.id)
        .first()
    )
    if split is None:
        raise HTTPException(status_code=404, detail="Split not found")

    requested_exercise_ids = {ex.exercise_id for ex in day.exercises}
    invalid_ids = utils.get_inaccessible_exercise_ids(
        requested_exercise_ids, current_user, db
    )
    if invalid_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Could not fetch exercise ids: {sorted(invalid_ids)}",
        )

    new_day = models.SplitDay(
        name=day.name, order=day.order, split_id=split.id
    )
    db.add(new_day)
    db.flush()

    for new_exercise in day.exercises:
        db.add(
            models.SplitDayExercise(
                split_day_id=new_day.id,
                exercise_id=new_exercise.exercise_id,
                order=new_exercise.order,
                target_sets=new_exercise.target_sets,
                target_reps=new_exercise.target_reps,
            )
        )

    db.commit()
    db.refresh(new_day)
    return new_day

@router.patch("/{split_id}/days/{day_id}", response_model=schemas.SplitDayOut)
def update_split_day(
    split_id: int,
    day_id: int,
    updates: schemas.SplitDayUpdate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    day = (
        db.query(models.SplitDay)
        .join(models.Split)
        .filter(
            models.SplitDay.id == day_id,
            models.SplitDay.split_id == split_id,
            models.Split.owner_id == current_user.id,
        )
        .first()
    )
    if day is None:
        raise HTTPException(status_code=404, detail="Split day not found")

    update_data = updates.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(day, key, value)

    db.commit()
    db.refresh(day)
    return day

@router.delete("/{split_id}/days/{day_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_split_day(
    split_id: int,
    day_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    day = (
        db.query(models.SplitDay)
        .join(models.Split)
        .filter(
            models.SplitDay.id == day_id,
            models.SplitDay.split_id == split_id,
            models.Split.owner_id == current_user.id,
        )
        .first()
    )
    if day is None:
        raise HTTPException(status_code=404, detail="Split day not found")

    db.delete(day)
    db.commit()