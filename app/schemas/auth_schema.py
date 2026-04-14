from pydantic import BaseModel, EmailStr

class MessageResponse(BaseModel):
    message: str

class loginRequest(BaseModel):
    email: EmailStr
    password: str

class UserLoginInfo(BaseModel):
    id: int
    name: str
    email: str
    role: str
    status: str

class LoginResponse(BaseModel):
    message: str
    user: UserLoginInfo

class forgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str
    confirm_password: str
