# guards-and-laws

**Production reliability layer for LLM systems — contracts, quality gates, repair loops, circuit breakers, and domain laws with hard enforcement.**

[![CI](https://github.com/fabrikalunnogosveta-del/guards-and-laws/actions/workflows/ci.yml/badge.svg)](https://github.com/fabrikalunnogosveta-del/guards-and-laws/actions)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Tests](https://img.shields.io/badge/tests-11%20passed-brightgreen)

---

## The problem we solved

| Problem (before) | Solution (this library) |
|---|---|
| LLM fails **silently and confidently** | Contracts + C1–C7 gates catch failure |
| Schema drift / wrong shape | Typed validation before anything ships |
| Blind retries hammer a dead API | **CircuitBreaker**: N failures → cooldown → reset |
| «Hope the model behaves» | **LawBook HARD VETO** + GuardSuite |
| Hallucinated facts ship to users | 3-line AntiHallucination check |
| Prompt knowledge is tribal | **CatalogInjector** — laws/recipes in every prompt |

**Making LLM output production-reliable is harder than writing the prompt.** Code fails loudly. LLMs fail silently and confidently.
This library turns that into **engineering**.

### Code vs LLM (why gates exist)

| Classic software | LLM systems |
|---|---|
| Exception on failure | Fluent nonsense on failure |
| Compiler catches type errors | Silent schema drift |
| Deterministic output | Stochastic output |
| Unit tests are enough | You need **gates, contracts, and vetoes** |

Most teams ship LLM features by hoping the model behaves.
This library turns that hope into **engineering**.

---

## What you get

```
┌─────────────────────────────────────────────────────────────┐
│                     LLM CALL PIPELINE                       │
│                                                             │
│  prompt ──► [C1 context] ──► [C2 tokens] ──► model         │
│                                              │              │
│                                              ▼              │
│                                    [C3 schema contract]     │
│                                              │              │
│                         ┌── fail ─────────────┤             │
│                         ▼                     │             │
│               [RepairLoop re-prompt]          │ pass        │
│                         │                     ▼             │
│                         │            [C6 finish_reason]     │
│                         │                     │             │
│                         │                     ▼             │
│                         │            [C7 business rules]    │
│                         │                     │             │
│                         ▼                     ▼             │
│               [CircuitBreaker] ──► GuardSuite ──► LawBook  │
│                                         │                  │
│                                         ▼                  │
│                                   PASS / WARN / VETO       │
└─────────────────────────────────────────────────────────────┘
```

| Component | What it does |
|---|---|
| **Contracts** | Schema-validate every LLM response (JSON object, non-empty, custom) |
| **Quality Gates C1–C7** | Pre-flight + post-flight checks (budget, tokens, schema, retry, circuit, truncation, business rules) |
| **RepairLoop** | On validation failure → re-prompt with the exact error (self-healing) |
| **CircuitBreaker** | N failures → cooldown → auto-reset. Stop hammering a dead API |
| **GuardSuite** | Pluggable cheap checks (chrono, style, geo, scene, …) that never crash the pipeline |
| **AntiHallucination** | 3-line defense: source check → fact registry → consistency |
| **CatalogInjector** | Inject domain knowledge (laws, recipes, examples) into system prompts |
| **LawBook** | Domain laws with `psycho_mechanism` + rules + **HARD VETO** enforcement |

---

## Why “laws”?

In creative/production domains, quality is not a number — it is a **set of constraints**
that experts enforce by feel. This library makes those constraints **machine-checkable**:

```json
{
  "id": "WS-05",
  "name": "Cold open",
  "psycho_mechanism": "The first 5-8 seconds decide stay/leave before conscious thought.",
  "rules": ["Second 0-5 = emotion OR unanswered question"],
  "violation": "Logo/greeting in the first 5s = viewer gone.",
  "enforcement": "HARD VETO",
  "checks": [{"fact": "cold_open_s", "max": 5, "severity": "VETO"}]
}
```

Each law card carries:
- **`psycho_mechanism`** — why the rule exists (brain / retention / perception)
- **`rules`** — concrete constraints
- **`violation`** — what goes wrong if you ignore it
- **`enforcement`** — `FLAG` / `WARN` / **`HARD VETO`**
- **`checks`** — machine-evaluable thresholds

---

## How this maps to real jobs

This is the **quality layer** extracted from a multi-agent AI production platform
(50+ orchestrated stages, structured LLM output as the only JSON path).

| Job title | What this repo proves |
|---|---|
| **LLM / AI Systems Engineer** | contracts, C1–C7 gates, repair loop |
| **AI Reliability / LLM Ops** | circuit breaker, anti-hallucination, silent-failure detection |
| **Prompt Systems / LLM Quality Engineer** | law books with psycho-mechanism + HARD VETO |
| **Multi-agent AI Engineer** | catalog injection into agent system prompts |
| **Media / Creative AI Engineer** | writing & neuro-cinematography law cards |

---

## Architecture

```
llm_guards/
  contracts.py           # typed output contracts (JSON / non-empty / custom)
  gates.py               # C1–C7 quality gates (pre-flight / post-flight)
  circuit_breaker.py     # failure isolation + auto-reset
  repair_loop.py         # self-healing re-prompt with validation error
  guard_suite.py         # pluggable multi-guard checks
  anti_hallucination.py  # 3-line defense coordinator
  catalog_injector.py    # inject domain knowledge into prompts
  laws_loader.py         # law books: evaluate facts vs laws
laws/
  writing_laws.json      # sample law cards (psycho_mechanism + rules + enforcement)
tests/test_core.py       # 11 pytest cases
examples/quickstart.py   # runnable demo (no external services)
```

### Quality gates (C1–C7)

| Gate | Check | When |
|---|---|---|
| **C1** | Context budget (prompt fits model window) | pre-flight |
| **C2** | Token clamp (`max_tokens` cap) | pre-flight |
| **C3** | Schema / contract validation | post-flight |
| **C4** | Retry budget (do not loop forever) | pre-flight |
| **C5** | Circuit breaker state | pre-flight |
| **C6** | `finish_reason` ≠ `length` (truncation is not success) | post-flight |
| **C7** | Post-validator business rules | post-flight |

---

## Install

```bash
git clone https://github.com/fabrikalunnogosveta-del/guards-and-laws.git
cd guards-and-laws
pip install -r requirements.txt
```

## Quickstart

```python
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

# ── 1. Reliability ──────────────────────────────────────────────
breaker = CircuitBreaker(failures=5, cooldown_s=300)

def call_llm(prompt: str) -> str:
    return breaker.call(lambda: my_api(prompt))  # raises CircuitOpen when open

# ── 2. Contract + self-healing repair ───────────────────────────
loop = RepairLoop(validate=validate_json_object, max_attempts=3)
result = loop.run(lambda err=None: '{"ok": true}')
assert result.ok
print(f"healed in {result.attempts} attempt(s)")

# ── 3. Quality gates ────────────────────────────────────────────
gates = QualityGates()
pre = gates.preflight(
    prompt_chars=800,
    context_window_chars=4000,
    max_tokens=2000,
    attempt=0,
    circuit_allow=True,
)
assert pre.passed

post = gates.postflight(
    parsed_ok=True,
    finish_reason="stop",   # "length" would fail C6
    business_ok=True,
)
assert post.passed

# ── 4. Guard suite ──────────────────────────────────────────────
suite = GuardSuite([chrono_guard, style_guard])
report = suite.run({"year": 1812, "style": "cinematic_history"})
print(report.action)  # PASS | WARN | BLOCK

# ── 5. Domain laws with HARD VETO ───────────────────────────────
book = LawBook(load_writing_laws())
law_report = book.evaluate({"cold_open_s": 2, "static_without_kick_s": 1.0})
print(law_report.action)  # PASS | WARN | FLAG | VETO
```

Run tests:

```bash
python -m pytest tests/ -q
# 11 passed in 0.09s
```

Run the demo:

```bash
python examples/quickstart.py
```

---

## API reference (core)

### `CircuitBreaker(failures=5, cooldown_s=300)`
- `allow()` → bool
- `call(fn)` → result or raise `CircuitOpen`
- States: `closed` → `open` (after N failures) → `half_open` (after cooldown) → `closed` (on success)

### `RepairLoop(validate, max_attempts=3)`
- `run(call)` → `RepairResult(ok, value, attempts, errors)`
- On failure, calls `call(last_error)` again — the model sees *why* it failed

### `QualityGates(context_budget_ratio=0.75, max_tokens_cap=32000, max_retries=5)`
- `preflight(...)` → `GateReport` (C1, C2, C4, C5)
- `postflight(...)` → `GateReport` (C3, C6, C7)

### `GuardSuite([chrono_guard, style_guard, ...])`
- `run(payload)` → `GuardReport` with `action` = `PASS` / `WARN` / `BLOCK`
- Guards never raise — they report

### `LawBook(laws)`
- `evaluate(facts)` → `LawReport` with `action` = `PASS` / `WARN` / `FLAG` / `VETO`

---

## Testing philosophy

Tests prove **behavioral contracts**, not just “code runs”:
- circuit opens after N failures and recovers after cooldown
- repair loop heals on 2nd attempt
- C6 rejects `finish_reason="length"`
- law `WS-05` returns **VETO** when `cold_open_s > 5`
- guard suite returns `BLOCK` on FLAG findings

---

## Production context

Extracted as a **standalone quality layer** from a multi-agent AI production platform:
- 50+ orchestrated pipeline stages
- Instructor-only structured LLM output (60+ Pydantic contracts)
- 700+ reasoning examples injected into system prompts
- Anti-hallucination (source / fact registry / consistency)
- QC gate before artifact publish

This repo contains **no secrets, no grey-hat internals, no vendor lock-in**.

---

## License

MIT

---

## Author

**Maxim Parshshin** — AI/LLM systems, quality gates, browser automation.
Remote contracts. Open-source: [humanlike-browser-engine](https://github.com/fabrikalunnogosveta-del/humanlike-browser-engine) · [guards-and-laws](https://github.com/fabrikalunnogosveta-del/guards-and-laws).
