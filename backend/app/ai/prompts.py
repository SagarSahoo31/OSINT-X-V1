"""Structured evidence prompt templates for the local Ollama AI Analyst."""

import json
from typing import Any, Dict, List


class PromptBuilder:
    """Constructs strict evidence-grounded prompts preventing hallucination."""

    SYSTEM_PROMPT = """You are the OSINT-X Defensive AI Security Analyst.
Your role is to analyze authorized OSINT and attack-surface data to provide defensive security insights.
STRICT GUIDELINES:
1. NEVER hallucinate or invent findings, assets, vulnerabilities, or credentials.
2. Ground all analysis EXCLUSIVELY in the provided structured evidence.
3. Clearly distinguish between:
   - [OBSERVED EVIDENCE]: Direct facts returned by tools.
   - [INFERRED RELATIONSHIP]: Heuristic or probabilistic correlations.
   - [UNCERTAINTY]: Areas where evidence is incomplete or inconclusive.
4. Provide actionable DEFENSIVE remediation recommendations.
5. Do NOT suggest exploitation steps, attacks, or invasive actions."""

    @classmethod
    def build_investigation_analysis_prompt(
        cls,
        target: str,
        target_type: str,
        entities: List[Dict[str, Any]],
        relationships: List[Dict[str, Any]],
        findings: List[Dict[str, Any]],
        risk_score: float,
    ) -> str:
        """Constructs prompt for full investigation assessment."""
        evidence_json = json.dumps({
            "target": target,
            "target_type": target_type,
            "risk_score": risk_score,
            "entities_count": len(entities),
            "findings_count": len(findings),
            "sample_entities": entities[:20],
            "sample_relationships": relationships[:15],
            "sample_findings": findings[:20],
        }, indent=2)

        return f"""Perform a defensive cybersecurity assessment based STRICTLY on the following evidence:

```json
{evidence_json}
```

Please structure your response with:
1. Executive Risk Summary (Ground in risk score and asset count)
2. Observed Attack Surface & Identities
3. Key Inferred Relationships & Exposure Paths
4. Uncertainties or Missing Data Points
5. Defensive Remediation & Hardening Actions"""
