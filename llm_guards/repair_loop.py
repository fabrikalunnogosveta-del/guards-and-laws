"""Repair loop — re-prompt with the validation error (self-healing)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, List, Optional

from .contracts import ContractResult, Validator


@dataclass
class RepairResult:
    ok: bool
    value: Any = None
    attempts: int = 0
    errors: List[str] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.errors is None:
            self.errors = []


class RepairLoop:
    """On validation failure, call again with the error message."""

    def __init__(self, validate: Validator, max_attempts: int = 3):
        self.validate = validate
        self.max_attempts = max_attempts

    def run(self, call: Callable[[Optional[str]], str]) -> RepairResult:
        errors: List[str] = []
        last: Optional[ContractResult] = None
        for attempt in range(1, self.max_attempts + 1):
            err = errors[-1] if errors else None
            raw = call(err)
            last = self.validate(raw)
            if last.ok:
                return RepairResult(ok=True, value=last.value, attempts=attempt, errors=errors)
            errors.append(last.error or "validation_failed")
        return RepairResult(
            ok=False,
            value=None,
            attempts=self.max_attempts,
            errors=errors,
        )
