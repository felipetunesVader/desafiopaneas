from pydantic import BaseModel, EmailStr, validator, Field
import re

# Schema for user creation
class UserCreate(BaseModel):
    username: str = Field(..., example="felipeantunes", description="The unique username for the user.")
    email: EmailStr = Field(..., example="jota@example.com", description="The email address of the user.")
    hashed_password: str = Field(..., example="hashedpassword", description="The hashed password for the user.")

    @validator('username')
    def validate_username(cls, value):
        if not re.match('^([a-z]|[0-9])+$', value):
            raise ValueError('Username format is invalid. Only lowercase letters and numbers are allowed.')
        return value

# Schema for user update
class UserUpdate(BaseModel):
    username: str | None = Field(default=None, example="newfelipe", description="The new username for the user if you wish to change it.")
    email: EmailStr | None = Field(default=None, example="newjota@example.com", description="The new email address for the user if you wish to change it.")
    is_active: bool | None = Field(default=None, example=True, description="Indicates whether the user is active or not.")
    is_admin: bool | None = Field(default=None, example=False, description="Indicates whether the user has admin privileges or not.")
    
# Schema for user response
class UserResponse(BaseModel):
    id: int = Field(..., example=1, description="The unique ID of the user.")
    username: str = Field(..., example="felipeantunes", description="The username of the user.")
    email: EmailStr = Field(..., example="jota@example.com", description="The email address of the user.")
    is_active: bool = Field(..., example=True, description="Indicates whether the user is active or not.")
    is_admin: bool = Field(..., example=False, description="Indicates whether the user has admin privileges or not.")
    access_token: str = Field(..., example="your_jwt_token_here", description="The JWT access token for user authentication.")
    token_type: str = Field(..., example="bearer", description="The type of the access token, typically 'bearer'.")

    class Config:
        orm_mode = True
        

# Schema for displaying user information
class UserRead(BaseModel):
    id: int = Field(..., example=1, description="The unique ID of the user.")
    username: str = Field(..., example="felipeantunes", description="The username of the user.")
    email: EmailStr = Field(..., example="jota@example.com", description="The email address of the user.")
    is_active: bool = Field(..., example=True, description="Indicates whether the user is active or not.")
    is_admin: bool = Field(..., example=False, description="Indicates whether the user has admin privileges or not.")

    class Config:
        orm_mode = True

# Schema for login data
class UserLogin(BaseModel):
    username: str = Field(..., example="felipeantunes", description="The username of the user for login.")
    hashed_password: str = Field(..., example="hashedpassword", description="The hashed password of the user for login.")

# Schema for response when a user is deleted
class UserDeletedResponse(BaseModel):
    username: str = Field(..., example="felipeantunes", description="The username of the user that was deleted.")
