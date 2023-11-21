import requests
import webbrowser

def fetch_random_champion():
    """
    Fetches a random League of Legends champion's data from the microservice.

    Returns:
        dict: A dictionary containing champion data.
        None: If there was an error in fetching data.
    """
    try:
        response = requests.get('http://127.0.0.1:5000/random-champion')
        if response.status_code == 200:
            return response.json()
        else:
            print("Failed to fetch data from microservice")
            return None
    except requests.RequestException as e:
        print(f"An exception occurred: {e}")
        return None

def main():
    champion_data = fetch_random_champion()
    if champion_data and 'image' in champion_data:
        image_url = champion_data['image']

        # Open the image in the default web browser
        webbrowser.open(image_url)

if __name__ == '__main__':
    main()
