# schemas.py
from pydantic import BaseModel, EmailStr

# Schema para criar um novo usuário
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    hashed_password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_active: bool
    is_admin: bool

    class Config:
        orm_mode = True
        from_attributes = True

# Schema para exibir informações do usuário
class User(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_active: bool
    is_admin: bool

    class Config:
        orm_mode = True
        from_attributes = True

# Schema para dados de login
class UserLogin(BaseModel):
    username: str
    hashed_password: str
