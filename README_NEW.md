# Champion Randomizer Service

A small Flask service that fetches League of Legends champion metadata from Riot's Data Dragon and returns a random champion through a JSON API or a lightweight HTML interface.

## What it demonstrates

- Python and Flask API development
- external HTTP service integration
- response normalization and validation
- timeout and failure handling
- TTL caching
- dependency injection for testability
- mocked upstream responses with pytest
- JSON and server-rendered HTML responses
- GitHub Actions CI

## API

| Route | Response |
| --- | --- |
| `/` | Service metadata |
| `/api/random-champion` | Random champion as JSON |
| `/view-champion` | Random champion HTML page |

Example response:

```json
{
  "id": "Ahri",
  "name": "Ahri",
  "image": "https://ddragon.leagueoflegends.com/cdn/13.23.1/img/champion/Ahri.png",
  "sprite": "champion0.png",
  "x": 48,
  "y": 0,
  "w": 48,
  "h": 48
}
```

## Architecture

```text
Browser / API client
        |
        v
      Flask
        |
        v
ChampionRepository
   |          |
   |          +---- TTL cache
   |
   +---- Riot Data Dragon
```

The Flask layer is intentionally thin. Data fetching, normalization, caching, and upstream error handling live in `ChampionRepository`.

## Caching behavior

Successful champion metadata is cached in memory for a configurable TTL. This avoids downloading the full champion dataset on every request.

If the cache has expired and Data Dragon temporarily fails, the repository serves the last successful cached value when one exists. If no usable value has ever been cached, the application returns HTTP `503`.

## Configuration

Copy:

```bash
cp .env.example .env
```

Supported environment variables:

| Variable | Default | Purpose |
| --- | --- | --- |
| `PORT` | `5000` | Local Flask port |
| `DDRAGON_PATCH` | `13.23.1` | Data Dragon patch |
| `UPSTREAM_TIMEOUT_SECONDS` | `5` | Riot request timeout |
| `CACHE_TTL_SECONDS` | `900` | Champion metadata cache lifetime |

The application reads these variables from the environment. A shell or process manager can load `.env`; the file is provided as a configuration example rather than committed credentials.

## Run locally

```bash
git clone https://github.com/aseabroo/champion-randomizer-service.git
cd champion-randomizer-service

python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py
```

Then open:

```text
http://127.0.0.1:5000/view-champion
```

## Tests

```bash
python -m pytest -q
```

The automated tests do not require a running server or internet connection. Data Dragon requests are replaced with controlled responses and a small fixture.

Coverage includes:

- successful JSON response
- HTML rendering
- caching
- request timeouts
- connection failures
- upstream HTTP failures
- invalid JSON
- malformed champion data
- stale-cache fallback
- `503` behavior when no usable data exists

## Demo client

With the server running:

```bash
python demo_client.py
```

The demo client calls the JSON endpoint and prints the selected champion and image URL.

## Project Structure

```text
champion-randomizer-service/
├── app.py
├── champion_data.py
├── demo_client.py
├── static/
│   └── styles.css
├── templates/
│   ├── champion.html
│   └── unavailable.html
├── tests/
│   ├── fixtures/
│   │   └── champions.json
│   └── test_app.py
├── .github/workflows/test.yml
├── .env.example
├── requirements.txt
└── README.md
```

## Data source

Champion metadata and images are provided by Riot Games Data Dragon.

League of Legends and Riot Games are trademarks or registered trademarks of Riot Games, Inc. This project is not endorsed by or affiliated with Riot Games.

## Project note

This is a learning and portfolio project focused on API integration, resilience, caching, and automated testing.
