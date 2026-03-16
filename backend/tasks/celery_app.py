from __future__ import annotations

from celery import Celery

from backend.config.settings import get_settings
from backend.scanners.cost_analyzer import CostAnalyzer
from backend.scanners.exposure_scanner import ExposureScanner
from backend.scanners.idle_detector import IdleDetector
from backend.scanners.zombie_detector import ZombieDetector

settings = get_settings()
celery = Celery(
    "costwatch",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery.conf.beat_schedule = {
    "scheduled-scan-every-6-hours": {
        "task": "backend.tasks.celery_app.run_periodic_scan",
        "schedule": 21600,
    },
    "refresh-cost-every-24-hours": {
        "task": "backend.tasks.celery_app.refresh_cost",
        "schedule": 86400,
    },
}


@celery.task
def run_periodic_scan() -> dict[str, int]:
    return {
        "zombies": len(ZombieDetector().scan()),
        "exposures": len(ExposureScanner().scan()),
        "idle": len(IdleDetector().scan()),
    }


@celery.task
def refresh_cost() -> dict[str, object]:
    return CostAnalyzer(settings.cost_spike_threshold_pct).summarize(days=30)
