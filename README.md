# Random League of Legends champion

A small Python/Flask service that fetches champion data from Riot's Data Dragon and returns a random champion as JSON or a simple HTML page.

## Run locally

Use Python 3.10 or newer.

```bash
git clone https://github.com/aseabroo/LOLmicroservice.git
cd LOLmicroservice
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python LOLmicroservice.py
```

On Windows, activate the environment with `.venv\Scripts\activate`.

| Route | Response |
| --- | --- |
| `/` | Service message and available routes |
| `/random-champion` | One champion's name, image URL, and sprite coordinates |
| `/view-champion` | A simple HTML page for one champion |

Open http://127.0.0.1:5000/view-champion. Champion requests need an internet connection.

## Tests

Keep the server running and use a second terminal with the environment activated:

```bash
python -m pytest test_app.py -v
```

The three existing tests make HTTP requests to the running server. They check the root response, JSON fields, and HTML tags. They are integration smoke tests and depend on the external data service.

`testMicroservice.py` provides a manual preview. `main.py` is an optional macOS/Linux helper that starts the server and runs the checks; it waits for Enter before stopping the server on the successful path.

## Limitations and next steps

- The data URL is fixed to patch `13.23.1`.
- External requests need timeouts and better error handling, especially on the HTML route.
- The tests should eventually use a saved response for repeatable checks.
- The helper needs reliable cleanup when a test fails.

## Diagram and data source

![Original service diagram](uml_diagram.png)

Champion data and images come from [Riot Games Data Dragon](https://developer.riotgames.com/docs/lol#data-dragon). Project code by Augustus Seabrooke; see [LICENSE](LICENSE).
