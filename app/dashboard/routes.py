from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.models import User
from app.auth.service import get_current_user
from app.dashboard.service import get_dashboard_stats
from app.database.database import get_db

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/")
def dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get dashboard statistics for the current user."""
    return get_dashboard_stats(db, current_user)
