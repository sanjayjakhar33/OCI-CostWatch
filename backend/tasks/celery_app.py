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
    "cost-scan": {
        "task": "backend.tasks.celery_app.refresh_cost",
        "schedule": settings.scan_interval_cost_seconds,
    },
    "zombie-scan": {
        "task": "backend.tasks.celery_app.scan_zombies",
        "schedule": settings.scan_interval_zombie_seconds,
    },
    "exposure-scan": {
        "task": "backend.tasks.celery_app.scan_exposures",
        "schedule": settings.scan_interval_exposure_seconds,
    },
    "idle-scan": {
        "task": "backend.tasks.celery_app.scan_idle",
        "schedule": settings.scan_interval_idle_seconds,
    },
}


@celery.task
def scan_zombies() -> dict[str, int]:
    return {"zombies": len(ZombieDetector().scan())}


@celery.task
def scan_exposures() -> dict[str, int]:
    return {"exposures": len(ExposureScanner().scan())}


@celery.task
def scan_idle() -> dict[str, int]:
    return {"idle": len(IdleDetector().scan())}


@celery.task
def refresh_cost() -> dict[str, object]:
    analyzer = CostAnalyzer(settings.cost_spike_threshold_pct, demo_mode=settings.demo_mode)
    return analyzer.summarize(days=30)
