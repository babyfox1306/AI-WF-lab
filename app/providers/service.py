from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.auth.models import User
from app.providers.encryption import encryption_service
from app.providers.models import ProviderConnection
from app.providers.schemas import ProviderCreate, ProviderTestResult, ProviderUpdate


def _not_found(provider_id: int) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Provider with id {provider_id} not found",
    )


def _check_owner(provider: ProviderConnection, user: User) -> None:
    if provider.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")


def create_provider(db: Session, data: ProviderCreate, user: User) -> ProviderConnection:
    """Create a new provider connection."""
    provider = ProviderConnection(
        owner_id=user.id,
        name=data.name,
        provider_type=data.provider_type,
        base_url=data.base_url.rstrip("/"),
        encrypted_api_key=encryption_service.encrypt(data.api_key) if data.api_key else None,
        default_model=data.default_model,
        timeout_seconds=data.timeout_seconds,
    )
    db.add(provider)
    db.commit()
    db.refresh(provider)
    return provider


def list_providers(db: Session, user: User) -> List[ProviderConnection]:
    """List all providers for the current user."""
    return db.query(ProviderConnection).filter(ProviderConnection.owner_id == user.id).all()


def get_provider(db: Session, provider_id: int, user: User) -> ProviderConnection:
    """Get a provider by id."""
    provider = db.query(ProviderConnection).filter(ProviderConnection.id == provider_id).first()
    if not provider:
        raise _not_found(provider_id)
    _check_owner(provider, user)
    return provider


def update_provider(db: Session, provider_id: int, data: ProviderUpdate, user: User) -> ProviderConnection:
    """Update a provider connection."""
    provider = get_provider(db, provider_id, user)
    if data.name is not None:
        provider.name = data.name
    if data.base_url is not None:
        provider.base_url = data.base_url.rstrip("/")
    if data.api_key is not None:
        provider.encrypted_api_key = encryption_service.encrypt(data.api_key)
    if data.default_model is not None:
        provider.default_model = data.default_model
    if data.timeout_seconds is not None:
        provider.timeout_seconds = data.timeout_seconds
    if data.is_active is not None:
        provider.is_active = data.is_active
    db.commit()
    db.refresh(provider)
    return provider


def delete_provider(db: Session, provider_id: int, user: User) -> None:
    """Delete a provider connection."""
    provider = get_provider(db, provider_id, user)
    db.delete(provider)
    db.commit()


def mask_api_key(provider: ProviderConnection) -> Optional[str]:
    """Get masked API key for response."""
    if not provider.encrypted_api_key:
        return None
    decrypted = encryption_service.decrypt(provider.encrypted_api_key)
    return encryption_service.mask(decrypted)


def test_connection(db: Session, provider_id: int, user: User) -> ProviderTestResult:
    """Test a provider connection."""
    provider = get_provider(db, provider_id, user)
    api_key = None
    if provider.encrypted_api_key:
        api_key = encryption_service.decrypt(provider.encrypted_api_key)

    try:
        import httpx
        headers = {}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        with httpx.Client(timeout=provider.timeout_seconds) as client:
            resp = client.get(
                f"{provider.base_url}/models",
                headers=headers,
            )
            if resp.status_code == 200:
                data = resp.json()
                models = [m.get("id", "") for m in data.get("data", [])][:20]
                return ProviderTestResult(
                    success=True,
                    message=f"Connected successfully. {len(models)} models available.",
                    models=models,
                )
            elif resp.status_code == 401:
                return ProviderTestResult(success=False, message="Authentication failed: invalid API key")
            else:
                return ProviderTestResult(
                    success=False,
                    message=f"Connection returned HTTP {resp.status_code}: {resp.text[:200]}",
                )
    except httpx.TimeoutException:
        return ProviderTestResult(success=False, message=f"Connection timed out after {provider.timeout_seconds}s")
    except httpx.ConnectError:
        return ProviderTestResult(success=False, message=f"Cannot connect to {provider.base_url}")
    except Exception as e:
        return ProviderTestResult(success=False, message=f"Connection error: {str(e)[:200]}")
