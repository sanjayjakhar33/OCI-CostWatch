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
from backend.config.settings import get_settings
from backend.models.database_models import CostRecord, Finding, Recommendation
from backend.scanners.cost_analyzer import CostAnalyzer
from backend.scanners.exposure_scanner import ExposureScanner
from backend.scanners.idle_detector import IdleDetector
from backend.scanners.zombie_detector import ZombieDetector
from backend.services.database import get_db, init_db
from backend.services.recommendations import build_recommendations, cloud_hygiene_score
from backend.utils.logging import configure_logging

settings = get_settings()
configure_logging(settings.log_level)

app = FastAPI(title="OCI CostWatch", version="2.0.0")
app = FastAPI(title="OCI CostWatch", version="1.0.0")
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
def run_scan(db: Session = Depends(get_db)) -> dict[str, object]:
    scan_counter.inc()
    zombies = ZombieDetector().scan()
    exposures = ExposureScanner().scan()
    idle = IdleDetector(settings.idle_cpu_threshold_pct, settings.idle_days_threshold).scan()
    recommendations = build_recommendations(zombies, exposures, idle)
    score = cloud_hygiene_score(len(zombies), len(exposures), len(idle), len(recommendations))

    for item in zombies:
        db.add(
            Finding(
                finding_type="zombie",
                resource_id=item["resource_id"],
                resource_name=item["resource_name"],
                severity="medium",
                estimated_monthly_waste_usd=float(item["estimated_monthly_waste_usd"]),
                details=str(item),
            )
        )

    for item in exposures:
        db.add(
            Finding(
                finding_type="exposure",
                resource_id=item["resource_id"],
                resource_name=item["resource_name"],
                severity=item["severity"],
                estimated_monthly_waste_usd=0.0,
                details=str(item),
            )
        )

    for rec in recommendations:
        db.add(
            Recommendation(
                recommendation_type=rec["type"],
                resource_id=rec["resource_id"],
                action=rec["action"],
                potential_savings_usd=float(rec["potential_savings_usd"]),
                priority=rec["priority"],
            )
        )

    db.commit()

    SlackAlert(settings.slack_webhook_url).send(
        "OCI CostWatch scan complete: "
        f"{len(zombies)} zombies, {len(exposures)} exposures, hygiene score {score}"
    )

    return {
        "zombies": zombies,
        "exposures": exposures,
        "idle": idle,
        "recommendations": recommendations,
        "hygiene_score": score,
    }


@app.get("/cost")
def cost(db: Session = Depends(get_db)) -> dict[str, object]:
    analyzer = CostAnalyzer(settings.cost_spike_threshold_pct)
    summary = analyzer.summarize(days=30)

    for day, value in summary["daily_totals"].items():
        db.add(
            CostRecord(
                date=datetime.fromisoformat(day).date(),
                service_name="all",
                amount_usd=float(value),
                currency="USD",
            )
        )
    db.commit()
    return summary


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
    return {
        "zombie_resources": ZombieDetector().scan(),
        "idle_resources": IdleDetector().scan(),
    }


@app.get("/exposures")
def exposures() -> dict[str, object]:
    return {"exposures": ExposureScanner().scan()}


@app.get("/recommendations")
def recommendations() -> dict[str, object]:
    zombies = ZombieDetector().scan()
    exposure_findings = ExposureScanner().scan()
    idle = IdleDetector().scan()
    recs = build_recommendations(zombies, exposure_findings, idle)
    return {"recommendations": recs}
