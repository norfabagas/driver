from flask import session
from .globals import *

def generate_auth_session(
        authorized_status: bool,
        expiry: int,
        user_id: str,
        name: str,
        email: str,
        token: str):
    session[user_id] = {
        'authorized': authorized_status,
        'exp': expiry,
        'name': name,
        'email': email,
        'token': token
    }

def is_session_valid(user_id) -> bool:
    if session.get(user_id):
        if session.get(user_id)['exp'] >= get_current_unix_time():
            return True
        else:
            session.pop(user_id)
            return False
    else:
        return False