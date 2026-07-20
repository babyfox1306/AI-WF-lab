from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.auth.models import User
from app.auth.service import get_current_user
from app.database.database import get_db
from app.providers.schemas import ProviderCreate, ProviderResponse, ProviderTestResult, ProviderUpdate
from app.providers.service import (
    create_provider,
    delete_provider,
    get_provider,
    list_providers,
    mask_api_key,
    test_connection,
    update_provider,
)

router = APIRouter(prefix="/providers", tags=["providers"])


@router.post("/", response_model=ProviderResponse, status_code=status.HTTP_201_CREATED)
def create(data: ProviderCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Register a new provider connection."""
    provider = create_provider(db, data, current_user)
    response = ProviderResponse.model_validate(provider)
    response.api_key_masked = mask_api_key(provider)
    return response


@router.get("/", response_model=List[ProviderResponse])
def list_all(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """List all provider connections for the current user."""
    providers = list_providers(db, current_user)
    responses = []
    for p in providers:
        r = ProviderResponse.model_validate(p)
        r.api_key_masked = mask_api_key(p)
        responses.append(r)
    return responses


@router.get("/{provider_id}", response_model=ProviderResponse)
def get(provider_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get a provider connection by id."""
    provider = get_provider(db, provider_id, current_user)
    response = ProviderResponse.model_validate(provider)
    response.api_key_masked = mask_api_key(provider)
    return response


@router.patch("/{provider_id}", response_model=ProviderResponse)
def update(provider_id: int, data: ProviderUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Update a provider connection."""
    provider = update_provider(db, provider_id, data, current_user)
    response = ProviderResponse.model_validate(provider)
    response.api_key_masked = mask_api_key(provider)
    return response


@router.delete("/{provider_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(provider_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Delete a provider connection."""
    delete_provider(db, provider_id, current_user)


@router.post("/{provider_id}/test", response_model=ProviderTestResult)
def test(provider_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Test a provider connection."""
    return test_connection(db, provider_id, current_user)
