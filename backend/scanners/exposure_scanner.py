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
                detail="Ingress allows 0.0.0.0/0 on tcp/22",
                severity="high",
            ),
            ExposureFinding(
                resource_id="ocid1.nsg.oc1..open002",
                resource_name="web-nsg",
                category="nsg_open_rdp",
                detail="Ingress allows 0.0.0.0/0 on tcp/3389",
                severity="critical",
            ),
        ]
        return [asdict(x) for x in findings]
