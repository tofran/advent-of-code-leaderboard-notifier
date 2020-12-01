#!/usr/bin/python3

# advent_of_code_notify.py
# Send a webhook notification when someone from an Advent Of Code
# leaderboard solves a puzzle
#
# tofran, dec 2020

import os
import requests
import json

LEADERBOARD_ENDPOINT_TEMPLATE = (
    "https://adventofcode.com/"
    "{year}/leaderboard/private/view/{leaderboard_id}.json"
)

CACHE_FILE = os.getenv("CACHE_FILE", "./cache.json")

ADVENT_OF_CODE_YEAR = int(os.getenv("ADVENT_OF_CODE_YEAR", "2020"))
ADVENT_OF_CODE_LEADERBOARD_ID = os.getenv("ADVENT_OF_CODE_LEADERBOARD_ID")
ADVENT_OF_CODE_SESSION_ID = os.getenv("ADVENT_OF_CODE_SESSION_ID")

WEBHOOK_URL = os.getenv("WEBHOOK_URL")

assert ADVENT_OF_CODE_LEADERBOARD_ID, "ADVENT_OF_CODE_LEADERBOARD_ID missing"
assert ADVENT_OF_CODE_SESSION_ID, "ADVENT_OF_CODE_SESSION_ID missing"
assert WEBHOOK_URL, "WEBHOOK_URL missing"

LEADERBOARD_ENDPOINT = LEADERBOARD_ENDPOINT_TEMPLATE.format(
    year=ADVENT_OF_CODE_YEAR,
    leaderboard_id=ADVENT_OF_CODE_LEADERBOARD_ID,
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
        LEADERBOARD_ENDPOINT,
        cookies={
            "session": ADVENT_OF_CODE_SESSION_ID
        }
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


def send_webhook_notification(content):
    requests.post(
        WEBHOOK_URL,
        data=json.dumps({
            "content": content,
        }),
        headers={"Content-Type": "application/json"}
    ).raise_for_status()


def get_leaderboard_diff(old_leaderboard, new_leaderboard):
    return sorted(
        get_leaderboard_set(new_leaderboard)
        - get_leaderboard_set(old_leaderboard)
    )


def main():
    old_leaderboard = get_cached_leaderboard()
    new_leaderboard = fetch_leaderboard()

    diff = get_leaderboard_diff(old_leaderboard, new_leaderboard)

    if not diff:
        return

    messages = [
        "{} solved day {} part {}".format(
            get_name(new_leaderboard, member_id),
            day,
            part
        )
        for member_id, day, part in diff
    ]

    print("Leaderboard chnaged:", messages)

    send_webhook_notification("\n".join(messages))

    save_cached_leaderboard(new_leaderboard)


if __name__ == "__main__":
    main()
