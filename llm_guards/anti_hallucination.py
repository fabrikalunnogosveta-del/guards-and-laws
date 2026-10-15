"""3-line anti-hallucination coordinator (never blocks forever, always reports)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, List, Optional, Sequence


@dataclass
class VerificationReport:
    step: str
    action: str = "PASS"  # PASS | RETRY | SKIP | ALERT
    notes: List[str] = field(default_factory=list)


@dataclass
class AntiHallucination:
    """
    Line 1: grounding (source / NLI-style check)
    Line 2: entity / fact registry cross-check
    Line 3: consistency / adversarial self-check

    Coordinated wrap: pre → step → post. Failure policy is configurable.
    """

    source_check: Optional[Callable[[Any], bool]] = None
    fact_check: Optional[Callable[[Any], bool]] = None
    consistency_check: Optional[Callable[[Any], bool]] = None
    max_retries: int = 2

    def verify(self, output: Any, *, step: str = "step") -> VerificationReport:
        report = VerificationReport(step=step)
        checks = [
            ("line1_source", self.source_check),
            ("line2_facts", self.fact_check),
            ("line3_consistency", self.consistency_check),
        ]
        failed = []
        for name, fn in checks:
            if fn is None:
                continue
            try:
                ok = bool(fn(output))
            except Exception as exc:  # noqa: BLE001
                ok = False
                report.notes.append(f"{name}: error {exc}")
            if not ok:
                failed.append(name)
                report.notes.append(f"{name}: FAILED")
        if not failed:
            report.action = "PASS"
        elif len(failed) >= 2:
            report.action = "ALERT"
        else:
            report.action = "RETRY"
        return report

    def wrap(
        self,
        step_fn: Callable[[], Any],
        *,
        step: str = "step",
        on_retry: Optional[Callable[[int], Any]] = None,
    ) -> VerificationReport:
        last = VerificationReport(step=step, action="ALERT")
        for attempt in range(self.max_retries + 1):
            output = step_fn() if attempt == 0 else (on_retry(attempt) if on_retry else step_fn())
            last = self.verify(output, step=step)
            if last.action == "PASS":
                return last
            if last.action == "ALERT":
                return last
        return last
