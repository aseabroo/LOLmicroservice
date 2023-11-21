import requests

def get_random_champion():
    url = 'http://127.0.0.1:5000/random-champion'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return "Error: Unable to fetch data from the microservice"

# Example usage
champion_data = get_random_champion()
print(champion_data)
