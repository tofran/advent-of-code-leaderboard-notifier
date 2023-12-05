#!/usr/bin/env python3

# advent_of_code_notify.py
# Send a webhook or notification when someone from an Advent of Code
# leaderboard solves a puzzle
#
# tofran and contributors, dec 2020
# https://github.com/tofran/advent-of-code-leaderboard-notifier

import json
import logging
import os
from datetime import UTC, date, datetime
from time import sleep

import requests

from notification_senders import BaseNotificationSender, TelegramSender, WebhookSender

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
NOTIFICATION_SENDER_NAME = os.getenv("NOTIFICATION_SENDER", "webhook")

NOTIFICATION_PATTERN_EMOJIS = os.getenv("NOTIFICATION_PATTERN_EMOJIS", "⭐🌟")
NOTIFICATION_PATTERN = os.getenv(
    "NOTIFICATION_PATTERN", "Day {day}: {member} solved {part_emoji} after {after}"
)
NOTIFICATION_2_PATTERN = os.getenv("NOTIFICATION_2_PATTERN", NOTIFICATION_PATTERN)

assert ADVENT_OF_CODE_LEADERBOARD_ID, "ADVENT_OF_CODE_LEADERBOARD_ID missing"
assert ADVENT_OF_CODE_SESSION_ID, "ADVENT_OF_CODE_SESSION_ID missing"

notification_sender: BaseNotificationSender = {
    "webhook": WebhookSender,
    "telegram": TelegramSender,
}[NOTIFICATION_SENDER_NAME]()


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
        (member_id, day, part, star_info["get_star_ts"])
        for member_id, member in leaderboard.get("members", {}).items()
        for day, parts in member.get("completion_day_level", {}).items()
        for part, star_info in parts.items()
    )


def get_name(leaderboard, member_id):
    return leaderboard["members"][member_id]["name"]


def get_leaderboard_diff(old_leaderboard, new_leaderboard):
    return sorted(
        get_leaderboard_set(new_leaderboard) - get_leaderboard_set(old_leaderboard)
    )


def send_notification(content):
    if len(content) > WEBHOOK_MAX_CONTENT_LENGTH:
        content = "The diff is too big, check the leaderboard: {}".format(
            get_leaderboard_endpoint(as_json_api=False)
        )

    notification_sender.send(content)


def format_unix_ts(ts: int) -> str:
    return datetime.fromtimestamp(ts).strftime(":%M:%S")


def format_unix_timedelta(td: int) -> str:
    td = int(td)
    if td < 0:
        return "-" + format_unix_timedelta(-td)

    d, mod = divmod(td, 3600 * 24)
    h, mod = divmod(mod, 3600)
    m, s = divmod(mod, 60)
    hms = f"{h:02}:{m:02}:{s:02}"
    return f"{d}d {hms}" if d else hms


def find_day_start_ts(day: int) -> int:
    day = int(day)
    # December X, UTC-5 midnight = 05:00 UTC
    moment = datetime(ADVENT_OF_CODE_YEAR, 12, day, hour=5, tzinfo=UTC)
    return int(moment.timestamp())


def run():
    old_leaderboard = get_cached_leaderboard()
    new_leaderboard = fetch_leaderboard()

    diff = get_leaderboard_diff(old_leaderboard, new_leaderboard)

    if not diff:
        logging.info("No changes detected.")
        return

    # sort by get_star_ts
    diff.sort(key=lambda x: x[3])

    messages = []
    for member_id, day, part, mmss_ts in diff:
        emojis = NOTIFICATION_PATTERN_EMOJIS
        part_index = int(part) - 1

        pattern = NOTIFICATION_PATTERN if part == "1" else NOTIFICATION_2_PATTERN
        messages.append(
            pattern.format(
                member_id=member_id,
                member=get_name(new_leaderboard, member_id),
                day=day,
                part=part,
                part_emoji=(
                    emojis[part_index] if 0 <= part_index <= len(emojis) else part
                ),
                # :mm:ss
                mmss=format_unix_ts(mmss_ts),
                # [d] hh:mm:ss since this day's puzzle publication
                after=format_unix_timedelta(mmss_ts - find_day_start_ts(day)),
            )
        )

    logging.info(f"Leaderboard changed: {messages}")

    send_notification("\n".join(messages))

    save_cached_leaderboard(new_leaderboard)


def main():
    if LOOP_SLEEP_SECONDS <= 0:
        run()
        return

    while True:
        try:
            run()
        except Exception:
            logging.exception("error while doing run()")

        logging.info(f"Sleeping {LOOP_SLEEP_SECONDS}s")
        sleep(LOOP_SLEEP_SECONDS)


if __name__ == "__main__":
    main()
