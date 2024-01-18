from fastapi import FastAPI, Body, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
import schemas
import models 
import auth
from dependencies import get_current_active_admin, get_current_user
from database import Base, engine, get_session
from sqlalchemy.orm import Session


Base.metadata.create_all(engine)

# def get_session():
#     session = SessionLocal()
#     try:
#         yield session
#     finally:
#         session.close()

app = FastAPI()



@app.post("/register",  dependencies=[Depends(get_current_active_admin)])
#@app.post("/register", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, session: Session = Depends(get_session)):
    db_user = session.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
    hashed_password = auth.get_password_hash(user.hashed_password)  # Isso chama a função de hash da senha
    new_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,  # Use a senha hasheada
        is_active=True,
        is_admin=False,
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    
    # Aqui está a nova parte: gerar o token JWT e incluí-lo na resposta
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

@app.get("/users/{user_id}", response_model=schemas.UserRead)
def read_user(user_id: int, session: Session = Depends(get_session)):
    db_user = session.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return schemas.UserRead.model_validate(db_user)

@app.put("/users/{user_id}", dependencies=[Depends(get_current_active_admin)])
def update_user(user_id: int, user_update: schemas.UserUpdate, session: Session = Depends(get_session)):
    db_user = session.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    for var, value in vars(user_update).items():
        setattr(db_user, var, value) if value else None

    session.commit()
    session.refresh(db_user)

    # Crie uma instância de UserResponse com os dados atualizados, sem incluir os tokens
    updated_user_response = schemas.UserUpdate(
        id=db_user.id,
        username=db_user.username,
        email=db_user.email,
        is_active=db_user.is_active,
        is_admin=db_user.is_admin,
    )
    return updated_user_response

@app.delete("/users/{user_id}", dependencies=[Depends(get_current_active_admin)])
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



   



# @app.post("/users/", response_model=schemas.User)
# def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
#     fake_hashed_password = user.password + "notreallyhashed"
#     db_user = models.User(email=user.email, hashed_password=fake_hashed_password)
#     db.add(db_user)
#     db.commit()
#     db.refresh(db_user)
#     return db_user


# @app.get("/users/{user_id}", response_model=schemas.User)
# def read_user(user_id: int, db: Session = Depends(get_db)):
#     db_user = db.query(models.User).filter(models.User.id == user_id).first()
#     if db_user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     return db_user


# @app.put("/users/{user_id}", response_model=schemas.User)
# def update_user(user_id: int, user: schemas.UserCreate, db: Session = Depends(get_db)):
#     db_user = db.query(models.User).filter(models.User.id == user_id).first()
#     if db_user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     db_user.email = user.email
#     db_user.hashed_password = user.password + "notreallyhashed"  # Atualize a lógica de hashing conforme necessário
#     db.commit()
#     db.refresh(db_user)
#     return db_user


# @app.delete("/users/{user_id}", status_code=204)
# def delete_user(user_id: int, db: Session = Depends(get_db)):
#     db_user = db.query(models.User).filter(models.User.id == user_id).first()
#     if db_user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     db.delete(db_user)
#     db.commit()
#     return {"detail": "User deleted successfully"}



# Adicione aqui os demais endpoints CRUD, autenticação e permissões
