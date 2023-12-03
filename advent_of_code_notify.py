#!/usr/bin/env python3

# advent_of_code_notify.py
# Send a webhook notification when someone from an Advent Of Code
# leaderboard solves a puzzle
#
# tofran, dec 2020
# https://github.com/tofran/advent-of-code-leaderboard-notifier
#
# iburakov, dec 2023
# - Telegram notifications

import json
import logging
import os
from datetime import date
from time import sleep

import requests

from webhook_senders import DefaultSender, TelegramSender, WebhookSender

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

LEADERBOARD_ENDPOINT_TEMPLATE = (
    "https://adventofcode.com/"
    "{year}/leaderboard/private/view/{leaderboard_id}{extension}"
)

CACHE_FILE = os.getenv("CACHE_FILE", "./cache.json")


def get_default_year():
    today = date.today()
    if today.month == 12:
        return today.year
    return today.year - 1


ADVENT_OF_CODE_LEADERBOARD_ID = os.getenv("ADVENT_OF_CODE_LEADERBOARD_ID")
ADVENT_OF_CODE_SESSION_ID = os.getenv("ADVENT_OF_CODE_SESSION_ID")
ADVENT_OF_CODE_YEAR = int(os.getenv("ADVENT_OF_CODE_YEAR", get_default_year()))
LOOP_SLEEP_SECONDS = int(os.getenv("LOOP_SLEEP_SECONDS", "0"))
WEBHOOK_MAX_CONTENT_LENGTH = int(os.getenv("WEBHOOK_MAX_CONTENT_LENGTH", "2000"))
WEBHOOK_SENDER_NAME = os.getenv("WEBHOOK_SENDER", "default")

assert ADVENT_OF_CODE_LEADERBOARD_ID, "ADVENT_OF_CODE_LEADERBOARD_ID missing"
assert ADVENT_OF_CODE_SESSION_ID, "ADVENT_OF_CODE_SESSION_ID missing"

webhook_senders = {"default": DefaultSender, "telegram": TelegramSender}
webhook_sender: WebhookSender = webhook_senders[WEBHOOK_SENDER_NAME]()


def get_leaderboard_endpoint(as_json_api=True):
    return LEADERBOARD_ENDPOINT_TEMPLATE.format(
        year=ADVENT_OF_CODE_YEAR,
        leaderboard_id=ADVENT_OF_CODE_LEADERBOARD_ID,
        extension=".json" if as_json_api else "",
    )


def get_cached_leaderboard():
    try:
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_cached_leaderboard(data):
    with open(CACHE_FILE, "w+") as f:
        json.dump(
            data,
            f,
            indent=2,
        )


def fetch_leaderboard():
    response = requests.get(
        get_leaderboard_endpoint(as_json_api=True),
        cookies={"session": ADVENT_OF_CODE_SESSION_ID},
    )

    response.raise_for_status()

    return response.json()


def get_leaderboard_set(leaderboard):
    return set(
        (member_id, day, part)
        for member_id, member in leaderboard.get("members", {}).items()
        for day, exercises in member.get("completion_day_level", {}).items()
        for part in exercises.keys()
    )


def get_name(leaderboard, member_id):
    return leaderboard["members"][member_id]["name"]


def get_leaderboard_diff(old_leaderboard, new_leaderboard):
    return sorted(
        get_leaderboard_set(new_leaderboard) - get_leaderboard_set(old_leaderboard)
    )


def send_webhook(content):
    if len(content) > WEBHOOK_MAX_CONTENT_LENGTH:
        content = "The diff is too big, check the leaderboard: {}".format(
            get_leaderboard_endpoint(as_json_api=False)
        )

    webhook_sender.send(content)


def run():
    old_leaderboard = get_cached_leaderboard()
    new_leaderboard = fetch_leaderboard()

    diff = get_leaderboard_diff(old_leaderboard, new_leaderboard)

    if not diff:
        logging.info("No changes detected.")
        return

    messages = [
        "{} solved day {} part {}".format(
            get_name(new_leaderboard, member_id), day, part
        )
        for member_id, day, part in diff
    ]

    logging.info(f"Leaderboard changed: {messages}")

    send_webhook("\n".join(messages))

    save_cached_leaderboard(new_leaderboard)


def main():
    if LOOP_SLEEP_SECONDS <= 0:
        run()
        return

    while True:
        try:
            run()
        except Exception:
            logging.exception("error while running run()")

        logging.info(f"Sleeping {LOOP_SLEEP_SECONDS}s")
        sleep(LOOP_SLEEP_SECONDS)


if __name__ == "__main__":
    main()
