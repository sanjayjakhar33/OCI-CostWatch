from __future__ import annotations


def cloud_hygiene_score(
    zombie_count: int,
    exposure_count: int,
    idle_count: int,
    opportunities: int,
    tag_non_compliance_count: int = 0,
    cost_anomaly_count: int = 0,
) -> int:
    penalty = (
        zombie_count * 6
        + exposure_count * 10
        + idle_count * 5
        + opportunities * 4
        + tag_non_compliance_count * 4
        + cost_anomaly_count * 8
    )
) -> int:
    penalty = zombie_count * 6 + exposure_count * 10 + idle_count * 5 + opportunities * 4
    return max(0, min(100, 100 - penalty))


def build_recommendations(
    zombies: list[dict],
    exposures: list[dict],
    idle: list[dict],
    tag_findings: list[dict] | None = None,
) -> list[dict[str, object]]:
    recs: list[dict[str, object]] = []
    for z in zombies:
    zombies: list[dict], exposures: list[dict], idle: list[dict]
) -> list[dict[str, object]]:
    recs: list[dict[str, object]] = []
    for z in zombies:
        action = (
            "Delete detached block volume"
            if z.get("resource_type") == "detached_block_volume"
            else "Remove or clean up unused resource"
        )
        recs.append(
            {
                "resource_id": z["resource_id"],
                "type": "zombie_cleanup",
                "action": "Delete or right-size unused resource",
                "action": action,
                "potential_savings_usd": z.get("estimated_monthly_waste_usd", 0),
                "priority": "medium",
            }
        )

    for exp in exposures:
        recs.append(
            {
                "resource_id": exp["resource_id"],
                "type": "exposure_hardening",
                "action": f"Restrict public ingress: {exp.get('detail')}",
                "potential_savings_usd": 0,
                "priority": "high",
            }
        )

    for idle_item in idle:
        recs.append(
            {
                "resource_id": idle_item["instance_id"],
                "type": "idle_optimization",
                "action": idle_item["recommendation"],
                "potential_savings_usd": 15,
                "priority": "medium",
            }
        )

    for tag in tag_findings or []:
        recs.append(
            {
                "resource_id": tag["resource_id"],
                "type": "tag_compliance",
                "action": f"Add missing tags: {', '.join(tag['missing_tags'])}",
                "potential_savings_usd": 0,
                "priority": "low",
            }
        )

    return recs
