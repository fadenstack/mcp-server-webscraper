"""Application settings — static infra + dynamic provider config."""

from __future__ import annotations

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from mcp_server.services.settings_manager import SettingsManager


class InfraSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="MCP_WEBSCRAPE_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    host: str = "0.0.0.0"
    port: int = 8102
    workers_count: int = 1
    reload: bool = False
    environment: str = "production"
    log_level: str = "info"
    auth_token: str = ""

    @property
    def auth_enabled(self) -> bool:
        return bool(self.auth_token)


class WebScrapeProviderSettings(BaseModel):
    request_timeout: int = Field(
        default=20,
        title="Request Timeout",
        description="HTTP request timeout in seconds",
        ge=3,
        le=120,
    )
    user_agent: str = Field(
        default="Fadenstack-Webscrape-MCP/1.0",
        title="User Agent",
        description="User-Agent header used while fetching pages",
    )
    default_max_output_chars: int = Field(
        default=12000,
        title="Default Max Output Characters",
        description="Default hard cap for extracted output length",
        ge=1000,
        le=200000,
    )
    default_output_format: str = Field(
        default="txt",
        title="Default Output Format",
        description="Default output format when caller does not set one",
        pattern="^(txt|markdown)$",
    )
    include_links: bool = Field(
        default=False,
        title="Include Links",
        description="Include link references in extraction output",
    )
    include_tables: bool = Field(
        default=True,
        title="Include Tables",
        description="Include table content in extraction output",
    )
    include_comments: bool = Field(
        default=False,
        title="Include Comments",
        description="Include comment sections when available",
    )
    include_images: bool = Field(
        default=False,
        title="Include Images",
        description="Include image references where possible",
    )


settings = InfraSettings()

provider_settings_manager: SettingsManager[WebScrapeProviderSettings] = SettingsManager(
    schema_class=WebScrapeProviderSettings,
    env_prefix="MCP_WEBSCRAPE_",
    persist_path="data/settings.json",
)
