import requests

def convert_currency(from_currency, to_currency, amount=1):
    api_key = '8f4479c51842704b08922857fbd36002'  
    url = f'http://data.fixer.io/api/latest?access_key={api_key}&symbols={to_currency}'
    response = requests.get(url)
    if response.status_code != 200:
        return {'error': f'Error fetching conversion rate: {response.status_code}'}
    
    data = response.json()
    if 'error' in data:
        return {'error': data['error']}
    
    conversion_rate = data['rates'].get(to_currency)
    if not conversion_rate:
        return {'error': f'Conversion rate for {to_currency} not found.'}
    
    converted_amount = amount * conversion_rate
    return {'rate': conversion_rate, 'converted_amount': converted_amount}
