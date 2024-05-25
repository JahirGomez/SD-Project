# tests/test_app.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
import pytest

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index_redirect(client):
    response = client.get('/')
    assert response.status_code == 302  # Redirección a la página de login


def test_login(client):
    client.post('/register', json={
        "username": "test_user",
        "password": "test_password"
    })
    response = client.post('/login', json={
        "username": "test_user",
        "password": "test_password"
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Login exitoso'
    assert 'token' in data
