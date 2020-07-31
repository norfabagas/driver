import time

def get_current_unix_time():
    return int(time.time())

def is_duplicate(first_var, second_var):
    if first_var == second_var:
        return True
    else:
        return False

def get_request_header():
    return {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }