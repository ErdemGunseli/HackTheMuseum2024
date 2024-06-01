import json
from typing import Any

# Utility function to read from a JSON file:
def read_config(key: str, path: str = "config.json") -> Any:
    # 'r' means read-only:
    with open(path, 'r') as file:
        return json.load(file).get(key)