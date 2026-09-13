from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import schemas, database, models, utils, outh2
from fastapi.security.oauth2 import OAuth2PasswordRequestFormStrict
from typing import List
from sqlalchemy import or_

router = APIRouter(prefix="/exercise", tags=["Exercises"])


@router.get("/", response_model=List[schemas.ExerciseOut])
def get_exercises(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(outh2.get_current_user),
):
    results = (
        db.query(models.Exercise)
        .filter(
            or_(
                models.Exercise.owner_id == current_user.id,
                models.Exercise.type == "staple",
            )
        )
        .all()
    
    )
    return results