from backend.scanners.cost_analyzer import CostAnalyzer
from backend.scanners.exposure_scanner import ExposureScanner
from backend.scanners.tag_compliance_scanner import TagComplianceScanner
from backend.scanners.zombie_detector import ZombieDetector
from backend.services.recommendations import build_recommendations, cloud_hygiene_score


def test_cost_summary_has_projection() -> None:
    summary = CostAnalyzer(demo_mode=True).summarize(days=7)
from backend.scanners.idle_detector import IdleDetector
from backend.scanners.zombie_detector import ZombieDetector


def test_cost_summary_has_projection() -> None:
    summary = CostAnalyzer().summarize(days=7)
    assert "monthly_projection" in summary
    assert summary["monthly_projection"] >= 0


def test_zombie_detector_returns_findings() -> None:
    assert len(ZombieDetector().scan()) > 0


def test_exposure_detector_returns_db_port_findings() -> None:
    findings = ExposureScanner().scan()
    assert any("5432" in finding["detail"] for finding in findings)


def test_tag_scanner_detects_missing_tags() -> None:
    findings = TagComplianceScanner(["Environment", "Owner", "Project"]).scan()
    assert len(findings) > 0


def test_recommendation_engine_and_hygiene_score() -> None:
    zombies = ZombieDetector().scan()
    exposures = ExposureScanner().scan()
    idle = []
    tags = TagComplianceScanner(["Environment", "Owner", "Project"]).scan()
    recs = build_recommendations(zombies, exposures, idle, tags)
    score = cloud_hygiene_score(
        len(zombies), len(exposures), len(idle), len(recs), tag_non_compliance_count=len(tags)
    )
    assert len(recs) >= len(zombies)
    assert 0 <= score <= 100
def test_exposure_detector_returns_findings() -> None:
    assert len(ExposureScanner().scan()) > 0


def test_idle_detector_filters_by_threshold() -> None:
    assert len(IdleDetector(cpu_threshold_pct=5, min_idle_days=7).scan()) >= 1
