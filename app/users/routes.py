from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.models import User
from app.auth.service import get_current_user
from app.database.database import get_db
from app.users.schemas import UserResponse, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Get the currently authenticated user's profile."""
    return current_user


@router.patch("/me", response_model=UserResponse)
def update_me(
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update the currently authenticated user's profile."""
    if data.username is not None:
        current_user.username = data.username
    if data.email is not None:
        current_user.email = data.email
    db.commit()
    db.refresh(current_user)
    return current_user
