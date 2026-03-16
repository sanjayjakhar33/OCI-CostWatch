from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "OCI CostWatch"
    app_env: str = "development"
    log_level: str = "INFO"
    demo_mode: bool = True

    database_url: str = Field(
        default="postgresql+psycopg://costwatch:costwatch@postgres:5432/costwatch"
    )
    redis_url: str = "redis://redis:6379/0"

    oci_config_file: str = "~/.oci/config"
    oci_profile: str = "DEFAULT"
    oci_region: str = "us-ashburn-1"
    oci_compartment_id: str = "ocid1.compartment.oc1..exampleuniqueID"

    mandatory_tags: list[str] = ["Environment", "Owner", "Project"]

    cost_spike_threshold_pct: float = 50.0
    idle_cpu_threshold_pct: float = 5.0
    idle_days_threshold: int = 7
    zombie_snapshot_days: int = 30

    scan_interval_cost_seconds: int = 86400
    scan_interval_zombie_seconds: int = 21600
    scan_interval_exposure_seconds: int = 43200
    scan_interval_idle_seconds: int = 21600

    slack_webhook_url: str | None = None
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_user: str | None = None
    smtp_password: str | None = None
    smtp_from: str | None = None
    smtp_to: str | None = None

    celery_broker_url: str = "redis://redis:6379/0"
    celery_result_backend: str = "redis://redis:6379/1"

    cors_origins: list[str] = ["*"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("cost_spike_threshold_pct")
    @classmethod
    def validate_threshold(cls, value: float) -> float:
        if value <= 0:
            raise ValueError("cost_spike_threshold_pct must be greater than zero")
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
