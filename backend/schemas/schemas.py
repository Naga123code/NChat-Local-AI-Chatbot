from pydantic import BaseModel, Field


# ==========================================
# AUTH SCHEMAS
# ==========================================

class UserCreate(BaseModel):
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        examples=["johndoe"]
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        examples=["SecurePass123!"]
    )


class UserResponse(BaseModel):
    id: int
    username: str

    model_config = {
        "from_attributes": True
    }


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ==========================================
# CHAT SCHEMAS
# ==========================================

class ChatRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        max_length=4000
    )


class ChatResponse(BaseModel):
    response: str