from fastapi import FastAPI, Body, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
import schemas
import models 
import auth
from database import Base, engine, SessionLocal
from sqlalchemy.orm import Session


Base.metadata.create_all(engine)

def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

app = FastAPI()



@app.post("/register", response_model=schemas.UserResponse)
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

@app.get("/users/{user_id}", response_model=schemas.UserResponse)
def read_user(user_id: int, session: Session = Depends(get_session)):
    db_user = session.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return schemas.UserResponse.model_validate(db_user)

@app.put("/users/{user_id}", response_model=schemas.UserResponse)
def update_user(user_id: int, user_update: schemas.UserUpdate, session: Session = Depends(get_session)):
    db_user = session.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    for var, value in vars(user_update).items():
        setattr(db_user, var, value) if value else None

    session.commit()
    session.refresh(db_user)
    return schemas.UserResponse.model_validate(db_user)

@app.delete("/users/{user_id}", response_model=schemas.UserResponse)
def delete_user(user_id: int, session: Session = Depends(get_session)):
    db_user = session.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    session.delete(db_user)
    session.commit()
    return schemas.UserResponse.model_validate(db_user)



   



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
