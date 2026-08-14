"""Multi-format report generation engine supporting PDF, JSON, and CSV exports."""

import csv
import io
import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.core.config import settings
from app.models.entity import Entity, Relationship
from app.models.finding import Finding
from app.models.investigation import Investigation
from app.models.risk import RiskScore


class ReportGenerator:
    """Generates structured cybersecurity assessment deliverables."""

    OUTPUT_DIR = os.path.join(os.getcwd(), "reports_output")

    @classmethod
    def _ensure_output_dir(cls) -> str:
        os.makedirs(cls.OUTPUT_DIR, exist_ok=True)
        return cls.OUTPUT_DIR

    @classmethod
    def generate_json(
        cls,
        investigation: Investigation,
        entities: List[Entity],
        relationships: List[Relationship],
        findings: List[Finding],
        latest_risk: RiskScore = None,
    ) -> Tuple[str, int]:
        """Generates comprehensive JSON assessment deliverable."""
        output_dir = cls._ensure_output_dir()
        filename = f"OSINT-X_Report_{investigation.id}_{int(datetime.now().timestamp())}.json"
        filepath = os.path.join(output_dir, filename)

        payload = {
            "platform": "OSINT-X Intelligence Platform",
            "report_version": "1.0",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "target": {
                "input": investigation.target_input,
                "type": investigation.target_type.value,
                "is_authorized": investigation.is_authorized,
            },
            "investigation": {
                "id": investigation.id,
                "title": investigation.title,
                "description": investigation.description,
                "status": investigation.status.value,
                "created_at": investigation.created_at.isoformat(),
                "completed_at": investigation.completed_at.isoformat() if investigation.completed_at else None,
            },
            "risk_assessment": {
                "overall_score": latest_risk.overall_score if latest_risk else 0.0,
                "severity_score": latest_risk.severity_score if latest_risk else 0.0,
                "exposure_score": latest_risk.exposure_score if latest_risk else 0.0,
                "explanation": latest_risk.explanation if latest_risk else [],
                "factors": latest_risk.factors if latest_risk else {},
            },
            "asset_inventory": [
                {
                    "id": e.id,
                    "type": e.entity_type.value,
                    "value": e.normalized_value,
                    "display": e.display_value,
                    "confidence": e.confidence,
                    "first_seen": e.first_seen.isoformat(),
                    "source_provenance": e.source_provenance,
                }
                for e in entities
            ],
            "relationships": [
                {
                    "id": r.id,
                    "source": r.source_entity_id,
                    "target": r.target_entity_id,
                    "type": r.relationship_type.value,
                    "confidence": r.confidence,
                    "reason": r.reason,
                    "source_tool": r.source_tool,
                }
                for r in relationships
            ],
            "findings": [
                {
                    "id": f.id,
                    "tool": f.source_tool,
                    "type": f.finding_type.value,
                    "severity": f.severity.value,
                    "title": f.title,
                    "description": f.description,
                    "confidence": f.confidence,
                    "raw_data": f.raw_data,
                }
                for f in findings
            ],
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

        file_size = os.path.getsize(filepath)
        return filepath, file_size

    @classmethod
    def generate_csv(
        cls,
        investigation: Investigation,
        entities: List[Entity],
        findings: List[Finding],
    ) -> Tuple[str, int]:
        """Generates flattened CSV asset inventory deliverable."""
        output_dir = cls._ensure_output_dir()
        filename = f"OSINT-X_Assets_{investigation.id}_{int(datetime.now().timestamp())}.csv"
        filepath = os.path.join(output_dir, filename)

        with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Entity ID", "Entity Type", "Value", "Display Value", "Confidence", "First Seen", "Investigation ID"])
            for e in entities:
                writer.writerow([
                    e.id,
                    e.entity_type.value,
                    e.normalized_value,
                    e.display_value,
                    e.confidence,
                    e.first_seen.isoformat(),
                    investigation.id,
                ])

        file_size = os.path.getsize(filepath)
        return filepath, file_size

    @classmethod
    def generate_pdf(
        cls,
        investigation: Investigation,
        entities: List[Entity],
        relationships: List[Relationship],
        findings: List[Finding],
        latest_risk: RiskScore = None,
    ) -> Tuple[str, int]:
        """Generates executive PDF assessment deliverable using ReportLab."""
        output_dir = cls._ensure_output_dir()
        filename = f"OSINT-X_Executive_Report_{investigation.id}_{int(datetime.now().timestamp())}.pdf"
        filepath = os.path.join(output_dir, filename)

        doc = SimpleDocTemplate(
            filepath,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36,
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Title"],
            fontSize=22,
            textColor=colors.HexColor("#0f172a"),
            spaceAfter=6,
            alignment=0,
        )
        heading_style = ParagraphStyle(
            "SectionHeader",
            parent=styles["Heading2"],
            fontSize=13,
            textColor=colors.HexColor("#1e293b"),
            spaceBefore=12,
            spaceAfter=6,
        )
        body_style = ParagraphStyle(
            "Body",
            parent=styles["Normal"],
            fontSize=9,
            textColor=colors.HexColor("#334155"),
            spaceAfter=4,
        )
        bold_body = ParagraphStyle(
            "BoldBody",
            parent=body_style,
            fontName="Helvetica-Bold",
        )

        elements = []

        # Header Title
        elements.append(Paragraph("OSINT-X — Cybersecurity Assessment Report", title_style))
        elements.append(Paragraph(f"Target: <b>{investigation.target_input}</b> ({investigation.target_type.value}) | Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}", body_style))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0284c7"), spaceAfter=10))

        # 1. Executive Summary & Exposure Risk
        elements.append(Paragraph("1. Executive Summary & Exposure Risk", heading_style))
        risk_val = latest_risk.overall_score if latest_risk else 0.0
        risk_color = "#dc2626" if risk_val >= 75 else ("#ea580c" if risk_val >= 40 else "#16a34a")

        summary_text = f"""
        This document represents an authorized defensive attack-surface and digital-footprint assessment for <b>{investigation.target_input}</b>.
        The overall <b>OSINT-X Exposure Risk Score</b> is evaluated at <font color="{risk_color}"><b>{risk_val}/100</b></font>.
        """
        elements.append(Paragraph(summary_text, body_style))

        if latest_risk and latest_risk.explanation:
            elements.append(Paragraph("<b>Risk Justification Rationale:</b>", bold_body))
            for reason in latest_risk.explanation:
                elements.append(Paragraph(f"• {reason}", body_style))

        elements.append(Spacer(1, 8))

        # 2. Scope & Target Metadata Table
        elements.append(Paragraph("2. Assessment Scope & Target Metadata", heading_style))
        scope_data = [
            ["Investigation ID", investigation.id],
            ["Target Value", investigation.target_input],
            ["Target Type", investigation.target_type.value],
            ["Authorization Confirmed", "Yes (Defensive Assessment Scope)" if investigation.is_authorized else "No"],
            ["Total Discovered Entities", str(len(entities))],
            ["Total Correlated Relationships", str(len(relationships))],
            ["Total Recorded Findings", str(len(findings))],
        ]
        t_scope = Table(scope_data, colWidths=[180, 360])
        t_scope.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f8fafc")),
            ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#1e293b")),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ]))
        elements.append(t_scope)
        elements.append(Spacer(1, 8))

        # 3. Discovered Asset Inventory
        elements.append(Paragraph("3. Discovered Asset Inventory", heading_style))
        asset_table_data = [["Entity Type", "Canonical Value", "Confidence", "Sources"]]
        for e in entities[:15]:  # Limit top 15 in executive view
            src_str = ", ".join(p.get("tool", "osint") for p in e.source_provenance if isinstance(p, dict)) or "system"
            asset_table_data.append([e.entity_type.value, e.normalized_value[:40], f"{e.confidence:.0f}%", src_str])

        if len(asset_table_data) > 1:
            t_assets = Table(asset_table_data, colWidths=[100, 240, 70, 130])
            t_assets.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ]))
            elements.append(t_assets)

        elements.append(Spacer(1, 10))

        # 4. Defensive Remediation & Compliance
        elements.append(Paragraph("4. Defensive Guidance & Ethical Boundaries", heading_style))
        elements.append(Paragraph("• Review exposed subdomains and services for unintended public accessibility or legacy administrative panels.", body_style))
        elements.append(Paragraph("• Enforce Multi-Factor Authentication (MFA) across all digital identities identified in public account presence enumerations.", body_style))
        elements.append(Paragraph("• Maintain regular continuous monitoring to detect unauthorized DNS/subdomain creation or certificate issuance anomalies.", body_style))
        elements.append(Paragraph("• <i>Notice: This report contains passive and authorized active reconnaissance findings and does not contain exploited credential data or active payloads.</i>", body_style))

        doc.build(elements)
        file_size = os.path.getsize(filepath)
        return filepath, file_size
