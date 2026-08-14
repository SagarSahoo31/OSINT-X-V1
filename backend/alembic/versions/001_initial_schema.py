"""Initial schema creation for OSINT-X.

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-08-14 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Users table
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("username", sa.String(length=100), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("role", sa.String(length=50), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("is_superuser", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)

    # 2. Audit logs
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=True),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("resource_type", sa.String(length=100), nullable=False),
        sa.Column("resource_id", sa.String(length=100), nullable=True),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("user_agent", sa.String(length=255), nullable=True),
        sa.Column("details", sa.JSON(), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_audit_logs_action"), "audit_logs", ["action"], unique=False)
    op.create_index(op.f("ix_audit_logs_resource_type"), "audit_logs", ["resource_type"], unique=False)
    op.create_index(op.f("ix_audit_logs_timestamp"), "audit_logs", ["timestamp"], unique=False)
    op.create_index("ix_audit_logs_action_timestamp", "audit_logs", ["action", "timestamp"])

    # 3. Investigations table
    op.create_table(
        "investigations",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("target_input", sa.String(length=500), nullable=False),
        sa.Column("target_type", sa.String(length=50), nullable=False),
        sa.Column("is_authorized", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("authorization_notes", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("meta_info", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_investigations_target_input"), "investigations", ["target_input"], unique=False)
    op.create_index(op.f("ix_investigations_target_type"), "investigations", ["target_type"], unique=False)
    op.create_index(op.f("ix_investigations_status"), "investigations", ["status"], unique=False)
    op.create_index(op.f("ix_investigations_user_id"), "investigations", ["user_id"], unique=False)

    # 4. Collector jobs
    op.create_table(
        "collector_jobs",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("investigation_id", sa.String(length=36), nullable=False),
        sa.Column("collector_name", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("raw_output_path", sa.String(length=500), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("items_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("execution_duration_ms", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["investigation_id"], ["investigations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_collector_jobs_investigation_id"), "collector_jobs", ["investigation_id"], unique=False)
    op.create_index(op.f("ix_collector_jobs_collector_name"), "collector_jobs", ["collector_name"], unique=False)
    op.create_index(op.f("ix_collector_jobs_status"), "collector_jobs", ["status"], unique=False)
    op.create_index("ix_collector_jobs_inv_collector", "collector_jobs", ["investigation_id", "collector_name"])

    # 5. Entities table
    op.create_table(
        "entities",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("investigation_id", sa.String(length=36), nullable=False),
        sa.Column("entity_type", sa.String(length=50), nullable=False),
        sa.Column("normalized_value", sa.String(length=500), nullable=False),
        sa.Column("display_value", sa.String(length=500), nullable=False),
        sa.Column("first_seen", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_seen", sa.DateTime(timezone=True), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("meta_info", sa.JSON(), nullable=False),
        sa.Column("source_provenance", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["investigation_id"], ["investigations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("investigation_id", "entity_type", "normalized_value", name="uq_investigation_entity_type_value"),
    )
    op.create_index(op.f("ix_entities_investigation_id"), "entities", ["investigation_id"], unique=False)
    op.create_index(op.f("ix_entities_entity_type"), "entities", ["entity_type"], unique=False)
    op.create_index(op.f("ix_entities_normalized_value"), "entities", ["normalized_value"], unique=False)
    op.create_index("ix_entities_inv_type_val", "entities", ["investigation_id", "entity_type", "normalized_value"])

    # 6. Relationships table
    op.create_table(
        "relationships",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("investigation_id", sa.String(length=36), nullable=False),
        sa.Column("source_entity_id", sa.String(length=36), nullable=False),
        sa.Column("target_entity_id", sa.String(length=36), nullable=False),
        sa.Column("relationship_type", sa.String(length=50), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("reason", sa.String(length=500), nullable=False),
        sa.Column("source_tool", sa.String(length=50), nullable=False),
        sa.Column("evidence", sa.JSON(), nullable=False),
        sa.Column("discovered_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["investigation_id"], ["investigations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["source_entity_id"], ["entities.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["target_entity_id"], ["entities.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("investigation_id", "source_entity_id", "target_entity_id", "relationship_type", name="uq_investigation_rel_src_tgt_type"),
    )
    op.create_index(op.f("ix_relationships_investigation_id"), "relationships", ["investigation_id"], unique=False)
    op.create_index(op.f("ix_relationships_relationship_type"), "relationships", ["relationship_type"], unique=False)
    op.create_index("ix_rel_inv_src_tgt", "relationships", ["investigation_id", "source_entity_id", "target_entity_id"])

    # 7. Findings table
    op.create_table(
        "findings",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("investigation_id", sa.String(length=36), nullable=False),
        sa.Column("collector_job_id", sa.String(length=36), nullable=True),
        sa.Column("source_tool", sa.String(length=50), nullable=False),
        sa.Column("finding_type", sa.String(length=50), nullable=False),
        sa.Column("severity", sa.String(length=50), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("raw_data", sa.JSON(), nullable=False),
        sa.Column("normalized_data", sa.JSON(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["investigation_id"], ["investigations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["collector_job_id"], ["collector_jobs.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_findings_investigation_id"), "findings", ["investigation_id"], unique=False)
    op.create_index(op.f("ix_findings_source_tool"), "findings", ["source_tool"], unique=False)
    op.create_index(op.f("ix_findings_finding_type"), "findings", ["finding_type"], unique=False)
    op.create_index(op.f("ix_findings_severity"), "findings", ["severity"], unique=False)
    op.create_index("ix_findings_inv_severity", "findings", ["investigation_id", "severity"])
    op.create_index("ix_findings_inv_type", "findings", ["investigation_id", "finding_type"])

    # 8. Evidence table
    op.create_table(
        "evidence",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("finding_id", sa.String(length=36), nullable=False),
        sa.Column("evidence_type", sa.String(length=100), nullable=False),
        sa.Column("content", sa.JSON(), nullable=False),
        sa.Column("hash_digest", sa.String(length=64), nullable=True),
        sa.Column("provenance_url", sa.String(length=1000), nullable=True),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["finding_id"], ["findings.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_evidence_finding_id"), "evidence", ["finding_id"], unique=False)
    op.create_index(op.f("ix_evidence_hash_digest"), "evidence", ["hash_digest"], unique=False)

    # 9. Risk scores table
    op.create_table(
        "risk_scores",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("investigation_id", sa.String(length=36), nullable=False),
        sa.Column("overall_score", sa.Float(), nullable=False),
        sa.Column("severity_score", sa.Float(), nullable=False),
        sa.Column("exposure_score", sa.Float(), nullable=False),
        sa.Column("confidence_weight", sa.Float(), nullable=False),
        sa.Column("factors", sa.JSON(), nullable=False),
        sa.Column("explanation", sa.JSON(), nullable=False),
        sa.Column("calculated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["investigation_id"], ["investigations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_risk_scores_investigation_id"), "risk_scores", ["investigation_id"], unique=False)
    op.create_index(op.f("ix_risk_scores_overall_score"), "risk_scores", ["overall_score"], unique=False)
    op.create_index("ix_risk_scores_inv_calc", "risk_scores", ["investigation_id", "calculated_at"])

    # 10. Reports table
    op.create_table(
        "reports",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("investigation_id", sa.String(length=36), nullable=False),
        sa.Column("format", sa.String(length=10), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("file_path", sa.String(length=500), nullable=False),
        sa.Column("file_size_bytes", sa.BigInteger(), nullable=False, server_default=sa.text("0")),
        sa.Column("generated_by", sa.String(length=36), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["investigation_id"], ["investigations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["generated_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_reports_investigation_id"), "reports", ["investigation_id"], unique=False)
    op.create_index("ix_reports_inv_format", "reports", ["investigation_id", "format"])


def downgrade() -> None:
    op.drop_table("reports")
    op.drop_table("risk_scores")
    op.drop_table("evidence")
    op.drop_table("findings")
    op.drop_table("relationships")
    op.drop_table("entities")
    op.drop_table("collector_jobs")
    op.drop_table("investigations")
    op.drop_table("audit_logs")
    op.drop_table("users")
