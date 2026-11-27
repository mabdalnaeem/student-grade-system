import json
import os

DATA_FILE = "database.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"students": {}, "courses": {}}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {"students": {}, "courses": {}}

def save_data(data):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    except IOError:
        return False