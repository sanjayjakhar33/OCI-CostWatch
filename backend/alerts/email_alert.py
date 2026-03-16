from __future__ import annotations

import smtplib
from email.message import EmailMessage


class EmailAlert:
    def __init__(
        self,
        smtp_host: str | None,
        smtp_port: int,
        smtp_user: str | None,
        smtp_password: str | None,
        sender: str | None,
        recipient: str | None,
    ) -> None:
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password
        self.sender = sender
        self.recipient = recipient

    def send(self, subject: str, body: str) -> bool:
        if not all([self.smtp_host, self.sender, self.recipient]):
            return False
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = self.sender
        msg["To"] = self.recipient
        msg.set_content(body)

        with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10) as server:
            server.starttls()
            if self.smtp_user and self.smtp_password:
                server.login(self.smtp_user, self.smtp_password)
            server.send_message(msg)
        return True
