from fastapi import APIRouter, Depends , status
from sqlalchemy.orm import Session
from .. import  schemas, database, models, utils

router = APIRouter(prefix="/user", tags=["Users"])


@router.post("/", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
def create_user(user_data: schemas.UserCreate, db: Session = Depends(database.get_db)):
    hashed_password = utils.hash(user_data.password)
    user_data.password = hashed_password
    new_user = models.User(**user_data.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
