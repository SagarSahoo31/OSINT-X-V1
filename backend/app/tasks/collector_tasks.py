"""Celery worker task definitions for asynchronous collector execution."""

import asyncio
from datetime import datetime, timezone
from typing import Any, Dict

from celery import shared_task
from sqlalchemy import select

from app.collectors import registry
from app.correlation.engine import correlation_engine
from app.core.celery_app import celery_app
from app.core.constants import CollectorJobStatus, InvestigationStatus
from app.core.database import SyncSessionLocal
from app.core.logging import logger
from app.models.entity import Entity, Relationship
from app.models.finding import Finding
from app.models.investigation import CollectorJob, Investigation
from app.models.risk import RiskScore
from app.normalization.engine import normalization_engine
from app.schemas.entity import EntityCreate
from app.schemas.finding import FindingCreate
from app.scoring.calculator import RiskEngine


@celery_app.task(name="app.tasks.run_collector_job")
def run_collector_job_task(job_id: str) -> Dict[str, Any]:
    """
    Executes a single collector job asynchronously in the Celery worker.
    """
    with SyncSessionLocal() as db:
        stmt = select(CollectorJob).where(CollectorJob.id == job_id)
        job = db.execute(stmt).scalar_one_or_none()
        if not job:
            logger.error("Collector job %s not found", job_id)
            return {"status": "error", "message": "Job not found"}

        # Fetch investigation
        inv_stmt = select(Investigation).where(Investigation.id == job.investigation_id)
        investigation = db.execute(inv_stmt).scalar_one_or_none()
        if not investigation:
            logger.error("Investigation %s for job %s not found", job.investigation_id, job_id)
            return {"status": "error", "message": "Investigation not found"}

        job.status = CollectorJobStatus.RUNNING
        job.started_at = datetime.now(timezone.utc)
        investigation.status = InvestigationStatus.RUNNING
        db.commit()

        collector = registry.get(job.collector_name)
        if not collector:
            job.status = CollectorJobStatus.FAILED
            job.error_message = f"Collector adapter '{job.collector_name}' not registered."
            job.completed_at = datetime.now(timezone.utc)
            db.commit()
            return {"status": "failed", "error": job.error_message}

        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            standardized_findings = loop.run_until_complete(
                collector.execute(investigation.target_input)
            )
            loop.close()

            # 1. Normalize
            raw_entities, raw_findings = normalization_engine.process_collector_findings(
                standardized_findings,
                investigation_id=investigation.id,
            )

            # Persist Entities
            created_entities = []
            for e_data in raw_entities:
                e_obj = Entity(
                    investigation_id=e_data.investigation_id,
                    entity_type=e_data.entity_type,
                    normalized_value=e_data.normalized_value,
                    display_value=e_data.display_value,
                    confidence=e_data.confidence,
                    meta_info=e_data.meta_info,
                    source_provenance=e_data.source_provenance,
                )
                db.add(e_obj)
                created_entities.append(e_obj)

            # Persist Findings
            for f_data in raw_findings:
                f_obj = Finding(
                    investigation_id=f_data.investigation_id,
                    source_tool=f_data.source_tool,
                    finding_type=f_data.finding_type,
                    severity=f_data.severity,
                    title=f_data.title,
                    description=f_data.description,
                    confidence=f_data.confidence,
                    raw_data=f_data.raw_data,
                )
                db.add(f_obj)

            db.flush()

            # 2. Correlate
            correlations = correlation_engine.correlate(
                investigation_id=investigation.id,
                entities=raw_entities,
                findings=raw_findings,
            )
            for r_data in correlations:
                r_obj = Relationship(
                    investigation_id=r_data.investigation_id,
                    source_entity_id=r_data.source_entity_id,
                    target_entity_id=r_data.target_entity_id,
                    relationship_type=r_data.relationship_type,
                    confidence=r_data.confidence,
                    reason=r_data.reason,
                    source_tool=r_data.source_tool,
                    meta_info=r_data.meta_info,
                )
                db.add(r_obj)

            # 3. Calculate Risk Score
            overall, sev, exp, conf_w, factors, reasons = RiskEngine.calculate_risk(
                findings=raw_findings,
                entities=raw_entities,
                investigation_id=investigation.id,
            )
            risk_record = RiskScore(
                investigation_id=investigation.id,
                overall_score=overall,
                severity_score=sev,
                exposure_score=exp,
                confidence_weight=conf_w,
                factors=factors,
                explanation=reasons,
            )
            db.add(risk_record)

            job.status = CollectorJobStatus.COMPLETED
            job.items_count = len(standardized_findings)
            job.completed_at = datetime.now(timezone.utc)
            investigation.status = InvestigationStatus.COMPLETED
            investigation.completed_at = datetime.now(timezone.utc)

            db.commit()
            return {"status": "success", "findings_count": len(standardized_findings)}

        except Exception as exc:
            logger.exception("Error executing job %s: %s", job_id, str(exc))
            job.status = CollectorJobStatus.FAILED
            job.error_message = str(exc)
            job.completed_at = datetime.now(timezone.utc)
            db.commit()
            return {"status": "failed", "error": str(exc)}
