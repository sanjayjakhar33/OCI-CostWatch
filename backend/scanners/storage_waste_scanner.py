from __future__ import annotations


class StorageWasteScanner:
    def scan(self) -> list[dict[str, str | float]]:
        return [
            {
                "resource_id": "ocid1.volume.oc1..u1",
                "resource_name": "unattached-data-vol",
                "resource_type": "unattached_block_volume",
                "reason": "Unattached for 21 days",
                "estimated_monthly_waste_usd": 14.0,
            },
            {
                "resource_id": "ocid1.bootvolume.oc1..oversized",
                "resource_name": "oversized-boot-volume",
                "resource_type": "oversized_boot_volume",
                "reason": "Usage <20% for 30 days",
                "estimated_monthly_waste_usd": 9.5,
            },
        ]
