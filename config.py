import json
from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parent / "credentials.json"

def get_config():
    with open(str(CONFIG_PATH), "r") as f:
        config = json.load(f)
    return config
