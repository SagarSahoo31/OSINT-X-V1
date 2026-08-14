"""Investigation lifecycle management service."""

from datetime import datetime, timezone
from typing import List, Optional, Tuple
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.constants import CollectorJobStatus, CollectorName, InvestigationStatus, TargetType
from app.core.exceptions import (
    InvestigationNotFoundError,
    TargetAuthorizationError,
    TargetValidationError,
)
from app.models.entity import Entity
from app.models.finding import Finding
from app.models.investigation import CollectorJob, Investigation
from app.models.risk import RiskScore
from app.schemas.investigation import (
    InvestigationCreate,
    InvestigationSummary,
    InvestigationUpdate,
)
from app.services.target_validator import TargetValidator


class InvestigationService:
    """Service handling investigation creation, validation, lifecycle, and queries."""

    DEFAULT_COLLECTORS = {
        TargetType.EMAIL: [CollectorName.HOLEHE],
        TargetType.USERNAME: [CollectorName.MAIGRET],
        TargetType.DOMAIN: [
            CollectorName.AMASS,
            CollectorName.DNS,
            CollectorName.HTTPX,
            CollectorName.WHATWEB,
            CollectorName.CRTSH,
        ],
        TargetType.IP: [
            CollectorName.DNS,
            CollectorName.HTTPX,
            CollectorName.WHATWEB,
        ],
        TargetType.URL: [
            CollectorName.HTTPX,
            CollectorName.WHATWEB,
        ],
    }

    @classmethod
    async def create_investigation(
        cls,
        db: AsyncSession,
        payload: InvestigationCreate,
        user_id: Optional[str] = None,
    ) -> Investigation:
        """Creates and stages a new authorized investigation."""
        # 1. Enforce defensive authorization requirement
        if not payload.is_authorized:
            raise TargetAuthorizationError(
                "Active investigation rejected: Explicit target authorization confirmation is mandatory for all scans."
            )

        # 2. Validate and canonicalize target
        canonical_target, target_meta = TargetValidator.validate(
            target_input=payload.target_input,
            target_type=payload.target_type,
        )

        # 3. Create Investigation record
        investigation = Investigation(
            title=payload.title,
            description=payload.description,
            target_input=canonical_target,
            target_type=payload.target_type,
            is_authorized=True,
            authorization_notes=payload.authorization_notes,
            status=InvestigationStatus.QUEUED,
            user_id=user_id,
            meta_info={"target_meta": target_meta},
        )
        db.add(investigation)
        await db.flush()

        # 4. Determine collectors to schedule
        selected_collectors = payload.enabled_collectors or cls.DEFAULT_COLLECTORS.get(
            payload.target_type, []
        )

        for col_name in selected_collectors:
            job = CollectorJob(
                investigation_id=investigation.id,
                collector_name=col_name,
                status=CollectorJobStatus.PENDING,
            )
            db.add(job)

        await db.commit()
        await db.refresh(investigation, attribute_names=["collector_jobs"])
        return investigation

    @classmethod
    async def get_investigation(
        cls,
        db: AsyncSession,
        investigation_id: str,
    ) -> Investigation:
        """Retrieves full investigation by ID with collector jobs."""
        stmt = (
            select(Investigation)
            .where(Investigation.id == investigation_id)
            .options(selectinload(Investigation.collector_jobs))
        )
        result = await db.execute(stmt)
        investigation = result.scalar_one_or_none()
        if not investigation:
            raise InvestigationNotFoundError(f"Investigation '{investigation_id}' not found.")
        return investigation

    @classmethod
    async def list_investigations(
        cls,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
        status: Optional[InvestigationStatus] = None,
        target_type: Optional[TargetType] = None,
    ) -> Tuple[List[InvestigationSummary], int]:
        """Returns paginated summary list of investigations with aggregate counts."""
        # Total count query
        count_stmt = select(func.count(Investigation.id))
        if status:
            count_stmt = count_stmt.where(Investigation.status == status)
        if target_type:
            count_stmt = count_stmt.where(Investigation.target_type == target_type)
        total_count = (await db.execute(count_stmt)).scalar() or 0

        # Query investigations with eager loaded collections
        stmt = (
            select(Investigation)
            .options(
                selectinload(Investigation.entities),
                selectinload(Investigation.findings),
                selectinload(Investigation.risk_scores),
            )
            .order_by(Investigation.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        if status:
            stmt = stmt.where(Investigation.status == status)
        if target_type:
            stmt = stmt.where(Investigation.target_type == target_type)

        result = await db.execute(stmt)
        investigations = result.scalars().all()

        summaries: List[InvestigationSummary] = []
        for inv in investigations:
            latest_risk = inv.risk_scores[-1].overall_score if inv.risk_scores else None
            summaries.append(
                InvestigationSummary(
                    id=inv.id,
                    title=inv.title,
                    target_input=inv.target_input,
                    target_type=inv.target_type,
                    status=inv.status,
                    is_authorized=inv.is_authorized,
                    created_at=inv.created_at,
                    completed_at=inv.completed_at,
                    entities_count=len(inv.entities),
                    findings_count=len(inv.findings),
                    risk_score=latest_risk,
                )
            )

        return summaries, total_count

    @classmethod
    async def update_investigation(
        cls,
        db: AsyncSession,
        investigation_id: str,
        payload: InvestigationUpdate,
    ) -> Investigation:
        """Updates investigation details and status."""
        investigation = await cls.get_investigation(db, investigation_id)

        if payload.title is not None:
            investigation.title = payload.title
        if payload.description is not None:
            investigation.description = payload.description
        if payload.status is not None:
            investigation.status = payload.status
            if payload.status == InvestigationStatus.RUNNING and not investigation.started_at:
                investigation.started_at = datetime.now(timezone.utc)
            elif payload.status in (InvestigationStatus.COMPLETED, InvestigationStatus.FAILED, InvestigationStatus.CANCELLED):
                investigation.completed_at = datetime.now(timezone.utc)
        if payload.authorization_notes is not None:
            investigation.authorization_notes = payload.authorization_notes

        await db.commit()
        await db.refresh(investigation)
        return investigation

    @classmethod
    async def cancel_investigation(
        cls,
        db: AsyncSession,
        investigation_id: str,
    ) -> Investigation:
        """Cancels an ongoing investigation and marks all pending jobs as cancelled."""
        investigation = await cls.get_investigation(db, investigation_id)
        investigation.status = InvestigationStatus.CANCELLED
        investigation.completed_at = datetime.now(timezone.utc)

        for job in investigation.collector_jobs:
            if job.status in (CollectorJobStatus.PENDING, CollectorJobStatus.RUNNING):
                job.status = CollectorJobStatus.FAILED
                job.error_message = "Investigation cancelled by analyst."
                job.completed_at = datetime.now(timezone.utc)

        await db.commit()
        await db.refresh(investigation)
        return investigation

    @classmethod
    async def delete_investigation(
        cls,
        db: AsyncSession,
        investigation_id: str,
    ) -> bool:
        """Deletes an investigation and cascades to all child records."""
        investigation = await cls.get_investigation(db, investigation_id)
        await db.delete(investigation)
        await db.commit()
        return True
