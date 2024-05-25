import requests

def get_weather_info(city):
    api_key = '81c3fc3622134f9e9b622717242005'
    url = f'http://api.weatherapi.com/v1/current.json?key={api_key}&q={city}'
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def get_timezone_info(city):
    api_key = '81c3fc3622134f9e9b622717242005'
    url = f'http://api.weatherapi.com/v1/timezone.json?key={api_key}&q={city}'
    response = requests.get(url)
    response.raise_for_status()
    return response.json()