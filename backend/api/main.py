from __future__ import annotations

from datetime import datetime

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, generate_latest
from sqlalchemy import select
from sqlalchemy.orm import Session
from starlette.responses import Response

from backend.alerts.slack_alert import SlackAlert
from backend.config.settings import Settings, get_settings
from backend.models.database_models import (
    ExposureFinding,
    Recommendation,
    ScanHistory,
    ZombieResource,
)
from backend.scanners.cost_analyzer import CostAnalyzer
from backend.scanners.exposure_scanner import ExposureScanner
from backend.scanners.idle_detector import IdleDetector
from backend.scanners.tag_compliance_scanner import TagComplianceScanner
from backend.scanners.zombie_detector import ZombieDetector
from backend.services.database import get_db, init_db
from backend.services.scan_service import ScanService
from backend.utils.logging import configure_logging

settings = get_settings()
configure_logging(settings.log_level)

app = FastAPI(title="OCI CostWatch", version="2.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

scan_counter = Counter("costwatch_scans_total", "Total scans performed")
spike_counter = Counter("costwatch_cost_spikes_total", "Detected cost spikes")


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "time": datetime.utcnow().isoformat()}


@app.get("/metrics")
def metrics() -> Response:
    return Response(generate_latest(), media_type="text/plain")


@app.post("/scan")
def run_scan(
    db: Session = Depends(get_db), cfg: Settings = Depends(get_settings)
) -> dict[str, object]:
    scan_counter.inc()
    payload = ScanService(db, cfg).run_full_scan()
    spike_counter.inc(len(payload["cost"]["spikes"]))
    SlackAlert(cfg.slack_webhook_url).send(
        "OCI CostWatch full scan completed "
        f"with hygiene score {payload['hygiene_score']} "
        f"and {len(payload['recommendations'])} recommendations"
    )
    return payload


@app.get("/cost")
def cost(cfg: Settings = Depends(get_settings)) -> dict[str, object]:
    return CostAnalyzer(cfg.cost_spike_threshold_pct, demo_mode=cfg.demo_mode).summarize(days=30)


@app.get("/resources")
def resources() -> dict[str, object]:
    return {"zombie_resources": ZombieDetector().scan(), "idle_resources": IdleDetector().scan()}


@app.get("/zombies")
def zombies(db: Session = Depends(get_db)) -> list[dict[str, object]]:
    rows = db.scalars(
        select(ZombieResource).order_by(ZombieResource.created_at.desc()).limit(100)
    ).all()
    return [
        {
            "resource_id": row.resource_id,
            "resource_name": row.resource_name,
            "resource_type": row.resource_type,
            "reason": row.reason,
            "estimated_monthly_waste_usd": row.estimated_monthly_waste_usd,
        }
        for row in rows
    ]


@app.get("/exposures")
def exposures(db: Session = Depends(get_db)) -> dict[str, object]:
    rows = db.scalars(
        select(ExposureFinding).order_by(ExposureFinding.created_at.desc()).limit(100)
    ).all()
    if not rows:
        return {"exposures": ExposureScanner().scan()}
    return {
        "exposures": [
            {
                "resource_id": row.resource_id,
                "resource_name": row.resource_name,
                "category": row.category,
                "detail": row.detail,
                "severity": row.severity,
            }
            for row in rows
        ]
    }


@app.get("/tags")
def tags(cfg: Settings = Depends(get_settings)) -> dict[str, object]:
    return {"tag_findings": TagComplianceScanner(cfg.mandatory_tags).scan()}


@app.get("/recommendations")
def recommendations(db: Session = Depends(get_db)) -> dict[str, object]:
    rows = db.scalars(
        select(Recommendation).order_by(Recommendation.created_at.desc()).limit(100)
    ).all()
    return {
        "recommendations": [
            {
                "type": row.recommendation_type,
                "resource_id": row.resource_id,
                "action": row.action,
                "potential_savings_usd": row.potential_savings_usd,
                "priority": row.priority,
            }
            for row in rows
        ]
    }


@app.get("/scan-history")
def scan_history(db: Session = Depends(get_db)) -> list[dict[str, object]]:
    rows = db.scalars(select(ScanHistory).order_by(ScanHistory.created_at.desc()).limit(50)).all()
    return [
        {
            "scan_type": row.scan_type,
            "status": row.status,
            "findings_count": row.findings_count,
            "created_at": row.created_at.isoformat(),
        }
        for row in rows
    ]
