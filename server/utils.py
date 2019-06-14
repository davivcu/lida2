################################################################################
# IMPORTS
################################################################################

# >>>> Native <<<<
import os
import json





################################################################################
# CODE
################################################################################

def load_json_file(path: str) -> Any:
    """Loads a JSON file."""
    with open(path, "r") as f:
        content = json.load(f)
    return content


def save_json_file(obj: Any, path: str) -> None:
    """Saves a JSON file."""
    with open(path, "w") as f:
        json.dump(obj, f, indent=4)
