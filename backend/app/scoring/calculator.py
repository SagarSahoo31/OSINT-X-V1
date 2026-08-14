"""OSINT-X Exposure Risk scoring engine and explainability factor calculator."""

from typing import Any, Dict, List, Tuple
from app.core.constants import EntityType, FindingSeverity, FindingType
from app.schemas.entity import EntityCreate
from app.schemas.finding import FindingCreate
from app.schemas.risk import RiskFactorBreakdown, RiskScoreRead


class RiskEngine:
    """Calculates the explainable OSINT-X Exposure Risk Score (0-100)."""

    SEVERITY_WEIGHTS = {
        FindingSeverity.CRITICAL: 100.0,
        FindingSeverity.HIGH: 80.0,
        FindingSeverity.MEDIUM: 50.0,
        FindingSeverity.LOW: 20.0,
        FindingSeverity.INFO: 5.0,
    }

    @classmethod
    def calculate_risk(
        cls,
        findings: List[FindingCreate],
        entities: List[EntityCreate],
        investigation_id: str,
    ) -> Tuple[float, float, float, float, Dict[str, Any], List[str]]:
        """
        Calculates: (overall_score, severity_score, exposure_score, confidence_weight, factors_dict, explanations)
        """
        if not findings and not entities:
            return 0.0, 0.0, 0.0, 1.0, {}, ["No assets or findings discovered; exposure risk is minimal."]

        # 1. Severity sub-score
        crit_count = sum(1 for f in findings if f.severity == FindingSeverity.CRITICAL)
        high_count = sum(1 for f in findings if f.severity == FindingSeverity.HIGH)
        med_count = sum(1 for f in findings if f.severity == FindingSeverity.MEDIUM)
        low_count = sum(1 for f in findings if f.severity == FindingSeverity.LOW)
        info_count = sum(1 for f in findings if f.severity == FindingSeverity.INFO)

        total_findings = len(findings) or 1
        weighted_sev_sum = (
            crit_count * cls.SEVERITY_WEIGHTS[FindingSeverity.CRITICAL]
            + high_count * cls.SEVERITY_WEIGHTS[FindingSeverity.HIGH]
            + med_count * cls.SEVERITY_WEIGHTS[FindingSeverity.MEDIUM]
            + low_count * cls.SEVERITY_WEIGHTS[FindingSeverity.LOW]
            + info_count * cls.SEVERITY_WEIGHTS[FindingSeverity.INFO]
        )
        severity_score = min(100.0, weighted_sev_sum / total_findings + (crit_count * 20.0) + (high_count * 10.0))

        # 2. Exposure depth sub-score
        domains_count = sum(1 for e in entities if e.entity_type in (EntityType.DOMAIN, EntityType.SUBDOMAIN))
        ips_count = sum(1 for e in entities if e.entity_type == EntityType.IP)
        urls_count = sum(1 for e in entities if e.entity_type == EntityType.URL)
        techs_count = sum(1 for e in entities if e.entity_type == EntityType.TECHNOLOGY)
        identities_count = sum(1 for e in entities if e.entity_type in (EntityType.EMAIL, EntityType.USERNAME, EntityType.PERSON))

        exposure_score = min(
            100.0,
            (domains_count * 8.0)
            + (ips_count * 10.0)
            + (urls_count * 6.0)
            + (techs_count * 5.0)
            + (identities_count * 7.0),
        )

        # 3. Confidence weight (mean confidence normalized to 0.5 - 1.0)
        avg_confidence = sum(f.confidence for f in findings) / total_findings if findings else 80.0
        confidence_weight = max(0.5, min(1.0, avg_confidence / 100.0))

        # 4. Composite OSINT-X Exposure Risk Score
        raw_score = (0.55 * severity_score + 0.45 * exposure_score) * confidence_weight
        overall_score = round(min(100.0, max(0.0, raw_score)), 1)

        # 5. Explainability factors & justification reasons
        explanations: List[str] = []
        if overall_score >= 75.0:
            explanations.append("High overall exposure: Significant attack-surface breadth and public service footprint detected.")
        elif overall_score >= 40.0:
            explanations.append("Moderate exposure: Standard publicly observable infrastructure and digital identities found.")
        else:
            explanations.append("Low exposure: Limited public footprint and minimal severity indicators observed.")

        if crit_count > 0:
            explanations.append(f"{crit_count} Critical severity finding(s) require immediate remediation review.")
        if high_count > 0:
            explanations.append(f"{high_count} High severity finding(s) detected across target assets.")
        if domains_count > 3:
            explanations.append(f"Substantial perimeter surface with {domains_count} discovered domains/subdomains.")
        if identities_count > 0:
            explanations.append(f"{identities_count} public digital identities/accounts correlated with target.")
        if techs_count > 0:
            explanations.append(f"{techs_count} exposed technology stack components identified.")

        factors = {
            "critical_findings": crit_count,
            "high_findings": high_count,
            "medium_findings": med_count,
            "low_findings": low_count,
            "domains_count": domains_count,
            "ips_count": ips_count,
            "identities_count": identities_count,
            "technologies_count": techs_count,
            "average_confidence": round(avg_confidence, 1),
        }

        return overall_score, round(severity_score, 1), round(exposure_score, 1), round(confidence_weight, 2), factors, explanations


risk_engine = RiskEngine()
