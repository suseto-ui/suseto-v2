from flask import request

def current_user():
    return 'anonymous'

def body():
    return request.get_json(silent=True) or {}
