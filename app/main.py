from fastapi import FastAPI, Body, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
import schemas
import models 
import auth
from dependencies import get_current_active_admin, get_current_user
from database import Base, engine, get_session
from typing import List
from sqlalchemy.orm import Session
from celery_app import send_confirmation_email
import logging
from logging.handlers import SocketHandler
import json
from pythonjsonlogger import jsonlogger



logger = logging.getLogger('uvicorn')
logger.setLevel(logging.INFO)

logstash_handler = logging.handlers.SocketHandler('logstash', 5000)

formatter = jsonlogger.JsonFormatter()  # Usa a biblioteca python-json-logger para formatar em JSON
logstash_handler.setFormatter(formatter)

logger.addHandler(logstash_handler)



Base.metadata.create_all(engine)

app = FastAPI()

@app.post("/register", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, session: Session = Depends(get_session)):
                                                      
    db_user = session.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        logger.warning(f"Attempt to register with an already registered email: {user.email}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
    
    hashed_password = auth.get_password_hash(user.hashed_password)
    is_admin = session.query(models.User).count() == 0
    new_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        is_active=True,
        is_admin=is_admin,  
    )
    
    session.add(new_user)
    try:
        session.commit()
        session.refresh(new_user)
        logger.info(f"User {new_user.username} successfully registered with email {new_user.email}")
    except Exception as e:
        session.rollback()
        logger.error(f"Error occurred while registering user {user.email}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
    
    
    try:
        send_confirmation_email.delay(user.email)
        logger.info(f"Confirmation email sent to {user.email}")
    except Exception as e:
        logger.error(f"Failed to send confirmation email to {user.email}: {e}")
    
    
    access_token = auth.create_access_token(data={"sub": new_user.username})
    user_dict = jsonable_encoder(new_user)
    return {
        "id": user_dict["id"],
        "username": user_dict["username"],
        "email": user_dict["email"],
        "is_active": user_dict["is_active"],
        "is_admin": user_dict["is_admin"],
        
    }
    
    
    access_token = auth.create_access_token(data={"sub": new_user.username})
    user_dict = jsonable_encoder(new_user)
    return {
        "id": user_dict["id"],
        "username": user_dict["username"],
        "email": user_dict["email"],
        "is_active": user_dict["is_active"],
        "is_admin": user_dict["is_admin"],
        "access_token": access_token,
        "token_type": "bearer"
    }

@app.get("/users", response_model=List[schemas.UserResponse])
def get_users(session: Session = Depends(get_session)):
    logger.info("Fetching all users.")
    try:
        db_users = session.query(models.User).all()
        users = [schemas.UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            is_active=user.is_active,
            is_admin=user.is_admin
        ) for user in db_users]
        logger.info(f"Successfully fetched {len(users)} users.")
        test_log = {"status": "test", "message": "This is a test log."}
        logger.info(json.dumps(test_log))

        return users
    except Exception as e:
        logger.error(f"Error fetching users: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.put("/users/{user_id}", response_model=schemas.UserUpdate, 
         dependencies=[Depends(get_current_active_admin)],
         responses={
             200: {
                 "description": "User successfully updated",
                 "content": {
                     "application/json": {
                         "example": {
                             "id": 1,
                             "username": "newfelipe",
                             "email": "newjota@example.com",
                             "is_active": True,
                             "is_admin": False
                         }
                     }
                 },
             },
             404: {
                 "description": "User not found",
                 "content": {
                     "application/json": {
                         "example": {"detail": "User not found"}
                     }
                 },
             }
         }) 
def update_user(user_id: int, user_update: schemas.UserUpdate, session: Session = Depends(get_session)):
    logger.info(f"Attempting to update user with id: {user_id}")
    db_user = session.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        logger.warning(f"User with id {user_id} not found for update.")
        raise HTTPException(status_code=404, detail="User not found")

    for var, value in vars(user_update).items():
        if value is not None:
            setattr(db_user, var, value)
            logger.debug(f"Updated {var} for user {user_id}")

    session.commit()
    session.refresh(db_user)
    logger.info(f"User with id {user_id} successfully updated.")

    updated_user_response = schemas.UserUpdate(
        id=db_user.id,
        username=db_user.username,
        email=db_user.email,
        is_active=db_user.is_active,
        is_admin=db_user.is_admin,
    )
    return updated_user_response

@app.delete("/users/{user_id}", 
            dependencies=[Depends(get_current_active_admin)],
            responses={
                200: {
                    "description": "User successfully deleted",
                    "content": {
                        "application/json": {
                            "example": {
                                "id": 1,
                                "username": "deleteduser"
                            }
                        }
                    },
                },
                404: {
                    "description": "User not found",
                    "content": {
                        "application/json": {
                            "example": {"detail": "User not found"}
                        }
                    },
                }
            })
def delete_user(user_id: int, session: Session = Depends(get_session)):
    logger.info(f"Attempting to delete user with id: {user_id}")
    db_user = session.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        logger.warning(f"User with id {user_id} not found for deletion.")
        raise HTTPException(status_code=404, detail="User not found")

    session.delete(db_user)
    try:
        session.commit()
        logger.info(f"User with id {user_id} successfully deleted.")
    except Exception as e:
        session.rollback()
        logger.error(f"Error occurred while deleting user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

    deleted_user_response = schemas.UserDeletedResponse(
        id=db_user.id,
        username=db_user.username,
    )
    return deleted_user_response

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_session)):
    logger.info(f"Login attempt for username: {form_data.username}")
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        logger.warning(f"Invalid login credentials for username: {form_data.username}")
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    access_token = auth.create_access_token(data={"sub": user.username})
    logger.info(f"User {form_data.username} successfully logged in.")
    return {"access_token": access_token, "token_type": "bearer"}


   



