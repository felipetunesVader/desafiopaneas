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



Base.metadata.create_all(engine)

app = FastAPI()

@app.post("/register", response_model=schemas.UserResponse)
# @app.post("/register", 
#           response_model=schemas.UserResponse, 
#           status_code=status.HTTP_201_CREATED,
#           dependencies=[Depends(get_current_active_admin)],
#           responses={
#               201: {
#                   "description": "User successfully created",
#                   "content": {
#                       "application/json": {
#                           "example": {
#                               "id": 1,
#                               "username": "felipetunes",
#                               "email": "jota@example.com",
#                               "is_active": True,
#                               "is_admin": False,
#                               "access_token": "fake-jwt-token",
#                               "token_type": "bearer"
#                           }
#                       }
#                   },
#               },
#               400: {
#                   "description": "Email already registered",
#                   "content": {
#                       "application/json": {
#                           "example": {"detail": "Email already registered"}
#                       }
#                   },
#               }
#           })
def create_user(user: schemas.UserCreate, session: Session = Depends(get_session)):
    db_user = session.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
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
    session.commit()
    session.refresh(new_user)
    
    access_token = auth.create_access_token(data={"sub": new_user.username})
    user_dict = jsonable_encoder(new_user)
    send_confirmation_email.delay(user.email)
    return {
        "id": user_dict["id"],
        "username": user_dict["username"],
        "email": user_dict["email"],
        "is_active": user_dict["is_active"],
        "is_admin": user_dict["is_admin"],
        # "access_token": access_token,
        # "token_type": "bearer"
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
    db_users = session.query(models.User).all()
    users = [schemas.UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        is_active=user.is_active,
        is_admin=user.is_admin
    ) for user in db_users]
    return users

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
    db_user = session.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    for var, value in vars(user_update).items():
        setattr(db_user, var, value) if value else None

    session.commit()
    session.refresh(db_user)

    
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
    db_user = session.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    session.delete(db_user)
    session.commit()
    deleted_user_response = schemas.UserDeletedResponse(
        id=db_user.id,
        username=db_user.username,
    )
    return deleted_user_response

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_session)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}



   



