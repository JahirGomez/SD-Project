import os
import hashlib
from flask import Flask, request, jsonify, render_template, redirect, url_for
from services.geocoding import get_geocode
from services.country_info import get_country_info
from services.pokemon import get_pokemon_info
from services.currency_conversion import convert_currency
from storage import save_purchase, load_purchases
from security import authenticate, generate_signature, generate_qr_code  # Importa la función generate_qr_code

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key')

USER_FILE = 'users.txt'

def save_user(username, password):
    with open(USER_FILE, 'a') as f:
        f.write(f'{username},{hashlib.sha256(password.encode()).hexdigest()}\n')

def get_users():
    if not os.path.exists(USER_FILE):
        return {}
    with open(USER_FILE, 'r') as f:
        users = {}
        for line in f:
            username, password = line.strip().split(',')
            users[username] = password
        return users

def generate_token(username):
    return hashlib.sha256(username.encode()).hexdigest()

@app.route('/')
def index():
    return redirect(url_for('login_page'))

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data['username']
    password = data['password']
    users = get_users()
    if username in users:
        return jsonify({'error': 'Usuario ya existe'}), 400
    save_user(username, password)
    return jsonify({'message': 'Usuario registrado con éxito'})

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data['username']
    password = hashlib.sha256(data['password'].encode()).hexdigest()
    users = get_users()
    if username not in users or users[username] != password:
        return jsonify({'error': 'Usuario o contraseña incorrectos'}), 400
    token = generate_token(username)
    return jsonify({'message': 'Login exitoso', 'token': token})

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/purchase', methods=['GET', 'POST'])
# @authenticate
def make_purchase():
    if request.method == 'GET':
        return render_template('purchase.html')
    try:
        data = request.json
        app.logger.debug(f"Received data: {data}")
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        user_location = data.get('location')
        pokemon = data.get('pokemon')
        
        app.logger.debug("Calling get_geocode")
        geocode = get_geocode(user_location)
        app.logger.debug(f"Geocode result: {geocode}")
        if geocode is None or 'results' not in geocode or not geocode['results']:
            raise Exception("Geocode API returned no results")
        
        country_code = None
        for component in geocode['results'][0]['address_components']:
            if 'country' in component['types']:
                country_code = component['short_name']
                break
        
        if not country_code:
            raise Exception("Country code not found in geocode results")
        
        app.logger.debug("Calling get_country_info")
        country_info = get_country_info(country_code)
        app.logger.debug(f"Country info result: {country_info}")
        if country_info is None or 'currency' not in country_info or not country_info['currency']:
            raise Exception("Country Info API returned no currency information")
        
        app.logger.debug("Calling get_pokemon_info")
        pokemon_info = get_pokemon_info(pokemon)
        app.logger.debug(f"Pokemon info result: {pokemon_info}")
        if pokemon_info is None:
            raise Exception("Pokemon Info API returned None")
        
        app.logger.debug("Calling convert_currency")
        currency = country_info['currency']
        price_in_usd = 10  # Suponiendo que el precio del Pokémon en USD es 10
        currency_conversion = convert_currency("USD", currency, price_in_usd)
        if 'error' in currency_conversion:
            raise Exception(currency_conversion['error'])
        app.logger.debug(f"Currency conversion result: {currency_conversion}")
        
        purchase = {
            'location': user_location,
            'country_info': country_info,
            'pokemon': pokemon_info,
            'price_in_usd': price_in_usd,
            'price_in_local_currency': currency_conversion['converted_amount']
        }
        
        save_purchase(purchase)
        
        return jsonify({'message': 'Purchase made successfully', 'purchase': purchase})
    except Exception as e:
        app.logger.error(f"Error processing purchase: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/purchases', methods=['GET'])
# @authenticate
def get_purchases():
    purchases = load_purchases()
    return jsonify(purchases)

@app.route('/purchase-result')
# @authenticate
def purchase_result():
    purchases = load_purchases()
    if purchases:
        purchase = purchases[-1]  # Cargar la última compra realizada
    else:
        return jsonify({'error': 'No hay compras registradas'}), 400

    # Ajustar las habilidades y tipos para que sean más legibles en el template
    for ability in purchase['pokemon']['abilities']:
        ability['ability'] = {'name': ability['ability']['name']}
    for type_info in purchase['pokemon']['types']:
        type_info['type'] = {'name': type_info['type']['name']}
    
    # Generar la firma digital
    signature = generate_signature(purchase)
    
    # Generar el código QR de la firma digital
    qr_code = generate_qr_code(signature)
    
    return render_template('purchase_result.html', purchase=purchase, signature=signature, qr_code=qr_code)

if __name__ == '__main__':
    app.run(debug=True)
