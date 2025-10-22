import json
import os
import time

cache_file = "cache.json"
cache_time = 21600

def load_cache():
    if not os.path.exists(cache_file):
        return {}
    try:
        with open(cache_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}
    
def save_cache(cache):
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=4)

def get_from_cache(key):
    cache = load_cache()
    if key in cache:
        entry = cache[key]
        if time.time() - entry["timestamp"] < cache_time:
            return entry["value"]
    return None

def set_to_cache(key, value):
    cache = load_cache()
    cache[key] = {
        "value": value,
        "timestamp": time.time(),
    }
    save_cache(cache)
