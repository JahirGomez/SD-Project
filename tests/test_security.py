# tests/test_security.py
import sys
import os
from flask import Flask
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from security import generate_signature, verify_signature, generate_token, get_users, authenticate

def test_generate_and_verify_signature():
    data = {"test": "data"}
    signature = generate_signature(data)
    assert verify_signature(data, signature) is True

    # Create an invalid signature by altering the valid signature
    invalid_signature = signature[:-1] + ('0' if signature[-1] != '0' else '1')
    assert verify_signature(data, invalid_signature) is False

app = Flask(__name__)

def test_generate_token():
    username = "test_user"
    token = generate_token(username)
    assert len(token) == 64

def test_authenticate(mocker):
    mock_request = mocker.Mock()
    mock_request.headers = {"Authorization": "Bearer valid_token"}
    mocker.patch('security.get_users', return_value={"test_user": "hashed_password"})
    mocker.patch('security.generate_token', return_value="valid_token")

    @authenticate
    def test_func():
        return True

    with app.test_request_context('/some_endpoint', headers={"Authorization": "Bearer valid_token"}):
        response = test_func()
        assert response is True