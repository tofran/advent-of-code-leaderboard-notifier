# Advent of Code leaderboard notifier

Send a webhook or notification when someone from an Advent of Code leaderboard solves a puzzle.

We are using this to track the progress of a group of friends on Discord/Telegram.

<img src='https://github.com/tofran/advent-of-code-leaderboard-notifier/assets/5229130/289bc0e7-5def-4ffa-a21f-53d4eeb8f695' height='200'>

## Usage

Just run this image whenever you want to check for updates:

```sh
# Discord/Slack/custom webhook/etc.
$ docker run \
  -e WEBHOOK_URL="your webhook url" \
  -e ADVENT_OF_CODE_SESSION_ID="your advent of code session id" \
  -e ADVENT_OF_CODE_LEADERBOARD_ID="numeric leaderboard id" \
  -e CACHE_FILE="/cache/cache.json" \
  -v "$(pwd)/cache/:/cache/" \
  # (Optional: run it as a background service)
  # -e LOOP_SLEEP_SECONDS="900" --restart=unless-stopped -d \
  # (Optional: customize the emojis in the notification)
  # -e NOTIFICATION_PATTERN_EMOJIS="⭐🌟"
  # -e NOTIFICATION_PATTERN_EMOJIS="🌲🎄"
  # -e NOTIFICATION_PATTERN_EMOJIS="🌱🎄"
  # -e NOTIFICATION_PATTERN_EMOJIS="🔵🟡"
  # -e NOTIFICATION_PATTERN_EMOJIS="🥈🥇"
  # (Optional: customize the notification text, see more keys below)
  # -e NOTIFICATION_PATTERN="{member} solved {day}.{part} {part_emoji} at {mmss}"
  # (Optional: customize just the part 2 notification)
  # -e NOTIFICATION_2_PATTERN="{member} solved the 🎉🍾SECOND 🎄💥 part of day {day}! MORE EMOJIS!!!"
  ghcr.io/tofran/advent-of-code-leaderboard-notifier

# Telegram
$ docker run \
  -e NOTIFICATION_SENDER=telegram \
  -e TELEGRAM_BOT_TOKEN="bot token" \
  -e TELEGRAM_CHAT_IDS="chat_id_1,chat_id_2" \
  -e ADVENT_OF_CODE_SESSION_ID="your advent of code session id" \
  -e ADVENT_OF_CODE_LEADERBOARD_ID="numeric leaderboard id" \
  -e CACHE_FILE="/cache/cache.json" \
  -v "$(pwd)/cache/:/cache/" \
  # (Same optionals, see above)
  ghcr.io/tofran/advent-of-code-leaderboard-notifier

```

It should exit successfully. Run it periodically (at a minimum interval of 15 min),
or pass the `LOOP_SLEEP_SECONDS` env var to make the script loop.

### Configuration

#### - `ADVENT_OF_CODE_LEADERBOARD_ID`

The unique ID of the leaderboard. It's an integer you can get from the end of leaderboard url or the prefix of the invite code.

#### - `ADVENT_OF_CODE_SESSION_ID`

Your advent of code session id. To retrieve it, visit adventofcode.com, open developer tools > storage > cookies > copy the value of your `session` cookie.

#### - `LOOP_SLEEP_SECONDS` (optional)

Defaults to `0`, meaning it only runs once and terminates the process. Otherwise set it to how many seconds to sleep between runs. It is recommended a value greater than `900` (15 min).

#### - `NOTIFICATION_PATTERN` (optional)

Customizes the notification text. Defaults to `Day {day}: {member} got {part_emoji} after {after}`. Supported keys:

- `member`: the leaderbord member's name
- `member_id`: the leaderbord member's id
- `day`: the day number
- `part`: the part number
- `part_emoji`: the part emoji (see `NOTIFICATION_PATTERN_EMOJIS`)
- `mmss`: when the puzzle was solved in `:mm:ss` format (no hours because timezones, still useful given 15 mins check interval)
- `after`: how much time has passed since puzzle publication when it was solved in `[d] hh:mm:ss` format.

#### - `NOTIFICATION_2_PATTERN` (optional)

Defaults to the current value of `NOTIFICATION_PATTERN`. Customizes just the notification text for part 2 specifically.

#### - `NOTIFICATION_PATTERN_EMOJIS` (optional)

Defaults to `🌱🎄`. A string of emojis to use for the `part_emoji` key in `NOTIFICATION_PATTERN`. The first emoji is used for part 1, the second for part 2.

#### - `NOTIFICATION_SENDER` (optional)

Default - `webhook`. Can be set to `telegram` to send notifications to Telegram instead.

##### `webhook` notification sender

Sends an HTTP POST to the `WEBHOOK_URL` with a JSON body like `{"content": "<notifications>"}`.

Env vars:

- `WEBHOOK_URL`: (required) Where to send the webhook. For example, a Discord webhook URL.

##### `telegram` notification sender

Sends notification as a message from a bot to given Telegram chats.

Env vars:

- `TELEGRAM_BOT_TOKEN`: (required) Telegram bot token, duh. Ask [@BotFather](https://t.me/botfather) for it.
- `TELEGRAM_CHAT_IDS`: (required) Comma-separated list of chat IDs to send notifications to. See [Telegram docs](https://core.telegram.org/bots/api#sendmessage) for more info. You can easily get those IDs by writing/forwarding messages to bots like [@JsonDumpBot](https://t.me/JsonDumpBot).

#### - `ADVENT_OF_CODE_YEAR` (optional)

Defaults to the current year if already in december, otherwise the previous one.

#### - `CACHE_FILE` (optional)

Defaults to `./cache.json`.

#### - `WEBHOOK_MAX_CONTENT_LENGTH` (optional)

Defaults to `2000`. The maximum number of characters that can be sent.

## License

MIT
