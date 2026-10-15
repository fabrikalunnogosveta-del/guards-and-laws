"""Typed output contracts for LLM responses (schema-first)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Optional


@dataclass(frozen=True)
class ContractResult:
    ok: bool
    value: Any = None
    error: Optional[str] = None


def validate_nonempty(raw: str) -> ContractResult:
    """Minimal contract: response must be non-empty after strip."""
    if not isinstance(raw, str) or not raw.strip():
        return ContractResult(ok=False, error="empty_response")
    return ContractResult(ok=True, value=raw)


def validate_json_object(raw: str) -> ContractResult:
    """Contract: response must parse as a JSON object (not array/scalar)."""
    import json

    try:
        data = json.loads(raw)
    except Exception as exc:  # noqa: BLE001 — surface parse error as contract error
        return ContractResult(ok=False, error=f"invalid_json: {exc}")
    if not isinstance(data, dict):
        return ContractResult(ok=False, error="not_a_json_object")
    return ContractResult(ok=True, value=data)


Validator = Callable[[str], ContractResult]
