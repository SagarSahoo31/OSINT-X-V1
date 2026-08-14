"""Report generation and export endpoints for OSINT-X."""

import os
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.entity import Entity, Relationship
from app.models.finding import Finding
from app.models.investigation import Investigation
from app.models.report import Report
from app.models.risk import RiskScore
from app.reporting.generator import ReportGenerator
from app.schemas.report import ReportCreate, ReportRead

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.post("", response_model=ReportRead, status_code=status.HTTP_201_CREATED)
async def generate_report(
    payload: ReportCreate,
    db: AsyncSession = Depends(get_db),
) -> ReportRead:
    """Generates an investigation report deliverable in PDF, JSON, or CSV format."""
    # 1. Fetch full investigation
    inv_stmt = select(Investigation).where(Investigation.id == payload.investigation_id)
    inv_res = await db.execute(inv_stmt)
    inv = inv_res.scalar_one_or_none()
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation not found")

    # 2. Fetch entities, relationships, findings, risk
    e_stmt = select(Entity).where(Entity.investigation_id == payload.investigation_id)
    entities = (await db.execute(e_stmt)).scalars().all()

    r_stmt = select(Relationship).where(Relationship.investigation_id == payload.investigation_id)
    relationships = (await db.execute(r_stmt)).scalars().all()

    f_stmt = select(Finding).where(Finding.investigation_id == payload.investigation_id)
    findings = (await db.execute(f_stmt)).scalars().all()

    risk_stmt = select(RiskScore).where(RiskScore.investigation_id == payload.investigation_id).order_by(RiskScore.calculated_at.desc())
    latest_risk = (await db.execute(risk_stmt)).scalars().first()

    fmt_upper = payload.format.upper()
    title = payload.title or f"{inv.title} - {fmt_upper} Deliverable"

    # 3. Generate file via ReportGenerator
    if fmt_upper == "PDF":
        filepath, file_size = ReportGenerator.generate_pdf(inv, entities, relationships, findings, latest_risk)
    elif fmt_upper == "JSON":
        filepath, file_size = ReportGenerator.generate_json(inv, entities, relationships, findings, latest_risk)
    elif fmt_upper == "CSV":
        filepath, file_size = ReportGenerator.generate_csv(inv, entities, findings)
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported report format: {payload.format}")

    # 4. Save Report record in DB
    report_record = Report(
        investigation_id=inv.id,
        format=fmt_upper,
        title=title,
        file_path=filepath,
        file_size_bytes=file_size,
    )
    db.add(report_record)
    await db.commit()
    await db.refresh(report_record)

    return ReportRead.model_validate(report_record)


@router.get("/{report_id}", response_model=ReportRead)
async def get_report_metadata(
    report_id: str,
    db: AsyncSession = Depends(get_db),
) -> ReportRead:
    """Returns report deliverable metadata."""
    stmt = select(Report).where(Report.id == report_id)
    report = (await db.execute(stmt)).scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return ReportRead.model_validate(report)


@router.get("/{report_id}/download")
async def download_report(
    report_id: str,
    db: AsyncSession = Depends(get_db),
) -> FileResponse:
    """Downloads the generated report file."""
    stmt = select(Report).where(Report.id == report_id)
    report = (await db.execute(stmt)).scalar_one_or_none()
    if not report or not os.path.exists(report.file_path):
        raise HTTPException(status_code=404, detail="Report file not found on server")

    media_types = {
        "PDF": "application/pdf",
        "JSON": "application/json",
        "CSV": "text/csv",
    }
    media_type = media_types.get(report.format, "application/octet-stream")
    filename = os.path.basename(report.file_path)

    return FileResponse(
        path=report.file_path,
        media_type=media_type,
        filename=filename,
    )
