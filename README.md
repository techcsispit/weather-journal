# weather-journal

Log the weather for a city, then look back at what you've logged: averages, the hottest day, how many days it rained. A Python command-line tool that uses OpenWeatherMap and saves entries in a SQLite file.

## Running it

You need Python 3.8 or newer, and a free API key from [OpenWeatherMap](https://openweathermap.org/api) for `log`. Everything else, including the tests, works without one.

```
pip install -r requirements.txt
export OWM_API_KEY=your-key        # or pass --key to log
python3 -m weather_journal log Mumbai
python3 -m weather_journal history
python3 -m weather_journal stats Mumbai
python3 -m unittest discover tests
```

On Windows, use `python` instead of `python3`, and `set OWM_API_KEY=your-key`.

## Commands

| Command | Does |
|---|---|
| `log <city> [--key KEY]` | Fetches the current weather and saves it |
| `add <city> <temp> <humidity> <condition>` | Saves an entry you type in by hand (temperature in °C, humidity in %), so no API key is needed |
| `history [city]` | Everything logged, newest first. Just one city if you name it |
| `stats <city>` | Number of entries, average temperature, hottest day, rainy days |

## How it's supposed to work

- Temperatures are in °C.
- A city that doesn't exist, or a wrong API key, gives a clear message saying which one it was.
- `stats` for a city with nothing logged just says so.
- Rainy days counts days, not entries: logging three times on one wet day is one rainy day. Drizzle and thunderstorms count as rain.
- Locations returned by OpenWeatherMap are stored by their stable ID, so cities with the same name keep separate histories. If a bare city name is ambiguous, use the suggested full label or `owm:<id>` selector.
- Successful weather responses are cached in `.cache/weather.db` for 10 minutes and reused across separate CLI runs.

## Code

- `weather_journal/fetch.py`: talks to OpenWeatherMap
- `weather_journal/store.py`: saving and reading entries (SQLite)
- `weather_journal/stats.py`: averages, hottest day, rainy days
- `weather_journal/cli.py`: the commands
- `tests/`: tests, run with `python3 -m unittest discover tests`

## Contributing

Fork the repo, make your changes on a new branch, and open a pull request. Run the tests first.

If you find a bug, open an issue with the steps to reproduce it, what you expected, and what happened instead.

Part of Source Start by CSI SPIT. MIT licensed.
