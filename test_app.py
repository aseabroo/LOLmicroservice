import json
from pathlib import Path
from unittest.mock import Mock

import pytest
import requests

import LOLmicroservice as service


@pytest.fixture
def client():
    service.app.config.update(TESTING=True)
    return service.app.test_client()


@pytest.fixture
def upstream(monkeypatch):
    fixture_path = Path(__file__).parent / "tests" / "fixtures" / "champions.json"
    payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    response = Mock()
    response.status_code = 200
    response.json.return_value = payload
    response.raise_for_status.return_value = None
    get = Mock(return_value=response)
    monkeypatch.setattr(service.requests, "get", get)
    return get, response


def test_root_status(client, upstream):
    get, _ = upstream
    response = client.get("/")

    assert response.status_code == 200
    assert response.get_json() == {
        "message": "League of Legends (LOL) Microservice is running.",
        "usage": ["/random-champion", "/view-champion"],
    }
    get.assert_not_called()


def test_random_champion(client, upstream):
    get, _ = upstream
    response = client.get("/random-champion")

    assert response.status_code == 200
    assert response.get_json() == {
        "name": "Ahri",
        "image": "https://ddragon.leagueoflegends.com/cdn/13.23.1/img/champion/Ahri.png",
        "sprite": "champion0.png",
        "x": 48,
        "y": 0,
        "w": 48,
        "h": 48,
    }
    get.assert_called_once_with(
        "https://ddragon.leagueoflegends.com/cdn/13.23.1/data/en_US/champion.json",
        timeout=5,
    )


def test_html_page_contains_name_and_img(client, upstream):
    response = client.get("/view-champion")

    assert response.status_code == 200
    assert response.mimetype == "text/html"
    html = response.get_data(as_text=True)
    assert "<h1>Ahri</h1>" in html
    assert 'alt="Ahri"' in html
    assert 'src="https://ddragon.leagueoflegends.com/cdn/13.23.1/img/champion/Ahri.png"' in html


def assert_unavailable(response, route):
    assert response.status_code == 503
    message = "Champion data is temporarily unavailable. Please try again."
    if route == "/random-champion":
        assert response.mimetype == "application/json"
        assert response.get_json() == {"error": message}
    else:
        assert response.mimetype == "text/html"
        assert message in response.get_data(as_text=True)


@pytest.mark.parametrize("route", ["/random-champion", "/view-champion"])
@pytest.mark.parametrize("error_type", [requests.Timeout, requests.ConnectionError])
def test_network_failure_returns_unavailable(client, upstream, route, error_type):
    get, _ = upstream
    get.side_effect = error_type("simulated upstream failure")

    assert_unavailable(client.get(route), route)


@pytest.mark.parametrize("route", ["/random-champion", "/view-champion"])
def test_upstream_http_error_returns_unavailable(client, upstream, route):
    _, response = upstream
    response.status_code = 503
    response.raise_for_status.side_effect = requests.HTTPError("upstream unavailable")

    assert_unavailable(client.get(route), route)


@pytest.mark.parametrize("route", ["/random-champion", "/view-champion"])
def test_invalid_json_returns_unavailable(client, upstream, route):
    _, response = upstream
    response.json.side_effect = ValueError("invalid JSON")

    assert_unavailable(client.get(route), route)


@pytest.mark.parametrize("route", ["/random-champion", "/view-champion"])
@pytest.mark.parametrize("payload", [
    {"data": {}},
    {"data": []},
    {"data": {"Ahri": {}}},
])
def test_unusable_data_returns_unavailable(client, upstream, route, payload):
    _, response = upstream
    response.json.return_value = payload

    assert_unavailable(client.get(route), route)
