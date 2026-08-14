"""Investigation endpoints for target validation, scan initiation, status tracking, and deletion."""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import InvestigationStatus, TargetType
from app.core.database import get_db
from app.schemas.investigation import (
    InvestigationCreate,
    InvestigationRead,
    InvestigationSummary,
    InvestigationUpdate,
)
from app.services.investigation_service import InvestigationService
from app.services.target_validator import TargetValidator

router = APIRouter(prefix="/investigations", tags=["Investigations"])


class TargetValidationRequest(BaseModel):
    target_input: str = Field(..., min_length=1, max_length=500)
    target_type: TargetType


class TargetValidationResponse(BaseModel):
    is_valid: bool
    target_input: str
    target_type: TargetType
    canonical_target: str
    metadata: Dict[str, Any]
    error_message: Optional[str] = None


@router.post("/validate-target", response_model=TargetValidationResponse)
async def validate_target(payload: TargetValidationRequest) -> TargetValidationResponse:
    """Pre-flight target validation endpoint verifying syntax, TLD, and safety rules."""
    try:
        canonical, meta = TargetValidator.validate(payload.target_input, payload.target_type)
        return TargetValidationResponse(
            is_valid=True,
            target_input=payload.target_input,
            target_type=payload.target_type,
            canonical_target=canonical,
            metadata=meta,
        )
    except Exception as exc:
        return TargetValidationResponse(
            is_valid=False,
            target_input=payload.target_input,
            target_type=payload.target_type,
            canonical_target=payload.target_input,
            metadata={},
            error_message=str(exc),
        )


@router.post("", response_model=InvestigationRead, status_code=status.HTTP_201_CREATED)
async def create_investigation(
    payload: InvestigationCreate,
    db: AsyncSession = Depends(get_db),
) -> InvestigationRead:
    """Creates a new authorized investigation and queues collectors."""
    investigation = await InvestigationService.create_investigation(db=db, payload=payload)
    return InvestigationRead.model_validate(investigation)


@router.get("", response_model=Dict[str, Any])
async def list_investigations(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[InvestigationStatus] = None,
    target_type: Optional[TargetType] = None,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Returns a paginated list of investigations with summary metrics."""
    summaries, total = await InvestigationService.list_investigations(
        db=db,
        skip=skip,
        limit=limit,
        status=status,
        target_type=target_type,
    )
    return {
        "items": summaries,
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.get("/{investigation_id}", response_model=InvestigationRead)
async def get_investigation(
    investigation_id: str,
    db: AsyncSession = Depends(get_db),
) -> InvestigationRead:
    """Returns complete investigation details with collector jobs."""
    investigation = await InvestigationService.get_investigation(db=db, investigation_id=investigation_id)
    return InvestigationRead.model_validate(investigation)


@router.patch("/{investigation_id}", response_model=InvestigationRead)
async def update_investigation(
    investigation_id: str,
    payload: InvestigationUpdate,
    db: AsyncSession = Depends(get_db),
) -> InvestigationRead:
    """Updates investigation metadata, title, or status."""
    investigation = await InvestigationService.update_investigation(
        db=db,
        investigation_id=investigation_id,
        payload=payload,
    )
    return InvestigationRead.model_validate(investigation)


@router.post("/{investigation_id}/cancel", response_model=InvestigationRead)
async def cancel_investigation(
    investigation_id: str,
    db: AsyncSession = Depends(get_db),
) -> InvestigationRead:
    """Cancels an ongoing investigation."""
    investigation = await InvestigationService.cancel_investigation(
        db=db,
        investigation_id=investigation_id,
    )
    return InvestigationRead.model_validate(investigation)


@router.delete("/{investigation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_investigation(
    investigation_id: str,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Deletes an investigation and all associated findings and graph entities."""
    await InvestigationService.delete_investigation(db=db, investigation_id=investigation_id)
