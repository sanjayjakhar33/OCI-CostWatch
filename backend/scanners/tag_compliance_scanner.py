from __future__ import annotations


class TagComplianceScanner:
    def __init__(self, mandatory_tags: list[str]) -> None:
        self.mandatory_tags = mandatory_tags

    def scan(self) -> list[dict[str, object]]:
        sample_resources = [
            {
                "resource_id": "ocid1.instance.oc1..x1",
                "resource_name": "app-01",
                "tags": {"Owner": "devops"},
            },
            {
                "resource_id": "ocid1.volume.oc1..x2",
                "resource_name": "data-volume",
                "tags": {"Environment": "prod", "Owner": "platform"},
            },
        ]
        findings: list[dict[str, object]] = []
        for item in sample_resources:
            tags = item.get("tags", {})
            missing = [tag for tag in self.mandatory_tags if tag not in tags]
            if missing:
                findings.append(
                    {
                        "resource_id": item["resource_id"],
                        "resource_name": item["resource_name"],
                        "missing_tags": missing,
                        "recommendation": "Apply mandatory governance tags",
                    }
                )
        return findings
