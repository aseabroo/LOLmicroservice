import os
import random

from flask import Flask, jsonify, render_template

from champion_data import ChampionRepository


def create_app(repository=None):
    app = Flask(__name__)
    app.config["CHAMPION_REPOSITORY"] = repository or ChampionRepository(
        patch=os.getenv("DDRAGON_PATCH", "13.23.1"),
        timeout=float(os.getenv("UPSTREAM_TIMEOUT_SECONDS", "5")),
        cache_ttl_seconds=int(os.getenv("CACHE_TTL_SECONDS", "900")),
    )

    @app.get("/")
    def index():
        repo = app.config["CHAMPION_REPOSITORY"]
        return jsonify({
            "service": "Champion Randomizer Service",
            "status": "ok",
            "patch": repo.patch,
            "routes": ["/api/random-champion", "/view-champion"],
        })

    @app.get("/api/random-champion")
    def random_champion():
        champions = app.config["CHAMPION_REPOSITORY"].get_champions()
        if not champions:
            return jsonify({
                "error": "Champion data is temporarily unavailable. Please try again."
            }), 503

        champion = random.choice(list(champions.values()))
        return jsonify(champion)

    @app.get("/view-champion")
    def view_champion():
        champions = app.config["CHAMPION_REPOSITORY"].get_champions()
        if not champions:
            return render_template("unavailable.html"), 503

        champion = random.choice(list(champions.values()))
        return render_template("champion.html", champion=champion)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.getenv("PORT", "5000")), debug=False)
