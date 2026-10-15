"""Law books: psycho_mechanism + rules + enforcement (FLAG / WARN / HARD VETO)."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


@dataclass
class LawFinding:
    law_id: str
    name: str
    severity: str  # FLAG | WARN | VETO
    message: str


@dataclass
class LawReport:
    findings: List[LawFinding] = field(default_factory=list)

    @property
    def action(self) -> str:
        if any(f.severity == "VETO" for f in self.findings):
            return "VETO"
        if any(f.severity == "FLAG" for f in self.findings):
            return "FLAG"
        if any(f.severity == "WARN" for f in self.findings):
            return "WARN"
        return "PASS"


class LawBook:
    """Evaluate structured facts against a law catalog."""

    def __init__(self, laws: List[Dict[str, Any]]):
        self.laws = laws or []

    def __len__(self) -> int:
        return len(self.laws)

    def evaluate(self, facts: Dict[str, Any]) -> LawReport:
        report = LawReport()
        for law in self.laws:
            findings = _eval_law(law, facts)
            report.findings.extend(findings)
        return report


def _eval_law(law: Dict[str, Any], facts: Dict[str, Any]) -> List[LawFinding]:
    """Support simple numeric thresholds declared in law['checks']."""
    out: List[LawFinding] = []
    law_id = str(law.get("id", "LAW"))
    name = str(law.get("name", law_id))
    for check in law.get("checks", []) or []:
        key = check.get("fact")
        if key not in facts:
            continue
        try:
            value = float(facts[key])
        except (TypeError, ValueError):
            continue
        limit = check.get("max")
        min_v = check.get("min")
        severity = str(check.get("severity", "FLAG")).upper()
        if severity == "HARD VETO":
            severity = "VETO"
        msg = check.get("message", f"{key} violates {law_id}")
        if limit is not None and value > float(limit):
            out.append(LawFinding(law_id, name, severity, msg))
        if min_v is not None and value < float(min_v):
            out.append(LawFinding(law_id, name, severity, msg))
    return out


def load_writing_laws(path: Optional[Union[str, Path]] = None) -> List[Dict[str, Any]]:
    """Load sample writing laws from laws/writing_laws.json."""
    if path is None:
        path = Path(__file__).resolve().parent.parent / "laws" / "writing_laws.json"
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return list(data.get("laws", []))


def load_laws_file(path: Union[str, Path]) -> List[Dict[str, Any]]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return list(data.get("laws", []))
