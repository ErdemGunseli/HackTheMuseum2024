import json
from typing import Any


def read_config(key: str, path: str = "config.json") -> Any:
    # 'r' means read-only:
    with open(path, 'r') as file:
        return json.load(file).get(key)