from __future__ import annotations


class NetworkWasteScanner:
    def scan(self) -> list[dict[str, str | float]]:
        return [
            {
                "resource_id": "ocid1.loadbalancer.oc1..unusedlb",
                "resource_name": "legacy-lb",
                "resource_type": "unused_load_balancer",
                "reason": "No backend set for 14 days",
                "estimated_monthly_waste_usd": 25.0,
            },
            {
                "resource_id": "ocid1.nsg.oc1..unusednsg",
                "resource_name": "unused-nsg",
                "resource_type": "unused_nsg",
                "reason": "No attached vnic",
                "estimated_monthly_waste_usd": 0.0,
            },
            {
                "resource_id": "ocid1.subnet.oc1..orphan",
                "resource_name": "orphan-subnet",
                "resource_type": "orphan_subnet",
                "reason": "No active VNICs in subnet",
                "estimated_monthly_waste_usd": 0.0,
            },
        ]
