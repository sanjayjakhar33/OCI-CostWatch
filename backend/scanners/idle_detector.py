from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass
class IdleResource:
    instance_id: str
    instance_name: str
    avg_cpu_pct: float
    network_bytes_in: int
    network_bytes_out: int
    uptime_days: int
    recommendation: str


class IdleDetector:
    def __init__(self, cpu_threshold_pct: float = 5.0, min_idle_days: int = 7) -> None:
        self.cpu_threshold_pct = cpu_threshold_pct
        self.min_idle_days = min_idle_days

    def scan(self) -> list[dict[str, str | float | int]]:
        findings = [
            IdleResource(
                instance_id="ocid1.instance.oc1..idle001",
                instance_name="batch-worker-01",
                avg_cpu_pct=1.8,
                network_bytes_in=1024,
                network_bytes_out=256,
                uptime_days=21,
                recommendation="Stop instance during off-hours or downsize shape",
            )
        ]
        return [
            asdict(x)
            for x in findings
            if x.avg_cpu_pct < self.cpu_threshold_pct and x.uptime_days >= self.min_idle_days
        ]
