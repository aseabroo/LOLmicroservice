import json
from pathlib import Path
from unittest.mock import Mock

import pytest
import requests

from app import create_app
from champion_data import ChampionRepository


@pytest.fixture
def payload():
    fixture_path = Path(__file__).parent / "fixtures" / "champions.json"
    return json.loads(fixture_path.read_text(encoding="utf-8"))


@pytest.fixture
def session(payload):
    response = Mock()
    response.status_code = 200
    response.json.return_value = payload
    response.raise_for_status.return_value = None

    fake_session = Mock()
    fake_session.get.return_value = response
    return fake_session, response


@pytest.fixture
def repository(session):
    fake_session, _ = session
    return ChampionRepository(
        patch="13.23.1",
        timeout=5,
        cache_ttl_seconds=900,
        session=fake_session,
    )


@pytest.fixture
def client(repository):
    application = create_app(repository)
    application.config.update(TESTING=True)
    return application.test_client()


def test_root_status(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.get_json() == {
        "service": "Champion Randomizer Service",
        "status": "ok",
        "patch": "13.23.1",
        "routes": ["/api/random-champion", "/view-champion"],
    }


def test_random_champion(client):
    response = client.get("/api/random-champion")

    assert response.status_code == 200
    assert response.get_json() == {
        "id": "Ahri",
        "name": "Ahri",
        "image": "https://ddragon.leagueoflegends.com/cdn/13.23.1/img/champion/Ahri.png",
        "sprite": "champion0.png",
        "x": 48,
        "y": 0,
        "w": 48,
        "h": 48,
    }


def test_html_page_contains_champion(client):
    response = client.get("/view-champion")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "<h1>Ahri</h1>" in html
    assert 'alt="Ahri"' in html


def test_repository_caches_successful_response(repository, session):
    fake_session, _ = session

    first = repository.get_champions()
    second = repository.get_champions()

    assert first == second
    fake_session.get.assert_called_once()


@pytest.mark.parametrize(
    "error",
    [
        requests.Timeout("timeout"),
        requests.ConnectionError("connection failed"),
        requests.HTTPError("upstream failed"),
    ],
)
def test_network_failures_return_unavailable(repository, session, error):
    fake_session, response = session

    if isinstance(error, requests.HTTPError):
        response.raise_for_status.side_effect = error
    else:
        fake_session.get.side_effect = error

    repository.clear_cache()
    assert repository.get_champions() is None


def test_invalid_json_returns_unavailable(repository, session):
    _, response = session
    response.json.side_effect = ValueError("invalid json")

    assert repository.get_champions() is None


@pytest.mark.parametrize(
    "bad_payload",
    [
        {"data": {}},
        {"data": []},
        {"data": {"Ahri": {}}},
    ],
)
def test_malformed_payload_returns_unavailable(repository, session, bad_payload):
    _, response = session
    response.json.return_value = bad_payload

    assert repository.get_champions() is None


def test_cached_data_survives_temporary_upstream_failure(repository, session):
    fake_session, _ = session
    expected = repository.get_champions()

    repository._cache.expires_at = 0
    fake_session.get.side_effect = requests.Timeout("temporary outage")

    assert repository.get_champions() == expected


@pytest.mark.parametrize("route", ["/api/random-champion", "/view-champion"])
def test_routes_return_503_without_data(route, session):
    fake_session, _ = session
    fake_session.get.side_effect = requests.ConnectionError("offline")
    repository = ChampionRepository(
        patch="13.23.1",
        timeout=5,
        cache_ttl_seconds=900,
        session=fake_session,
    )
    application = create_app(repository)
    application.config.update(TESTING=True)
    client = application.test_client()

    response = client.get(route)
    assert response.status_code == 503
