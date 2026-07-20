from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.auth.schemas import TokenResponse, UserLogin, UserRegister, UserResponse
from app.auth.service import (
    authenticate_user,
    create_access_token,
    register_user,
)
from app.database.database import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user account."""
    return register_user(db, data)


@router.post("/login", response_model=TokenResponse)
def login(data: UserLogin, db: Session = Depends(get_db)):
    """Authenticate and return a JWT token."""
    user = authenticate_user(db, data.email, data.password)
    token = create_access_token(data={"sub": str(user.id)})
    return TokenResponse(access_token=token)
