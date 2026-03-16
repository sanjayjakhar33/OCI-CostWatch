from __future__ import annotations

import argparse
import json

from backend.scanners.cost_analyzer import CostAnalyzer
from backend.scanners.exposure_scanner import ExposureScanner
from backend.scanners.idle_detector import IdleDetector
from backend.scanners.zombie_detector import ZombieDetector
from backend.services.recommendations import build_recommendations, cloud_hygiene_score


def command_scan() -> None:
    zombies = ZombieDetector().scan()
    exposures = ExposureScanner().scan()
    idle = IdleDetector().scan()
    recs = build_recommendations(zombies, exposures, idle)
    score = cloud_hygiene_score(len(zombies), len(exposures), len(idle), len(recs))
    print(
        json.dumps(
            {"zombies": zombies, "exposures": exposures, "idle": idle, "hygiene": score},
            indent=2,
        )
    )


def command_report() -> None:
    report = CostAnalyzer().summarize(days=30)
    print(json.dumps(report, indent=2))


def command_alerts() -> None:
    print("Alerts are configured via Slack webhook and optional SMTP in environment variables.")


def command_dashboard() -> None:
    print("Grafana dashboard available at http://localhost:3000 (default admin/admin)")


def main() -> None:
    parser = argparse.ArgumentParser(prog="costwatch", description="OCI CostWatch CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("scan")
    sub.add_parser("report")
    sub.add_parser("alerts")
    sub.add_parser("dashboard")

    args = parser.parse_args()

    if args.command == "scan":
        command_scan()
    elif args.command == "report":
        command_report()
    elif args.command == "alerts":
        command_alerts()
    elif args.command == "dashboard":
        command_dashboard()


if __name__ == "__main__":
    main()
