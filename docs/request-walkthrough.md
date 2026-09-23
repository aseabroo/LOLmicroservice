# Following a request through the service

This guide describes the current code. Reading it is a starting point for practicing an explanation and making a change yourself.

## A successful JSON request

1. A client requests `GET /random-champion`. Flask calls `random_champion()`.
2. That function calls `fetch_champion_data()`. Requests downloads the Data Dragon JSON with a five-second network timeout.
3. `raise_for_status()` rejects an unsuccessful HTTP response. `response.json()` turns the response body into Python data.
4. The dictionary comprehension keeps the name, image URL, and sprite coordinates for each champion.
5. `random.choice()` selects one key/value pair. `jsonify()` returns the chosen champion as JSON.

The HTML route uses the same fetch function, then passes one champion's fields into a Jinja template. It shows one random champion, not the entire collection.

## When the upstream request fails

The fetch function returns `None` for a request error, unreadable JSON, missing required fields, or an empty champion collection. Both routes check that result before selecting a champion.

- The JSON route returns an error object and HTTP `503`.
- The HTML route returns an explanatory message and HTTP `503`.

Previously, an unsuccessful HTTP response could produce a string. A nonempty string passes `if data:`, but it has no `.items()` method. That caused the HTML route to fail. Returning a dictionary or `None` gives the routes one predictable success shape and one failure result.

The timeout limits network waiting; it is not a total wall-clock deadline for the whole Flask request.

## How to read the tests

`client` is a Flask test client. It calls the application without starting a separate server.

`upstream` loads a small example response from `tests/fixtures/champions.json`. Pytest's `monkeypatch` temporarily replaces `requests.get` with a mock. Each test can make that mock return data or raise a specific error.

The fixture contains one champion so the expected result does not depend on randomness. A failure test checks the HTTP status and the response the caller actually receives.

During this update, the new suite produced **16 failures and one pass** against the original service. After the fix, **all 17 cases passed**. This was an offline check; it did not verify the live data service.

## Try explaining these in your own words

- What is the difference between a dictionary key and its value in `data['data']`?
- Why does `if data:` accept a nonempty string?
- What happens if the request succeeds but its body is not JSON?
- Why is an empty dictionary a failure for a random-selection endpoint?
- What does mocking the network let the tests verify, and what does it leave unverified?

A useful next exercise is to add a second champion to a copy of the fixture and check that the endpoint returns one complete valid record. Try predicting the result before running the test.

## Scope and assistance

The original project is by Augustus Seabrooke. The September 2026 error-handling update, tests, and this walkthrough were developed with AI assistance.
