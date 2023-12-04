import os
from abc import ABC, abstractmethod
from venv import logger

import requests


class BaseNotificationSender(ABC):
    # __init__() should load required parameters from env vars

    @abstractmethod
    def send(self, content):
        ...


class WebhookSender(BaseNotificationSender):
    """Sends a webhook notification to Slack/Discord/etc"""

    webhook_url: str

    def __init__(self):
        self.webhook_url = os.getenv("WEBHOOK_URL")
        assert self.webhook_url, "WEBHOOK_URL is missing"

    def send(self, content):
        requests.post(
            self.webhook_url,
            json={
                "content": content,
            },
            headers={"Content-Type": "application/json"},
        ).raise_for_status()


class TelegramSender(BaseNotificationSender):
    """Sends a notification to Telegram chats"""

    bot_token: str
    chat_ids: list[str]

    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        assert self.bot_token, "TELEGRAM_BOT_TOKEN is missing, ask @BotFather for it."

        self.chat_ids = [
            s.strip() for s in os.getenv("TELEGRAM_CHAT_IDS", []).split(",")
        ]
        assert self.chat_ids, (
            "TELEGRAM_CHAT_IDS is missing, "
            "a comma-separated list of chat IDs to send notification to is expected "
            "(see https://core.telegram.org/bots/api#sendmessage)."
        )

    def send(self, content):
        for chat_id in self.chat_ids:
            try:
                requests.post(
                    f"https://api.telegram.org/bot{self.bot_token}/sendMessage",
                    json=dict(
                        chat_id=chat_id,
                        text=content,
                    ),
                    headers={"Content-Type": "application/json"},
                ).raise_for_status()
            except Exception:
                logger.exception(f"failed to send notification to chat {chat_id}")
