# Advent of code leaderboard notifier

Send a webhook notification when someone from an Advent Of Code leaderboard solves a puzzle.

I'm using this to track the progress of a group of friends on Discord.

![Example discord notification](https://user-images.githubusercontent.com/5692603/100946056-738cae80-34fa-11eb-833f-645b8ea2e116.png)

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

### Configuration

 - `ADVENT_OF_CODE_LEADERBOARD_ID`: The unique ID of the leaderboard. It's an integer you can get from the end of leaderboard url or the prefix of the invite code.
 - `ADVENT_OF_CODE_SESSION_ID`: Your advent of code session id.  
    To retrieve it, go visit adventofcode.com, open developer tools > storage > cookies > copy the value of your `session` cookie.
 - `WEBHOOK_URL`: Where to send the webhook. Can be for example a discord webhook.
 - `ADVENT_OF_CODE_YEAR`: Optional, defaults to the current year if already in december, otherwise the previous one.
 - `CACHE_FILE`: Optional, defaults to `./cache.json`


## License

MIT
