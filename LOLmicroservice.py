from flask import Flask, jsonify
import requests
import random

app = Flask(__name__)

def fetch_champion_data():
    """
    Fetches the data of League of Legends champions from the Riot Games API.

    Returns:
        dict: A dictionary containing champion data.
        str: Error message in case of a failure to fetch data.
    """
    url = "https://ddragon.leagueoflegends.com/cdn/13.23.1/data/en_US/champion.json"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        champions = {
            champ: {
                "name": data['data'][champ]['name'],
                "image": f"http://ddragon.leagueoflegends.com/cdn/13.23.1/img/champion/{champ}.png",
                "sprite": data['data'][champ]['image']['sprite'],
                "x": data['data'][champ]['image']['x'],
                "y": data['data'][champ]['image']['y'],
                "w": data['data'][champ]['image']['w'],
                "h": data['data'][champ]['image']['h']
            }
            for champ in data['data']
        }
        return champions
    else:
        return "Failed to fetch data"

@app.route('/random-champion', methods=['GET'])
def random_champion():
    """
    Endpoint to get a random League of Legends champion's data.

    Returns:
        JSON: A JSON object containing the champion's data.
    """
    champion_data = fetch_champion_data()
    if champion_data and isinstance(champion_data, dict):
        champion_key, champion_info = random.choice(list(champion_data.items()))
        return jsonify(champion_info)
    else:
        return jsonify({"error": "Unable to fetch champion data"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
