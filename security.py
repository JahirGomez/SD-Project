from functools import wraps
from flask import request, jsonify
import hashlib
import os
import json
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
import qrcode
from io import BytesIO
import base64

USER_FILE = 'users.txt'

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

def authenticate(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if token:
            token = token.split(' ')[1] if ' ' in token else token
            users = get_users()
            valid_tokens = [generate_token(user) for user in users]
            if token in valid_tokens:
                return f(*args, **kwargs)
        return jsonify({'message': 'Authentication required!'}), 403
    return decorated_function

def generate_keys():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    with open("private_key.pem", "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))

    public_key = private_key.public_key()
    with open("public_key.pem", "wb") as f:
        f.write(public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))

def generate_signature(data):
    if not os.path.exists("private_key.pem"):
        generate_keys()
    
    with open("private_key.pem", "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
        )

    data_bytes = json.dumps(data).encode('utf-8')

    signature = private_key.sign(
        data_bytes,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

    return signature.hex()

def verify_signature(data, signature):
    if not os.path.exists("public_key.pem"):
        generate_keys()
        
    with open("public_key.pem", "rb") as key_file:
        public_key = serialization.load_pem_public_key(
            key_file.read()
        )

    data_bytes = json.dumps(data).encode('utf-8')
    signature_bytes = bytes.fromhex(signature)

    try:
        public_key.verify(
            signature_bytes,
            data_bytes,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except Exception as e:
        return False

def generate_qr_code(data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill='black', back_color='white')
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
    return img_str