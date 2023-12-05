# Advent of Code leaderboard notifier

Send a webhook or notification when someone from an Advent of Code leaderboard solves a puzzle.

This can be very useful to track the progress of a group of friends/co-workers on Discord,
Telegram, Slack, etc. It makes the challenge more engaging and competitive.

![Example discord notification](https://user-images.githubusercontent.com/5692603/100946056-738cae80-34fa-11eb-833f-645b8ea2e116.png)

![Example Telegram notification](https://github.com/tofran/advent-of-code-leaderboard-notifier/assets/5692603/37933eee-49ca-409c-9689-4eb10d2aa37a)

## Usage

The image is available in the [GitHub Package Registry] and [Docker Hub]:

Either run the image periodically (ex: cronjob) or run it continuously with `LOOP_SLEEP_SECONDS`.
It will send puzzle solution events to the configured destination.

### Examples

**Simple Discord/Slack/custom webhook**

```sh
docker run \
  -e WEBHOOK_URL="your webhook url" \
  -e ADVENT_OF_CODE_SESSION_ID="your advent of code session id" \
  -e ADVENT_OF_CODE_LEADERBOARD_ID="numeric leaderboard id" \
  -e CACHE_FILE="/cache/cache.json" \
  # Optional - run it continuously as a background service:
  # -e LOOP_SLEEP_SECONDS="900" --restart=unless-stopped -d \
  -v "$(pwd)/cache/:/cache/" \
  ghcr.io/tofran/advent-of-code-leaderboard-notifier
```

**Telegram**

```sh
$ docker run \
  -e NOTIFICATION_SENDER=telegram \
  -e TELEGRAM_BOT_TOKEN="bot token" \
  -e TELEGRAM_CHAT_IDS="chat_id_1,chat_id_2" \
  -e ADVENT_OF_CODE_SESSION_ID="your advent of code session id" \
  -e ADVENT_OF_CODE_LEADERBOARD_ID="numeric leaderboard id" \
  -e CACHE_FILE="/cache/cache.json" \
  # (Same optional env vars, see below)
  -v "$(pwd)/cache/:/cache/" \
  ghcr.io/tofran/advent-of-code-leaderboard-notifier
```

### Configuration

#### - `ADVENT_OF_CODE_LEADERBOARD_ID`

The unique ID of the leaderboard. It's an integer you can get from the end of leaderboard url or
the prefix of the invite code.

#### - `ADVENT_OF_CODE_SESSION_ID`

Your advent of code session id. To retrieve it, visit adventofcode.com,
open developer tools > storage > cookies > copy the value of your `session` cookie.

#### - `LOOP_SLEEP_SECONDS` (optional)

Defaults to `0`, meaning it only runs once and terminates the process.
Otherwise set it to how many seconds to sleep between runs.
It is recommended a value greater than `900` (15 min) - following the Advent of Code recommendation.

#### - `NOTIFICATION_PATTERN` (optional)

Customizes the notification text.
Defaults to `Day {day}: {member} solved {part_emoji} after {after}`. Supported keys:

- `member`: the leaderboard member's name
- `member_id`: the leaderboard member's id
- `day`: the day number
- `part`: the part number
- `part_emoji`: the part emoji (see `NOTIFICATION_PATTERN_EMOJIS`)
- `after`: how much time has passed since puzzle publication `[d] hh:mm:ss` format.
- `mmss`: when the puzzle was solved in `:mm:ss` format.  
  Does not respect timezones (works okay in most timezones - with an offset multiple of the hour)  
  Unstable: might have breaking changes in minor versions.

#### - `NOTIFICATION_2_PATTERN` (optional)

Defaults to the current value of `NOTIFICATION_PATTERN`.
Overrides the notification text for the 2nd puzzle only.
Example: `{member} solved the 🎉🍾 SECOND 🎄💥 part of day {day}!!!`

#### - `NOTIFICATION_PATTERN_EMOJIS` (optional)

Defaults to `⭐🌟`.
A string of emojis to use for the `part_emoji` key in `NOTIFICATION_PATTERN`.
The first emoji is used for part 1, the second for part 2.

A few examples: `🌲🎄`, `🌱🎄`, `🔵🟡`, `🥈🥇`.

#### - `NOTIFICATION_SENDER` (optional)

Default - `webhook`. Can be set to `telegram` to send notifications to Telegram instead.

##### `webhook` notification sender

Sends an HTTP POST to the `WEBHOOK_URL` with a JSON body like `{"content": "<notifications>"}`.

Env vars:

- `WEBHOOK_URL`: (required) Where to send the webhook. For example, a Discord webhook URL.

##### `telegram` notification sender

Sends notification as a message from a bot to given Telegram chats.

Env vars:

- `TELEGRAM_BOT_TOKEN`: (required) Telegram bot token.  
  Ask [@BotFather](https://t.me/botfather) for it.
- `TELEGRAM_CHAT_IDS`: (required) Comma-separated list of chat IDs to send notifications to.  
  See [Telegram docs](https://core.telegram.org/bots/api#sendmessage) for more info.  
  Tip: forward messages to [@JsonDumpBot](https://t.me/JsonDumpBot) and retrieve the chat ids.

#### - `ADVENT_OF_CODE_YEAR` (optional)

Defaults to the latest/current Advent Of Code event.
(The current year if already in december, otherwise the previous one.)

#### - `CACHE_FILE` (optional)

Defaults to `./cache.json`. Where to store the progress of the leaderboard.
Without it, the script is useless because it does not remember what it previously sent.

#### - `WEBHOOK_MAX_CONTENT_LENGTH` (optional)

Defaults to `2000`. The maximum number of characters that can be sent.
Some providers have a character limit restriction.
When it reaches it, it notifies saying the diff is too large.

## License

MIT

[GitHub Package registry]: https://github.com/tofran/advent-of-code-leaderboard-notifier/pkgs/container/advent-of-code-leaderboard-notifier
[Docker Hub]: https://hub.docker.com/r/tofran/advent-of-code-leaderboard-notifier
