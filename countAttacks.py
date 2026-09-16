#!/usr/bin/env python3
"""
Count attacks in Project/EditorListATK.json

Usage:
  python script.py

Behavior:
- Loads Project/EditorListATK.json (errors and exits if missing or invalid JSON).
- Locates an 'atk' list if present; otherwise tries reasonable fallbacks (top-level list,
  first list value in a dict, etc.).
- Counts items that are JSON objects (dicts) and contain the keys:
    'time', 'boxID', 'HeartPosition'
- Prints: Number of attacks: <count>
- Exit codes:
    0 -> success
    1 -> missing file or invalid JSON or unexpected structure
"""
import os
import sys
import json

PROJECT_DIR = "Project"
ATK_FILE = os.path.join(PROJECT_DIR, "EditorListATK.json")
REQUIRED_KEYS = {"time", "boxID", "HeartPosition"}

def load_json_or_exit(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: file not found: {path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: invalid JSON in {path}: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: cannot read {path}: {e}")
        sys.exit(1)

def find_atk_list(data):
    """
    Return a list object that should hold attack dicts, or None if not found.
    Priority:
      1) dict with key 'atk' and list value
      2) top-level list (assume list items are attack dicts)
      3) dict: first value that is a list
    """
    # 1) dict with 'atk'
    if isinstance(data, dict):
        if "atk" in data and isinstance(data["atk"], list):
            return data["atk"]

    # 2) top-level list
    if isinstance(data, list):
        return data

    # 3) any list value inside a dict (first found)
    if isinstance(data, dict):
        for v in data.values():
            if isinstance(v, list):
                return v

    return None

def is_attack_obj(obj):
    if not isinstance(obj, dict):
        return False
    # ensure all required top-level keys exist
    return REQUIRED_KEYS.issubset(set(obj.keys()))

def main():
    data = load_json_or_exit(ATK_FILE)
    atk_list = find_atk_list(data)
    if atk_list is None:
        print(f"Error: could not locate an attack list inside {ATK_FILE}")
        sys.exit(1)

    count = 0
    for item in atk_list:
        if is_attack_obj(item):
            count += 1

    print(f"Number of attacks: {count}")
    sys.exit(0)

if __name__ == "__main__":
    main()