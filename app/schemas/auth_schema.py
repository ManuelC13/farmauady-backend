from pydantic import BaseModel, EmailStr

class loginRequest(BaseModel):
    email: EmailStr
    password: str

class loginResponse(BaseModel):
    message: str

class forgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str
    confirm_password: str