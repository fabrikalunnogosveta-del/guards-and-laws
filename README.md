# llm-guards-and-laws

**Quality gates, circuit breakers, repair loops and domain laws for reliable LLM systems.**

Prompting is harder than code: code fails loudly, LLMs fail silently and confidently.
This library turns “hope the model behaves” into **contracts, gates, repair loops, and vetoes**.

[![CI](https://github.com/fabrikalunnogosveta-del/guards-and-laws/actions/workflows/ci.yml/badge.svg)](https://github.com/fabrikalunnogosveta-del/guards-and-laws/actions)

---

## Why this exists

| Classic code | LLM output |
|---|---|
| Exception on failure | Confident nonsense on failure |
| Compiler catches type errors | Silent schema drift |
| Deterministic | Stochastic |

Production LLM pipelines need **QC**, not vibes:
- structured contracts (schema-validated output)
- pre-flight / post-flight gates (C1–C7)
- repair loops (re-prompt with the validation error)
- circuit breakers (stop hammering a failing API)
- domain **laws** with enforcement (FLAG / WARN / **HARD VETO**)
- guard suites (chrono / style / geo / scene / …)
- knowledge catalog injection into system prompts

---

## How this maps to real jobs

This repo is a **quality layer** used in multi-agent production systems
(50+ orchestrated stages, structured LLM output as the only JSON path).

| Job title | What this repo proves |
|---|---|
| **LLM / AI Systems Engineer** | contracts, C1–C7 gates, repair loop |
| **AI Reliability / LLM Ops** | circuit breaker, anti-hallucination coordinator |
| **Prompt Systems / LLM Quality** | law books with psycho-mechanism + HARD VETO |
| **Multi-agent AI Engineer** | catalog injection into agent system prompts |
| **Media / Creative AI Engineer** | writing & neuro-cinematography law cards |

---

## Architecture

```
llm_guards/
  contracts.py          # typed output contracts (JSON / non-empty)
  gates.py              # C1–C7 quality gates (pre/post flight)
  circuit_breaker.py    # failure isolation + auto-reset
  repair_loop.py        # self-healing re-prompt with error
  guard_suite.py        # pluggable multi-guard checks
  anti_hallucination.py # 3-line defense coordinator
  catalog_injector.py   # inject domain knowledge into prompts
  laws_loader.py        # law books: evaluate facts vs laws
laws/
  writing_laws.json     # sample law cards (psycho_mechanism + rules + enforcement)
tests/test_core.py      # 11 pytest cases
examples/quickstart.py  # runnable demo (no external services)
```

### Quality gates (C1–C7)

| Gate | Check |
|---|---|
| C1 | Context budget (prompt fits model window) |
| C2 | Token clamp (`max_tokens` cap) |
| C3 | Schema / contract validation |
| C4 | Retry budget (do not loop forever) |
| C5 | Circuit breaker state |
| C6 | `finish_reason` ≠ `length` (truncation is not success) |
| C7 | Post-validator business rules |

### Laws

Each law card carries:
- `psycho_mechanism` — why the rule exists (brain / retention / perception)
- `rules` — concrete constraints
- `violation` — what goes wrong if ignored
- `enforcement` — FLAG / WARN / **HARD VETO**
- `checks` — machine-evaluable thresholds

Example: *Cold open must land emotion or an open question in the first 5 seconds — otherwise retention dies before the title card.*

---

## Install

```bash
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

# 1) Reliability
breaker = CircuitBreaker(failures=5, cooldown_s=300)

# 2) Contract + repair
loop = RepairLoop(validate=validate_json_object, max_attempts=3)
result = loop.run(lambda err=None: '{"ok": true}')
assert result.ok

# 3) Domain laws
book = LawBook(load_writing_laws())
report = book.evaluate({"cold_open_s": 2, "static_without_kick_s": 1.0})
print(report.action)  # PASS | WARN | FLAG | VETO
```

Run tests:

```bash
python -m pytest tests/ -q
```

---

## Production context

Extracted from a **multi-agent AI production platform**:
- 50+ orchestrated pipeline stages
- Instructor-only structured LLM output (60+ Pydantic contracts)
- 700+ reasoning examples injected into system prompts
- anti-hallucination (source / fact registry / consistency)
- QC gate before artifact publish

This repo is the **standalone quality layer** — no grey-hat internals, no secrets.

---

## License

MIT
