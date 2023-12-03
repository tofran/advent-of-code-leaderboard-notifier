import os
from abc import ABC, abstractmethod
from venv import logger

import requests


class WebhookSender(ABC):
    # __init__() should load required parameters from env vars

    @abstractmethod
    def send(self, content):
        ...


class DefaultSender(WebhookSender):
    """
    Sends a notification to Slack/Discord/etc.

    Body is a JSON object with a "content" key.
    """

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


class TelegramSender(WebhookSender):
    """
    Sends a notification to Telegram chats.

    Body is a JSON object with "chat_id" and "text" keys.
    """

    def __init__(self):
        self.webhook_url = os.getenv("WEBHOOK_TELEGRAM_URL")
        assert self.webhook_url, (
            "WEBHOOK_TELEGRAM_URL is missing, "
            "https://api.telegram.org/bot<token>/sendMessage is expected."
        )

        self.chat_id = os.getenv("WEBHOOK_TELEGRAM_CHAT_ID")
        assert self.chat_id, (
            "WEBHOOK_TELEGRAM_CHAT_ID is missing, "
            "a comma-separated list of chat IDs to send notification to is expected "
            "(see https://core.telegram.org/bots/api#sendmessage)."
        )

    def send(self, content):
        for chat_id in self.chat_id.split(","):
            try:
                requests.post(
                    self.webhook_url,
                    json={
                        "chat_id": self.chat_id,
                        "text": content,
                    },
                    headers={"Content-Type": "application/json"},
                ).raise_for_status()
            except Exception:
                logger.exception(f"failed to send notification to chat {chat_id}")
