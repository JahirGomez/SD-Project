import requests

def get_places(location):
    api_key = 'AIzaSyAxC582Fdcs-OEDxuTnYEHJFeZYb65B4uE'
    url = f'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={location}&radius=1500&type=restaurant&key={api_key}'
    response = requests.get(url)
    response.raise_for_status()
    return response.json()