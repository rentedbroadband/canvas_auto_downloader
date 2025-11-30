# download_log.py
import os
import json
from config import load_config

def get_log_file():
    config = load_config()
    log_file = config["DOWNLOAD_LOG_FILE"]
    os.makedirs(os.path.dirname(log_file) or '.', exist_ok=True)
    return log_file

def load_download_log():
    """Load the download log from file. Creates an empty log if the file doesn't exist."""
    log_file = get_log_file()
    try:
        if os.path.exists(log_file):
            with open(log_file, "r") as f:
                return json.load(f)
    except Exception as e:
        print(f"Warning: Could not load download log: {e}")
    return {}

def save_download_log(log):
    """Save the download log to file."""
    log_file = get_log_file()
    try:
        with open(log_file, "w") as f:
            json.dump(log, f, indent=2)
    except Exception as e:
        print(f"Warning: Could not save download log: {e}")

def is_already_downloaded(file_path, log):
    """Check if a file is already in the download log."""
    return os.path.abspath(file_path) in log

def add_to_download_log(file_path, log):
    """Add a file to the download log."""
    log[os.path.abspath(file_path)] = True
    save_download_log(log)
