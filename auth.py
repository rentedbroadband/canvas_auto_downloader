# auth.py
import requests
import json
from config import load_config

def load_cookies():
    config = load_config()
    with open(config["COOKIES_FILE"], "r") as f:
        cookies_json = json.load(f)
    if isinstance(cookies_json, dict):
        return cookies_json
    return {cookie["name"]: cookie["value"] for cookie in cookies_json}

def create_session():
    session = requests.Session()
    session.cookies.update(load_cookies())
    return session
