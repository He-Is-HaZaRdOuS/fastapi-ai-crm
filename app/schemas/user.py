from pydantic import BaseModel, EmailStr, ValidationInfo, field_validator


class UserCreate(BaseModel):
    email: EmailStr
    password: str

    @field_validator('email')
    def lowercase_email(cls, value: str, info: ValidationInfo):
        return value.lower()


class UserOut(BaseModel):
    id: int
    email: EmailStr

    class Config:
        from_attributes = True

class PasswordChange(BaseModel):
    current_password: str
    new_password: str
    new_password_confirm: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
