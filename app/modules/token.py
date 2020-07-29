import jwt, requests, os
from typing import Tuple, Mapping, Any

def get_token_secret() -> Tuple[int, str]:
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    response = requests.get(os.getenv("AUTH_GATE_URL") + "/api-secret", headers=headers)
    if response.status_code == 200:
        return response.status_code, response.json()['data']
    else:
        return response.status_code, ""

def decode_token(token: str) -> Mapping[str, Any]:
    _, secret = get_token_secret()
    return jwt.decode(token, secret, algorithms=['HS256'])

def get_user_id(token: str) -> str:
    decoded_jwt = decode_token(token)
    return decoded_jwt['user_id']