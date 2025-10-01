import os, json

config_file = "config.json"

def load_config():
    if not os.path.exists(config_file):
        return {}
    try:
        with open(config_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print("Error: Config file is corrupted. Loading default config.")
        return {}

def save_config(config):
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)