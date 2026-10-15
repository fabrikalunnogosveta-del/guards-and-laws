"""Core tests — gates, breaker, repair, guards, laws."""

from llm_guards import (
    AntiHallucination,
    CatalogInjector,
    CircuitBreaker,
    CircuitOpen,
    GuardSuite,
    LawBook,
    QualityGates,
    RepairLoop,
    chrono_guard,
    load_writing_laws,
    style_guard,
    validate_json_object,
    validate_nonempty,
)


def test_circuit_opens_after_failures():
    cb = CircuitBreaker(failures=3, cooldown_s=10)
    for _ in range(3):
        try:
            cb.call(lambda: (_ for _ in ()).throw(RuntimeError("x")))
        except RuntimeError:
            pass
    assert not cb.allow()
    try:
        cb.call(lambda: 1)
        raise AssertionError("should be open")
    except CircuitOpen:
        pass


def test_circuit_resets_on_success():
    clock = {"t": 0.0}
    cb = CircuitBreaker(failures=2, cooldown_s=300, clock=lambda: clock["t"])
    cb.record_failure()
    cb.record_failure()
    assert cb.state.value == "open"
    clock["t"] = 400.0  # cooldown elapsed → half_open
    assert cb.state.value == "half_open"
    cb.record_success()
    assert cb.state.value == "closed"
    assert cb.allow()


def test_quality_gates_preflight():
    g = QualityGates(context_budget_ratio=0.75, max_tokens_cap=32000, max_retries=5)
    ok = g.preflight(
        prompt_chars=100, context_window_chars=1000, max_tokens=1000, attempt=0, circuit_allow=True
    )
    assert ok.passed
    bad = g.preflight(
        prompt_chars=900, context_window_chars=1000, max_tokens=1000, attempt=0, circuit_allow=True
    )
    assert not bad.passed


def test_quality_gates_postflight_length():
    g = QualityGates()
    r = g.postflight(parsed_ok=True, finish_reason="length", business_ok=True)
    assert not r.passed
    assert any(c.gate == "C6_finish_reason" for c in r.failures)


def test_repair_loop_heals():
    calls = {"n": 0}

    def call(err=None):
        calls["n"] += 1
        return "not-json" if calls["n"] == 1 else '{"ok": true}'

    result = RepairLoop(validate=validate_json_object, max_attempts=3).run(call)
    assert result.ok
    assert result.attempts == 2
    assert result.value == {"ok": True}


def test_repair_loop_exhausts():
    result = RepairLoop(validate=validate_json_object, max_attempts=2).run(lambda err=None: "nope")
    assert not result.ok
    assert result.attempts == 2


def test_guard_suite_chrono_and_style():
    suite = GuardSuite([chrono_guard, style_guard])
    report = suite.run({"year": 5000, "style": ""})
    assert report.has_flags
    assert report.action == "BLOCK"
    clean = suite.run({"year": 1942, "style": "cinematic"})
    assert clean.action == "PASS"


def test_anti_hallucination_retry_then_alert():
    ah = AntiHallucination(source_check=lambda o: False, fact_check=lambda o: False)
    rep = ah.verify("x", step="fact_exactor")
    assert rep.action == "ALERT"
    ah1 = AntiHallucination(source_check=lambda o: False)
    assert ah1.verify("x").action == "RETRY"


def test_laws_cold_open_veto():
    book = LawBook(load_writing_laws())
    assert len(book) >= 4
    report = book.evaluate({"cold_open_s": 12, "static_without_kick_s": 5.0})
    assert report.action == "VETO"
    ok = book.evaluate({"cold_open_s": 3, "static_without_kick_s": 2.0, "inciting_incident_pct": 10})
    assert ok.action == "PASS"


def test_catalog_injector():
    inj = CatalogInjector()
    inj.register("laws", ["WS-05: cold open 5s"])
    inj.register("brand", {"style": "cinematic"})
    prompt = inj.inject(["laws", "brand"])
    assert "WS-05" in prompt
    assert "cinematic" in prompt
    assert inj.prompt_size(["laws"]) > 0


def test_validate_nonempty():
    assert validate_nonempty("  hi ").ok
    assert not validate_nonempty("   ").ok
