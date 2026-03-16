from __future__ import annotations

from datetime import datetime

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, generate_latest
from sqlalchemy.orm import Session
from starlette.responses import Response

from backend.alerts.slack_alert import SlackAlert
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

app = FastAPI(title="OCI CostWatch", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

scan_counter = Counter("costwatch_scans_total", "Total scans performed")


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
