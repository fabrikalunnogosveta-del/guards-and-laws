"""Inject domain knowledge (laws, recipes, examples) into LLM system prompts."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional


class CatalogInjector:
    """Compose a system prompt from named catalog slices."""

    def __init__(self) -> None:
        self._catalogs: Dict[str, Any] = {}

    def register(self, name: str, content: Any) -> None:
        self._catalogs[name] = content

    def get(self, name: str, default: Any = "") -> Any:
        return self._catalogs.get(name, default)

    def inject(self, names: Iterable[str], *, header: str = "DOMAIN KNOWLEDGE") -> str:
        parts: List[str] = [f"=== {header} ==="]
        for name in names:
            content = self._catalogs.get(name)
            if content is None:
                continue
            if isinstance(content, (list, tuple)):
                body = "\n".join(str(x) for x in content)
            elif isinstance(content, dict):
                body = "\n".join(f"{k}: {v}" for k, v in content.items())
            else:
                body = str(content)
            parts.append(f"--- {name} ---\n{body}")
        return "\n".join(parts)

    def prompt_size(self, names: Iterable[str]) -> int:
        return len(self.inject(names))
