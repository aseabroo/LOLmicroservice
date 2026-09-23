from flask import Flask, jsonify, render_template_string
import requests
import random

app = Flask(__name__)

def fetch_champion_data():
    """
    Fetch champion data from Riot Games Data Dragon.

    Returns:
        dict: Champion data when the upstream response is usable.
        None: The request failed or the response contained no usable data.
    """
    url = "https://ddragon.leagueoflegends.com/cdn/13.23.1/data/en_US/champion.json"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, dict) or not isinstance(data.get('data'), dict):
            return None
        champions = {
            champ: {
                "name": data['data'][champ]['name'],
                "image": f"https://ddragon.leagueoflegends.com/cdn/13.23.1/img/champion/{champ}.png",
                "sprite": data['data'][champ]['image']['sprite'],
                "x": data['data'][champ]['image']['x'],
                "y": data['data'][champ]['image']['y'],
                "w": data['data'][champ]['image']['w'],
                "h": data['data'][champ]['image']['h']
            }
            for champ in data['data']
        }
        return champions or None
    except (requests.RequestException, ValueError, KeyError, TypeError):
        return None

@app.route('/')
def index():
    return jsonify({
        'message': "League of Legends (LOL) Microservice is running.",
        'usage': ["/random-champion", "/view-champion"],
    })

@app.route('/random-champion', methods=['GET'])
def random_champion():
    """
    Endpoint to get a random League of Legends champion's data.

    Returns:
        JSON: A JSON object containing the champion's data.
    """
    champion_data = fetch_champion_data()
    if champion_data:
        _, champion_info = random.choice(list(champion_data.items()))
        return jsonify(champion_info)
    else:
        return jsonify({
            "error": "Champion data is temporarily unavailable. Please try again."
        }), 503

@app.route('/view-champion')
def view_champion():
    """
    Endpoint to view one random League of Legends champion.

    Returns:
        HTML: The champion's name and image, or an unavailable message.
    """
    data = fetch_champion_data()
    if data:
        _, champ = random.choice(list(data.items()))
        return render_template_string("""
            <html><body style="text-align: center;">
                <h1>{{ name }}</h1>
                <img src="{{ image }}" alt="{{ name }}" style="height: 300px;"/>
                <p><a href="/view-champion"> New Random Champion</a></p>
            </body></html> 
        """, **champ)
    return "<h1>Champion data is temporarily unavailable. Please try again.</h1>", 503
   

if __name__ == '__main__':
    app.run(host="127.0.0.1",  port=5000, debug=False)
