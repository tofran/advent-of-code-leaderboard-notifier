# Advent of Code leaderboard notifier (Telegram-enabled fork)

Send a webhook or notification when someone from an Advent of Code leaderboard solves a puzzle.

This is a fork of [tofran/advent-of-code-leaderboard-notifier](https://github.com/tofran/advent-of-code-leaderboard-notifier) that:

- enables sending notifications to Telegram (or easily implement another custom webhook sender)
- adds colored emojis to notifications so they're easier to read at a glance
- adds event times to notifications (no hours, just ":MM:SS" because timezones, but it's enough for a 15 min interval)

<img src='https://github.com/iburakov/advent-of-code-leaderboard-notifier-telegram/assets/5229130/83e0aad9-1b2f-4453-945c-2ae96b83b091' height='300'>

## Usage

Just run this image whenever you want to check for updates:

```sh
# Slack/Discord/custom webhook/etc.
$ docker run \
  -e WEBHOOK_URL="your webhook url" \
  -e ADVENT_OF_CODE_SESSION_ID="your advent of code session id" \
  -e ADVENT_OF_CODE_LEADERBOARD_ID="numeric leaderboard id" \
  -e CACHE_FILE="/cache/cache.json" \
  # (Optional) -e LOOP_SLEEP_SECONDS="900" \
  # (Optional, runs it as a background service) --restart=unless-stopped -d \
  -v "$(pwd)/cache/:/cache/" \
  ghcr.io/iburakov/advent-of-code-leaderboard-notifier-telegram:main

# Telegram
$ docker run \
  -e NOTIFICATION_SENDER=telegram \
  -e TELEGRAM_BOT_TOKEN="bot token" \
  -e TELEGRAM_CHAT_IDS="chat_id_1,chat_id_2" \
  -e ADVENT_OF_CODE_SESSION_ID="your advent of code session id" \
  -e ADVENT_OF_CODE_LEADERBOARD_ID="numeric leaderboard id" \
  -e CACHE_FILE="/cache/cache.json" \
  # (Optional) -e LOOP_SLEEP_SECONDS="900" \
  # (Optional, runs it as a background service) --restart=unless-stopped -d \
  -v "$(pwd)/cache/:/cache/" \
  ghcr.io/iburakov/advent-of-code-leaderboard-notifier-telegram:main

```

It should exit successfully. Run it periodically (at a minimum interval of 15 min),
or pass the `LOOP_SLEEP_SECONDS` env var to make the script loop.

### Configuration

- `ADVENT_OF_CODE_LEADERBOARD_ID`: The unique ID of the leaderboard. It's an integer you can get from the end of leaderboard url or the prefix of the invite code.
- `ADVENT_OF_CODE_SESSION_ID`: Your advent of code session id.  
   To retrieve it, visit adventofcode.com, open developer tools > storage > cookies > copy the value of your `session` cookie.
- `ADVENT_OF_CODE_YEAR`: Optional, defaults to the current year if already in december, otherwise the previous one.
- `CACHE_FILE`: Optional, defaults to `./cache.json`
- `LOOP_SLEEP_SECONDS`: Optional, defaults to `0`, meaning it only runs once and terminates the process. Otherwise set it to how many seconds to sleep between runs. It is recommended a value greater than `900` (15 min).
- `WEBHOOK_MAX_CONTENT_LENGTH`: Optional, the maximum number of characters that can be sent. Defaults to `2000`.
- `NOTIFICATION_SENDER`: Optional, allows to select a custom notification sender. Default - `webhook`. Can be set to `telegram` to send notifications to Telegram instead. Each notification sender has its own params. See below and in `notification_senders.py` for more info.

`webhook` notification sender params:

- `WEBHOOK_URL`: Where to send the webhook. For example, a Discord webhook URL.

`telegram` notification sender params:

- `TELEGRAM_BOT_TOKEN`: Your Telegram bot token. Ask [@BotFather](https://t.me/botfather) for it.
- `TELEGRAM_CHAT_IDS`: Comma-separated list of chat IDs to send notifications to. See [Telegram docs](https://core.telegram.org/bots/api#sendmessage) for more info. You can find them by writing/forwarding messages to bots like [@JsonDumpBot](https://t.me/JsonDumpBot).

## License

MIT
