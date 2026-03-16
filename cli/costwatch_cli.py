from __future__ import annotations

import argparse

from tabulate import tabulate

from backend.scanners.exposure_scanner import ExposureScanner
from backend.scanners.idle_detector import IdleDetector
from backend.scanners.tag_compliance_scanner import TagComplianceScanner
from backend.scanners.zombie_detector import ZombieDetector
from backend.services.recommendations import build_recommendations


def render_table(rows: list[dict], headers: str = "keys") -> None:
    if not rows:
        print("No records found")
        return
    print(tabulate(rows, headers=headers, tablefmt="github"))


def command_scan() -> None:
    zombies = ZombieDetector().scan()
    exposures = ExposureScanner().scan()
    idle = IdleDetector().scan()
    tags = TagComplianceScanner(["Environment", "Owner", "Project"]).scan()
    recs = build_recommendations(zombies, exposures, idle, tags)
    print("# Scan Summary")
    print(
        f"zombies={len(zombies)} exposures={len(exposures)} idle={len(idle)} tag_issues={len(tags)}"
    )
    print(f"recommendations={len(recs)}")


def command_report() -> None:
    command_scan()


def command_exposures() -> None:
    render_table(ExposureScanner().scan())


def command_zombies() -> None:
    render_table(ZombieDetector().scan())


def command_recommendations() -> None:
    recs = build_recommendations(
        ZombieDetector().scan(),
        ExposureScanner().scan(),
        IdleDetector().scan(),
        TagComplianceScanner(["Environment", "Owner", "Project"]).scan(),
    )
    render_table(recs)


def command_dashboard() -> None:
    print("Grafana dashboard available at http://localhost:3000 (default admin/admin)")


def main() -> None:
    parser = argparse.ArgumentParser(prog="costwatch", description="OCI CostWatch CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("scan")
    sub.add_parser("report")
    sub.add_parser("exposures")
    sub.add_parser("zombies")
    sub.add_parser("recommendations")
    sub.add_parser("dashboard")

    args = parser.parse_args()
    commands = {
        "scan": command_scan,
        "report": command_report,
        "exposures": command_exposures,
        "zombies": command_zombies,
        "recommendations": command_recommendations,
        "dashboard": command_dashboard,
    }
    commands[args.command]()


if __name__ == "__main__":
    main()
