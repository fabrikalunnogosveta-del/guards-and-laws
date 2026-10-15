"""Quickstart — quality gates + repair + laws (no external services required)."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from llm_guards import (
    CircuitBreaker,
    GuardSuite,
    LawBook,
    QualityGates,
    RepairLoop,
    chrono_guard,
    load_writing_laws,
    style_guard,
    validate_json_object,
)


def main() -> None:
    gates = QualityGates()
    pre = gates.preflight(
        prompt_chars=800, context_window_chars=4000, max_tokens=2000, attempt=0, circuit_allow=True
    )
    print("preflight:", "PASS" if pre.passed else pre.failures)

    breaker = CircuitBreaker(failures=5, cooldown_s=300)
    print("circuit:", breaker.state.value)

    def call(err=None):
        return '{"status": "ok"}' if err is None else '{"status": "ok"}'

    result = RepairLoop(validate=validate_json_object, max_attempts=3).run(call)
    print("repair:", result.ok, "attempts=", result.attempts)

    suite = GuardSuite([chrono_guard, style_guard])
    report = suite.run({"year": 1812, "style": "cinematic_history"})
    print("guards:", report.action)

    book = LawBook(load_writing_laws())
    law_report = book.evaluate({"cold_open_s": 2, "static_without_kick_s": 1.0})
    print("laws:", law_report.action, f"({len(book)} laws loaded)")


if __name__ == "__main__":
    main()
