from dataclasses import dataclass
from time import monotonic

import requests


@dataclass
class CacheEntry:
    data: dict
    expires_at: float


class ChampionRepository:
    def __init__(self, patch, timeout=5.0, cache_ttl_seconds=900, session=None):
        self.patch = patch
        self.timeout = timeout
        self.cache_ttl_seconds = cache_ttl_seconds
        self.session = session or requests.Session()
        self._cache = None

    @property
    def data_url(self):
        return (
            "https://ddragon.leagueoflegends.com/cdn/"
            f"{self.patch}/data/en_US/champion.json"
        )

    def image_url(self, champion_id):
        return (
            "https://ddragon.leagueoflegends.com/cdn/"
            f"{self.patch}/img/champion/{champion_id}.png"
        )

    def get_champions(self):
        now = monotonic()
        if self._cache and self._cache.expires_at > now:
            return self._cache.data

        try:
            response = self.session.get(self.data_url, timeout=self.timeout)
            response.raise_for_status()
            payload = response.json()
            champions = self._normalize(payload)
        except (requests.RequestException, ValueError, KeyError, TypeError):
            return self._cache.data if self._cache else None

        if not champions:
            return self._cache.data if self._cache else None

        self._cache = CacheEntry(
            data=champions,
            expires_at=now + self.cache_ttl_seconds,
        )
        return champions

    def clear_cache(self):
        self._cache = None

    def _normalize(self, payload):
        data = payload.get("data") if isinstance(payload, dict) else None
        if not isinstance(data, dict) or not data:
            return None

        champions = {}
        for champion_id, raw in data.items():
            if not isinstance(raw, dict):
                return None

            image = raw.get("image")
            name = raw.get("name")
            if not isinstance(image, dict) or not isinstance(name, str):
                return None

            required = ("sprite", "x", "y", "w", "h")
            if any(field not in image for field in required):
                return None

            champions[champion_id] = {
                "id": champion_id,
                "name": name,
                "image": self.image_url(champion_id),
                "sprite": image["sprite"],
                "x": image["x"],
                "y": image["y"],
                "w": image["w"],
                "h": image["h"],
            }

        return champions
