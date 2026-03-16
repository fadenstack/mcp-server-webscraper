"""Abstract base class for tool providers."""

from __future__ import annotations

from abc import ABC, abstractmethod

from mcp.types import Tool


class ToolProvider(ABC):
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Short provider identifier."""

    @abstractmethod
    def list_tools(self) -> list[Tool]:
        """Return MCP Tool definitions."""

    @abstractmethod
    async def call_tool(self, name: str, arguments: dict) -> str:
        """Execute a tool call and return plain-text result."""
