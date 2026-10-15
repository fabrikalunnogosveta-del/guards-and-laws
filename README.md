# llm-guards-and-laws

**Quality gates and domain laws for reliable LLM systems.**

Prompting is harder than code: code fails loudly, LLMs fail silently and confidently.
This library turns “hope the model behaves” into contracts, gates, repair loops, and vetoes.

[![CI](https://github.com/fabrikalunnogosveta-del/guards-and-laws/actions/workflows/ci.yml/badge.svg)](https://github.com/fabrikalunnogosveta-del/guards-and-laws/actions)

---

## Why this exists

| Code | LLM output |
|---|---|
| Exception on failure | Confident nonsense on failure |
| Compiler catches type errors | Silent schema drift |
| Deterministic | Stochastic |

Production LLM pipelines need **QC**, not vibes:
- structured contracts (Pydantic-style)
- pre-flight gates (C1–C7)
- repair loops (re-prompt with the error)
- circuit breakers (stop hammering a dead API)
- domain **laws** with enforcement (HARD VETO)
- guard suites (geo / chrono / style / scene / …)

---

## Install

```bash
pip install -r requirements.txt
```

## Quickstart

```python
from llm_guards import CircuitBreaker, RepairLoop, GuardSuite, LawBook, load_writing_laws

# 1) Reliability
breaker = CircuitBreaker(failures=5, cooldown_s=300)

# 2) Contract + repair
class Out:
    def __init__(self, text: str, valid: bool):
        self.text, self.valid = text, valid

def validate(raw: str) -> Out:
    ok = bool(raw) and raw.strip().startswith("{")
    return Out(raw, ok)

loop = RepairLoop(validate=validate, max_attempts=3)
result = loop.run(lambda err=None: '{"ok": true}' if err is None else '{"ok": true}')
assert result.valid

# 3) Domain laws
book = LawBook(load_writing_laws())
report = book.evaluate({"cold_open_s": 12, "static_without_kick_s": 5.0})
print(report.action)  # PASS | WARN | VETO
```

Run tests:

```bash
python -m pytest tests/ -q
```

---

## Architecture

```
llm_guards/
  contracts.py         # typed output contracts
  gates.py             # C1–C7 pre-flight / post-flight gates
  circuit_breaker.py   # failure isolation
  repair_loop.py       # re-prompt with validation error
  guard_suite.py       # pluggable multi-guard checks (<100ms target)
  anti_hallucination.py# 3-line defense coordinator (NLI / source / consistency)
  catalog_injector.py  # inject domain knowledge into prompts
  laws_loader.py       # load + evaluate law books (psycho_mechanism + rules)
laws/
  writing_laws.json    # sample production laws (structure + enforcement)
tests/                 # pytest suite
examples/quickstart.py
```

### Quality gates (C1–C7)

| Gate | Check |
|---|---|
| C1 | Context budget (prompt fits model window) |
| C2 | Token clamp (`max_tokens`) |
| C3 | Schema / contract validation |
| C4 | Retry budget (do not loop forever) |
| C5 | Circuit breaker state |
| C6 | `finish_reason` ≠ `length` |
| C7 | Post-validator business rules |

### Laws

Each law carries:
`psycho_mechanism` · `rules` · `violation` · `enforcement` (FLAG / WARN / **HARD VETO**)

Example: *Cold open must land emotion or an open question in the first 5 seconds — otherwise retention dies before the title card.*

---

## How this maps to real systems

Used as the **quality layer** for multi-agent production pipelines:
- 50+ orchestrated stages
- structured LLM output as the only JSON path
- knowledge catalogs injected into system prompts
- silent-failure detection before artifacts ship

See `laws/` for the law-book format and `tests/` for enforcement behavior.

---

## License

MIT
