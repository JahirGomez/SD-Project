import requests

def get_geocode(address):
    api_key = 'AIzaSyAkF2KiehQXQpyck9amjRIxBqk1YvP7YHU'
    url = f'https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={api_key}'
    response = requests.get(url)
    response.raise_for_status()
    return response.json()