import jwt, requests, os
from typing import Tuple, Mapping, Any

def get_token_secret() -> Tuple[int, str]:
    accepted_token = os.getenv("ACCEPTED_TOKEN")

    headers = {
        "Authorization": 'Bearer ' + accepted_token
    }

    response = requests.get(os.getenv("AUTH_SERVICE_URL") + "/api-secret", headers=headers)
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