from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass
class ExposureFinding:
    resource_id: str
    resource_name: str
    category: str
    detail: str
    severity: str


class ExposureScanner:
    def scan(self) -> list[dict[str, str]]:
        findings = [
            ExposureFinding(
                resource_id="ocid1.securitylist.oc1..open001",
                resource_name="default-security-list",
                category="security_list_open_world",
                detail="Ingress allows 0.0.0.0/0 on tcp/22 (SSH)",
                severity="high",
            ),
            ExposureFinding(
                resource_id="ocid1.nsg.oc1..open002",
                resource_name="web-nsg",
                category="nsg_open_rdp",
                detail="Ingress allows 0.0.0.0/0 on tcp/3389 (RDP)",
                severity="critical",
            ),
            ExposureFinding(
                resource_id="ocid1.nsg.oc1..open003",
                resource_name="db-nsg",
                category="nsg_open_database",
                detail="Ingress allows 0.0.0.0/0 on tcp/3306 and tcp/5432",
                severity="critical",
            ),
        ]
        return [asdict(x) for x in findings]
