from __future__ import annotations

import logging
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta

logger = logging.getLogger(__name__)

try:
    import oci  # type: ignore
except Exception:  # pragma: no cover
except Exception:  # pragma: no cover - optional at runtime
    oci = None


@dataclass
class CostItem:
    day: date
    service_name: str
    amount_usd: float


class CostAnalyzer:
    def __init__(self, threshold_pct: float = 50.0, demo_mode: bool = True) -> None:
        self.threshold_pct = threshold_pct
        self.demo_mode = demo_mode

    def fetch_cost_data(self, days: int = 30) -> list[CostItem]:
        if self.demo_mode or oci is None:
            logger.info("cost_data_source=demo days=%s", days)
    def __init__(self, threshold_pct: float = 50.0) -> None:
        self.threshold_pct = threshold_pct

    def fetch_cost_data(self, days: int = 30) -> list[CostItem]:
        """Fetch cost data from OCI Cost Analysis APIs or fallback with sample data."""
        if oci is None:
            logger.warning("OCI SDK unavailable, using synthetic cost data")
            today = date.today()
            out: list[CostItem] = []
            for i in range(days):
                d = today - timedelta(days=i)
                out.extend(
                    [
                        CostItem(d, "Compute", 20 + (i % 3) * 1.5),
                        CostItem(d, "BlockStorage", 10 + (i % 4)),
                        CostItem(d, "Networking", 5 + (i % 2)),
                    ]
                )
            return sorted(out, key=lambda x: x.day)

        logger.info("cost_data_source=oci sdk_available=true")
        # Placeholder for OCI Cost Analysis API integration.
        # Kept explicit for production extension.
        logger.info("OCI SDK present; implement tenancy-specific cost query logic here")
        return []

    @staticmethod
    def daily_totals(items: list[CostItem]) -> dict[date, float]:
        totals: dict[date, float] = defaultdict(float)
        for item in items:
            totals[item.day] += item.amount_usd
        return dict(sorted(totals.items(), key=lambda kv: kv[0]))

    @staticmethod
    def service_breakdown(items: list[CostItem]) -> dict[str, float]:
        totals: dict[str, float] = defaultdict(float)
        for item in items:
            totals[item.service_name] += item.amount_usd
        return dict(sorted(totals.items(), key=lambda kv: kv[1], reverse=True))

    @staticmethod
    def project_monthly_cost(items: list[CostItem]) -> float:
        if not items:
            return 0.0
        daily = CostAnalyzer.daily_totals(items)
        avg = sum(daily.values()) / max(len(daily), 1)
        return round(avg * 30, 2)

    def detect_spikes(self, items: list[CostItem]) -> list[dict[str, str | float]]:
        spikes: list[dict[str, str | float]] = []
        daily = self.daily_totals(items)
        sorted_days = sorted(daily)
        for idx in range(1, len(sorted_days)):
            prev_day, day = sorted_days[idx - 1], sorted_days[idx]
            prev = daily[prev_day]
            curr = daily[day]
            if prev <= 0:
                continue
            change_pct = ((curr - prev) / prev) * 100
            if change_pct > self.threshold_pct:
                event = {
                    "date": day.isoformat(),
                    "previous": round(prev, 2),
                    "current": round(curr, 2),
                    "change_pct": round(change_pct, 2),
                }
                logger.warning("cost_spike_detected=%s", event)
                spikes.append(event)
                spikes.append(
                    {
                        "date": day.isoformat(),
                        "previous": round(prev, 2),
                        "current": round(curr, 2),
                        "change_pct": round(change_pct, 2),
                    }
                )
        return spikes

    def summarize(self, days: int = 30) -> dict[str, object]:
        data = self.fetch_cost_data(days=days)
        return {
            "generated_at": datetime.utcnow().isoformat(),
            "daily_totals": {k.isoformat(): v for k, v in self.daily_totals(data).items()},
            "service_breakdown": self.service_breakdown(data),
            "monthly_projection": self.project_monthly_cost(data),
            "spikes": self.detect_spikes(data),
        }
