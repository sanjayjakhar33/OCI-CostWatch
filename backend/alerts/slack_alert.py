from __future__ import annotations

import logging

import requests

logger = logging.getLogger(__name__)


class SlackAlert:
    def __init__(self, webhook_url: str | None) -> None:
        self.webhook_url = webhook_url

    def send(self, message: str) -> bool:
        if not self.webhook_url:
            logger.warning("Slack webhook URL is not configured")
            return False

        response = requests.post(self.webhook_url, json={"text": message}, timeout=10)
        ok = response.status_code < 300
        if not ok:
            logger.error("Failed to send Slack alert: %s", response.text)
        return ok
