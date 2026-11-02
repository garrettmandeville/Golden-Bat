"""
Data Loading Module

Description: Loads game content (rooms, items, story, audio config) from the JSON
             files in the data folder.
"""

import json
from goldenbat.paths import resource_path

def load_json(filename):
    """Reads and parses a JSON file from the data folder."""
    with open(resource_path("data", filename), encoding = "utf-8") as file:
        return json.load(file)
