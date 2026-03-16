"""Generic runtime-mutable settings manager for MCP server templates."""

from __future__ import annotations

import json
import os
import threading
from pathlib import Path
from typing import Any, Generic, TypeVar

from loguru import logger
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)
MASK = "••••••••"


class SettingsManager(Generic[T]):
    """Manage runtime-mutable provider settings with file persistence."""

    def __init__(
        self,
        schema_class: type[T],
        env_prefix: str,
        persist_path: Path | str = "data/settings.json",
    ) -> None:
        self._schema_class = schema_class
        self._env_prefix = env_prefix.rstrip("_") + "_"
        self._persist_path = Path(persist_path)
        self._lock = threading.Lock()

        env_values = self._load_from_env()
        persisted = self._load_from_file()
        merged = {**env_values, **persisted}
        self._current = schema_class.model_validate(merged)
        logger.info(
            "SettingsManager initialised ({} fields, {} persisted overrides)",
            len(schema_class.model_fields),
            len(persisted),
        )

    @property
    def current(self) -> T:
        return self._current

    def get_schema(self) -> dict[str, Any]:
        return self._schema_class.model_json_schema()

    def get_values(self, *, unmask: bool = False) -> dict[str, Any]:
        data = self._current.model_dump()
        if not unmask:
            sensitive = self._sensitive_fields()
            for key in sensitive:
                if key in data and data[key]:
                    data[key] = MASK
        return data

    def update(self, patch: dict[str, Any]) -> T:
        current_data = self._current.model_dump()

        sensitive = self._sensitive_fields()
        for key in list(patch.keys()):
            if key in sensitive and patch[key] == MASK:
                del patch[key]

        merged = {**current_data, **patch}
        new_settings = self._schema_class.model_validate(merged)

        with self._lock:
            self._current = new_settings
            self._persist_to_file(merged)

        logger.info("Settings updated: {}", list(patch.keys()))
        return new_settings

    def _sensitive_fields(self) -> set[str]:
        result: set[str] = set()
        for name, field_info in self._schema_class.model_fields.items():
            extra = field_info.json_schema_extra
            if isinstance(extra, dict) and extra.get("x-sensitive"):
                result.add(name)
        return result

    def _load_from_env(self) -> dict[str, Any]:
        values: dict[str, Any] = {}
        for name in self._schema_class.model_fields:
            env_key = f"{self._env_prefix}{name.upper()}"
            env_val = os.environ.get(env_key)
            if env_val is not None:
                values[name] = env_val
        return values

    def _load_from_file(self) -> dict[str, Any]:
        if not self._persist_path.exists():
            return {}
        try:
            data = json.loads(self._persist_path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                valid_keys = set(self._schema_class.model_fields.keys())
                return {k: v for k, v in data.items() if k in valid_keys}
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("Failed to load persisted settings: {}", exc)
        return {}

    def _persist_to_file(self, data: dict[str, Any]) -> None:
        try:
            self._persist_path.parent.mkdir(parents=True, exist_ok=True)
            self._persist_path.write_text(
                json.dumps(data, indent=2, default=str),
                encoding="utf-8",
            )
        except OSError as exc:
            logger.error("Failed to persist settings: {}", exc)
