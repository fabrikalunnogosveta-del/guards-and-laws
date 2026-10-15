"""Pluggable multi-guard suite (pattern: geo / chrono / style / scene / …)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, List, Optional


@dataclass(frozen=True)
class GuardFinding:
    guard: str
    check: str
    severity: str  # FLAG | WARN | INFO
    message: str
    suggestion: str = ""


@dataclass
class GuardReport:
    findings: List[GuardFinding] = field(default_factory=list)

    @property
    def has_flags(self) -> bool:
        return any(f.severity == "FLAG" for f in self.findings)

    @property
    def is_clean(self) -> bool:
        return not self.has_flags and not any(f.severity == "WARN" for f in self.findings)

    @property
    def action(self) -> str:
        if self.has_flags:
            return "BLOCK"
        if any(f.severity == "WARN" for f in self.findings):
            return "WARN"
        return "PASS"


GuardFn = Callable[[dict], List[GuardFinding]]


class GuardSuite:
    """Run many cheap checks; never raise — report only."""

    def __init__(self, guards: Optional[List[GuardFn]] = None):
        self.guards: List[GuardFn] = list(guards or [])

    def register(self, guard: GuardFn) -> None:
        self.guards.append(guard)

    def run(self, payload: dict) -> GuardReport:
        report = GuardReport()
        for guard in self.guards:
            try:
                report.findings.extend(guard(payload) or [])
            except Exception as exc:  # noqa: BLE001 — guards must never kill the pipeline
                report.findings.append(
                    GuardFinding(
                        guard=getattr(guard, "__name__", "guard"),
                        check="guard_crash",
                        severity="WARN",
                        message=str(exc),
                    )
                )
        return report


def chrono_guard(payload: dict) -> List[GuardFinding]:
    """Example guard: flag dates that look inverted or missing year."""
    findings: List[GuardFinding] = []
    year = payload.get("year")
    if year is not None:
        try:
            y = int(year)
            if y < -5000 or y > 2100:
                findings.append(
                    GuardFinding("chrono_guard", "year_range", "FLAG", f"year out of range: {y}")
                )
        except (TypeError, ValueError):
            findings.append(
                GuardFinding("chrono_guard", "year_parse", "FLAG", f"year not numeric: {year!r}")
            )
    return findings


def style_guard(payload: dict) -> List[GuardFinding]:
    """Example guard: warn on empty style / brand token."""
    if not payload.get("style"):
        return [
            GuardFinding(
                "style_guard",
                "missing_style",
                "WARN",
                "no style token in payload",
                suggestion="inject brand/style catalog",
            )
        ]
    return []
