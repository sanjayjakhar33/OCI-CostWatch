from backend.scanners.cost_analyzer import CostAnalyzer
from backend.scanners.exposure_scanner import ExposureScanner
from backend.scanners.idle_detector import IdleDetector
from backend.scanners.zombie_detector import ZombieDetector


def test_cost_summary_has_projection() -> None:
    summary = CostAnalyzer().summarize(days=7)
    assert "monthly_projection" in summary
    assert summary["monthly_projection"] >= 0


def test_zombie_detector_returns_findings() -> None:
    assert len(ZombieDetector().scan()) > 0


def test_exposure_detector_returns_findings() -> None:
    assert len(ExposureScanner().scan()) > 0


def test_idle_detector_filters_by_threshold() -> None:
    assert len(IdleDetector(cpu_threshold_pct=5, min_idle_days=7).scan()) >= 1
