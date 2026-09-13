from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import ouath2, schemas, database, models, utils
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

router = APIRouter(tags=["Authentication"])


@router.post("/login", response_model=schemas.Token)
def login(
    db: Session = Depends(database.get_db),
    user_credential: OAuth2PasswordRequestForm = Depends(),
):
    user = (
        db.query(models.User)
        .filter(models.User.email == user_credential.username)
        .first()
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid login credentials"
        )
    if not utils.verify(user_credential.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid login credentials"
        )
    access_token = ouath2.create_token(data={"user_id": user.id})
    return {"access_token" : access_token, "token_type": "bearer"}
