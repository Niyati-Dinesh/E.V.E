from pydantic import BaseModel, EmailStr, Field


# ---------- REQUEST SCHEMAS ----------

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# ---------- RESPONSE SCHEMAS ----------

class UserResponse(BaseModel):
    user_id: int
    email: EmailStr
    role: str


class MessageResponse(BaseModel):
    message: str
