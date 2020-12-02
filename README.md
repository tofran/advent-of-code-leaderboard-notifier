# Advent of code leaderboard notifier

Send a webhook notification when someone from an Advent Of Code leaderboard solves a puzzle

I'm using this to track the progress of a group of friends on Discord.

## Usage

Just run this image periodically (at a minimum interval of 15 min):

```sh
$ docker run \
  -e WEBHOOK_URL="your webhook url" \
  -e ADVENT_OF_CODE_SESSION_ID="your advent of code session id" \
  -e ADVENT_OF_CODE_LEADERBOARD_ID="numeric leaderboard id" \
  -e CACHE_FILE=/cache/cache.json \
  -v "$(pwd)/cache/:/cache/" \
  ghcr.io/tofran/advent-of-code-leaderboard-notifier
```

## License

MIT