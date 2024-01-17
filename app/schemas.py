# schemas.py
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    hashed_password: str

class UserUpdate(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    is_active: bool | None = None
    is_admin: bool | None = None
    
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
