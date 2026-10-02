from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm  
from sqlmodel import Session, select

from backend.auth import (
    create_access_token,
    hash_password,
    verify_password,
)
from backend.database import get_session
from backend.model import User
from backend.schemas.schemas import (
    TokenResponse,
    UserCreate,
    UserResponse,
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# ==========================================
# REGISTER
# ==========================================

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register(
    user_data: UserCreate,
    session: Session = Depends(get_session)
):
    existing_user = session.exec(
        select(User).where(User.username == user_data.username)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )

    hashed_pwd = hash_password(user_data.password)

    new_user = User(
        username=user_data.username,
        hashed_password=hashed_pwd
    )

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return new_user


# ==========================================
# LOGIN (Compatible with Swagger UI Authorize button)
# ==========================================

@router.post(
    "/login",
    response_model=TokenResponse
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),  
    session: Session = Depends(get_session)
):
    # Find user using form_data.username
    user = session.exec(
        select(User).where(User.username == form_data.username)
    ).first()

    # Validate user and password
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Create JWT token
    token = create_access_token(user.username)

    return {
        "access_token": token,
        "token_type": "bearer"
    }