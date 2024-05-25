import unittest
from unittest.mock import patch
from services import weather, country_info, currency_conversion, geocoding, places, pokemon

class TestServices(unittest.TestCase):

    @patch('services.weather.requests.get')
    def test_get_weather_info(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"location": {"name": "London"}, "current": {"temp_c": 15}}
        response = weather.get_weather_info('London')
        self.assertEqual(response['location']['name'], 'London')
        self.assertEqual(response['current']['temp_c'], 15)
    
    @patch('services.country_info.Client')
    def test_get_country_info(self, mock_client):
        mock_service = mock_client.return_value.service
        mock_service.FullCountryInfo.return_value = type('obj', (object,), {
            'sName': 'United Kingdom', 
            'sCurrencyISOCode': 'GBP', 
            'sCapitalCity': 'London', 
            'sContinentCode': 'EU', 
            'sPhoneCode': '44'
        })
        response = country_info.get_country_info('GB')
        self.assertEqual(response['name'], 'United Kingdom')
        self.assertEqual(response['currency'], 'GBP')
        self.assertEqual(response['capital'], 'London')
    
    @patch('services.currency_conversion.requests.get')
    def test_convert_currency(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {'rates': {'USD': 1.2}}
        response = currency_conversion.convert_currency('EUR', 'USD', 10)
        self.assertEqual(response['converted_amount'], 12.0)
    
    @patch('services.geocoding.requests.get')
    def test_get_geocode(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {'results': [{'geometry': {'location': {'lat': 51.5074, 'lng': -0.1278}}}]}
        response = geocoding.get_geocode('London')
        self.assertEqual(response['results'][0]['geometry']['location']['lat'], 51.5074)
    
    @patch('services.places.requests.get')
    def test_get_places(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {'results': [{'name': 'Restaurant'}]}
        response = places.get_places('51.5074,-0.1278')
        self.assertEqual(response['results'][0]['name'], 'Restaurant')
    
    @patch('services.pokemon.requests.get')
    def test_get_pokemon_info(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {'name': 'pikachu', 'abilities': [{'ability': {'name': 'static'}}]}
        response = pokemon.get_pokemon_info('pikachu')
        self.assertEqual(response['name'], 'pikachu')
        self.assertEqual(response['abilities'][0]['ability']['name'], 'static')

if __name__ == '__main__':
    unittest.main()
