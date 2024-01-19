from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from auth import SECRET_KEY, ALGORITHM
from sqlalchemy.orm import Session
from database import get_session
import models

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")  


def get_current_user(db: Session = Depends(get_session), token: str = Depends(oauth2_scheme)) -> models.User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=400, detail="Invalid token payload")
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def get_current_active_admin(current_user: models.User = Depends(get_current_user)):
    if not current_user.is_active or not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Operation not permitted")
    return current_user
