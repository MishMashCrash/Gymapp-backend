from passlib.context import CryptContext
from . import models
from sqlalchemy.orm import Session
from sqlalchemy import or_

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash(password: str):
    return pwd_context.hash(password)

def verify(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_inaccessible_exercise_ids(exercise_ids: set[int],
    current_user: models.User,
    db: Session,
) -> set[int]:
    if not exercise_ids:
        return set()
    
    accessible_ids = {
    row.id
    for row in db.query(models.Exercise.id)
    .filter(
        models.Exercise.id.in_(exercise_ids),
        models.Exercise.is_active == True,
        or_(
            models.Exercise.owner_id == current_user.id,
            models.Exercise.type == "staple",
        ),
    )
    .all()
}
    return exercise_ids - accessible_ids