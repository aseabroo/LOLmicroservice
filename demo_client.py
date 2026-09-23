import requests


def main():
    response = requests.get(
        "http://127.0.0.1:5000/api/random-champion",
        timeout=5,
    )
    response.raise_for_status()
    champion = response.json()

    print(f"Champion: {champion['name']}")
    print(f"Image: {champion['image']}")


if __name__ == "__main__":
    main()
