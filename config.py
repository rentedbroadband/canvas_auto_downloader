# config.py
import json

def load_config(config_file="config.json"):
    """Load configuration from a JSON file."""
    with open(config_file) as f:
        return json.load(f)
