from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from backend.models.database_models import (
    CostHistory,
    ExposureFinding,
    Recommendation,
    ScanHistory,
    ZombieResource,
)


class ScanRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def save_cost_summary(self, daily_totals: dict[str, float]) -> None:
        for day, amount in daily_totals.items():
            self.db.add(
                CostHistory(
                    day=datetime.fromisoformat(day).date(),
                    service_name="all",
                    amount_usd=float(amount),
                )
            )
        self.db.add(
            ScanHistory(scan_type="cost", status="success", findings_count=len(daily_totals))
        )

    def save_zombies(self, zombies: list[dict]) -> None:
        for item in zombies:
            self.db.add(
                ZombieResource(
                    resource_id=item["resource_id"],
                    resource_name=item["resource_name"],
                    resource_type=item["resource_type"],
                    reason=item["reason"],
                    estimated_monthly_waste_usd=float(item["estimated_monthly_waste_usd"]),
                )
            )
        self.db.add(ScanHistory(scan_type="zombie", status="success", findings_count=len(zombies)))

    def save_exposures(self, exposures: list[dict]) -> None:
        for item in exposures:
            self.db.add(
                ExposureFinding(
                    resource_id=item["resource_id"],
                    resource_name=item["resource_name"],
                    category=item["category"],
                    detail=item["detail"],
                    severity=item["severity"],
                )
            )
        self.db.add(
            ScanHistory(scan_type="exposure", status="success", findings_count=len(exposures))
        )

    def save_recommendations(self, recommendations: list[dict]) -> None:
        for rec in recommendations:
            self.db.add(
                Recommendation(
                    recommendation_type=str(rec["type"]),
                    resource_id=str(rec["resource_id"]),
                    action=str(rec["action"]),
                    potential_savings_usd=float(rec["potential_savings_usd"]),
                    priority=str(rec["priority"]),
                )
            )

    def commit(self) -> None:
        self.db.commit()
