import requests 

BASE = "http://127.0.0.1:5000"

def test_root_status():
    response = requests.get(BASE + "/")
    assert response.status_code == 200
    assert "League of Legends (LOL) Microservice is running." in response.text

def test_random_champion():
    response = requests.get(BASE + "/random-champion")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "image" in data
    assert "sprite" in data
    assert "x" in data
    assert "y" in data
    assert "w" in data
    assert "h" in data

def test_html_page_contains_name_and_img():
    response = requests.get(BASE + "/view-champion")   
    assert response.status_code == 200
    assert "<img" in response.text and "<h1>" in response.text