"""C1–C7 quality gates for LLM calls."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class GateCheck:
    gate: str
    passed: bool
    detail: str = ""


@dataclass
class GateReport:
    checks: List[GateCheck] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return all(c.passed for c in self.checks)

    @property
    def failures(self) -> List[GateCheck]:
        return [c for c in self.checks if not c.passed]


@dataclass
class QualityGates:
    """Pre-flight / post-flight gates. Fail-closed on hard gates."""

    context_budget_ratio: float = 0.75  # C1
    max_tokens_cap: int = 32000  # C2
    max_retries: int = 5  # C4

    def preflight(
        self,
        *,
        prompt_chars: int,
        context_window_chars: int,
        max_tokens: int,
        attempt: int = 0,
        circuit_allow: bool = True,
    ) -> GateReport:
        report = GateReport()
        ratio = prompt_chars / max(context_window_chars, 1)
        report.checks.append(
            GateCheck("C1_context_budget", ratio <= self.context_budget_ratio, f"ratio={ratio:.2f}")
        )
        report.checks.append(
            GateCheck("C2_token_clamp", max_tokens <= self.max_tokens_cap, f"max_tokens={max_tokens}")
        )
        report.checks.append(GateCheck("C4_retry_budget", attempt <= self.max_retries, f"attempt={attempt}"))
        report.checks.append(GateCheck("C5_circuit", circuit_allow, "circuit_allow"))
        return report

    def postflight(
        self,
        *,
        parsed_ok: bool,
        finish_reason: Optional[str] = None,
        business_ok: bool = True,
    ) -> GateReport:
        report = GateReport()
        report.checks.append(GateCheck("C3_schema", parsed_ok, "schema_validate"))
        length_trunc = finish_reason == "length"
        report.checks.append(
            GateCheck("C6_finish_reason", not length_trunc, f"finish_reason={finish_reason}")
        )
        report.checks.append(GateCheck("C7_post_validator", business_ok, "business_rules"))
        return report
