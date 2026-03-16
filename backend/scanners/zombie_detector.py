from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass
class ZombieResource:
    resource_id: str
    resource_name: str
    resource_type: str
    reason: str
    estimated_monthly_waste_usd: float


class ZombieDetector:
    def scan(self) -> list[dict[str, str | float]]:
        findings = [
            ZombieResource(
                resource_id="ocid1.volume.oc1..detached001",
                resource_name="orphan-volume-01",
                resource_type="detached_block_volume",
                reason="Volume detached for over 14 days",
                estimated_monthly_waste_usd=18.5,
            ),
            ZombieResource(
                resource_id="ocid1.publicip.oc1..unused001",
                resource_name="unused-public-ip-01",
                resource_type="unused_public_ip",
                reason="Public IP not attached to any VNIC",
                estimated_monthly_waste_usd=3.0,
            ),
            ZombieResource(
                resource_id="ocid1.bootvolumebackup.oc1..old001",
                resource_name="snapshot-old-01",
                resource_type="old_snapshot",
                reason="Snapshot retention exceeds policy",
                estimated_monthly_waste_usd=7.2,
            ),
        ]
        return [asdict(x) for x in findings]
