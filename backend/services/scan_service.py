from __future__ import annotations

import logging

from sqlalchemy.orm import Session

from backend.config.settings import Settings
from backend.repositories.scan_repository import ScanRepository
from backend.scanners.cost_analyzer import CostAnalyzer
from backend.scanners.exposure_scanner import ExposureScanner
from backend.scanners.idle_detector import IdleDetector
from backend.scanners.network_waste_scanner import NetworkWasteScanner
from backend.scanners.storage_waste_scanner import StorageWasteScanner
from backend.scanners.tag_compliance_scanner import TagComplianceScanner
from backend.scanners.zombie_detector import ZombieDetector
from backend.services.recommendations import build_recommendations, cloud_hygiene_score

logger = logging.getLogger(__name__)


class ScanService:
    def __init__(self, db: Session, settings: Settings) -> None:
        self.db = db
        self.settings = settings
        self.repo = ScanRepository(db)

    def run_full_scan(self) -> dict[str, object]:
        zombies = ZombieDetector().scan()
        storage_waste = StorageWasteScanner().scan()
        network_waste = NetworkWasteScanner().scan()
        all_zombies = zombies + storage_waste + network_waste
        exposures = ExposureScanner().scan()
        idle = IdleDetector(
            self.settings.idle_cpu_threshold_pct, self.settings.idle_days_threshold
        ).scan()
        tag_findings = TagComplianceScanner(self.settings.mandatory_tags).scan()
        cost = CostAnalyzer(
            threshold_pct=self.settings.cost_spike_threshold_pct,
            demo_mode=self.settings.demo_mode,
        ).summarize(days=30)

        recommendations = build_recommendations(all_zombies, exposures, idle, tag_findings)
        score = cloud_hygiene_score(
            zombie_count=len(all_zombies),
            exposure_count=len(exposures),
            idle_count=len(idle),
            opportunities=len(recommendations),
            tag_non_compliance_count=len(tag_findings),
            cost_anomaly_count=len(cost["spikes"]),
        )

        self.repo.save_zombies(all_zombies)
        self.repo.save_exposures(exposures)
        self.repo.save_cost_summary(cost["daily_totals"])
        self.repo.save_recommendations(recommendations)
        self.repo.commit()

        logger.info(
            "scan_complete zombies=%s exposures=%s idle=%s tags=%s score=%s",
            len(all_zombies),
            len(exposures),
            len(idle),
            len(tag_findings),
            score,
        )

        return {
            "zombies": all_zombies,
            "exposures": exposures,
            "idle": idle,
            "tag_compliance": tag_findings,
            "cost": cost,
            "recommendations": recommendations,
            "hygiene_score": score,
        }
