#!/usr/bin/env python3
"""
script.py — fixed insertion logic

- All-or-nothing: if any required file is missing or has unexpected structure, print error and exit without writing.
- Appends:
  - to EditorListATK.json -> append to top-level 'atk' list (creates 'atk' list if dict doesn't have it)
  - to EditorListStringDialogBeforeAttackAndString.json -> append into the inner 'dialog' list
  - to EditorListStringDialog.json -> append into the inner 'text' list
- time is always written as float.
Usage:
    python script.py        # default 20.0
    python script.py 40     # 40.0
"""

import os
import sys
import json
import tempfile

PROJECT_DIR = "Project"
ATK_FILE = os.path.join(PROJECT_DIR, "EditorListATK.json")
BEFORE_FILE = os.path.join(PROJECT_DIR, "EditorListStringDialogBeforeAttackAndString.json")
STRING_FILE = os.path.join(PROJECT_DIR, "EditorListStringDialog.json")
DEFAULT_TIME = 20.0

def parse_time_arg(argv):
    if len(argv) > 1 and str(argv[1]).strip() != "":
        try:
            return float(argv[1])
        except (ValueError, TypeError):
            print(f"Warning: couldn't parse '{argv[1]}' as number — using default {DEFAULT_TIME}")
    return float(DEFAULT_TIME)

def atomic_write(path, data):
    fd, tmp_path = tempfile.mkstemp(prefix=".tmp_", dir=os.path.dirname(path) or ".")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as tmpf:
            json.dump(data, tmpf, ensure_ascii=False, indent=2)
        os.replace(tmp_path, path)
    except Exception:
        try: os.remove(tmp_path)
        except Exception: pass
        raise

def load_json_or_err(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: required file missing: {path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: invalid JSON in {path}: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: cannot read {path}: {e}")
        sys.exit(1)

def new_atk_entry(time_value):
    return {
        "time": float(time_value),
        "boxID": 0,
        "HeartPosition": {"x": 3.3499999046325685, "y": 1.6100000143051148}
    }

NEW_BEFORE_ENTRY = {"numberOfDialogueBeforeAttackCome": 1, "textInBox": "* Placeholder"}
NEW_STRING_ENTRY = {"text": "Placeholder"}

def find_inner_list_for_key(data, key_name):
    """
    Return a tuple (container, list_ref) where:
      - container is the object we will modify (either a dict or list element)
      - list_ref is the actual list object (so we can append)
    If not found or unexpected structure -> return (None, None)
    """
    # Case: data is dict and has key_name as list
    if isinstance(data, dict):
        if key_name in data and isinstance(data[key_name], list):
            return (data, data[key_name])
        # if key missing but dict is acceptable, create key as list (we'll create later)
        return (data, None)

    # Case: data is list -> search for first element that's a dict and has key_name as list
    if isinstance(data, list):
        for elem in data:
            if isinstance(elem, dict) and key_name in elem and isinstance(elem[key_name], list):
                return (elem, elem[key_name])
        # If none found, but first element is dict and doesn't have key, we could opt to create it there.
        # We'll return the first dict element to allow preserving existing structure.
        for elem in data:
            if isinstance(elem, dict):
                return (elem, None)

    return (None, None)

def prepare_atk_mod(data, time_value):
    """
    Returns modified data in memory (not written yet), or exits on unexpected structure.
    Acceptable:
      - dict (will use/create data['atk'] list)
      - list (will append new entry as a top-level element)
    """
    new_entry = new_atk_entry(time_value)
    if isinstance(data, dict):
        if "atk" in data:
            if not isinstance(data["atk"], list):
                print(f"Error: 'atk' key exists but is not a list in {ATK_FILE}")
                sys.exit(1)
            # append
            data["atk"].append(new_entry)
        else:
            # create atk key (preserve other keys)
            data["atk"] = [new_entry]
        return data

    if isinstance(data, list):
        data.append(new_entry)
        return data

    print(f"Error: unexpected structure in {ATK_FILE} (must be dict or list).")
    sys.exit(1)

def prepare_before_mod(data):
    """
    Insert NEW_BEFORE_ENTRY into the inner 'dialog' list.
    If 'dialog' list exists inside the dict or inside the first dict element of top-level list, append to it.
    If 'dialog' missing but a dict container exists, create 'dialog':[existing?] -> but we will append the new entry into it.
    """
    container, inner = find_inner_list_for_key(data, "dialog")
    if container is None:
        print(f"Error: could not locate a 'dialog' container in {BEFORE_FILE}.")
        sys.exit(1)

    if inner is None:
        # create dialog list on that container and append
        # container must be a dict
        if not isinstance(container, dict):
            print(f"Error: cannot create 'dialog' list in {BEFORE_FILE} - unexpected container.")
            sys.exit(1)
        container["dialog"] = [NEW_BEFORE_ENTRY]
    else:
        inner.append(NEW_BEFORE_ENTRY)

    return data

def prepare_string_mod(data):
    """
    Insert NEW_STRING_ENTRY into the inner 'text' list.
    Similar logic to prepare_before_mod but for 'text'.
    """
    container, inner = find_inner_list_for_key(data, "text")
    if container is None:
        print(f"Error: could not locate a 'text' container in {STRING_FILE}.")
        sys.exit(1)

    if inner is None:
        if not isinstance(container, dict):
            print(f"Error: cannot create 'text' list in {STRING_FILE} - unexpected container.")
            sys.exit(1)
        # If container already has text as scalar, convert? Safer to create list with existing converted first.
        existing = container.get("text")
        if existing is None:
            container["text"] = [NEW_STRING_ENTRY]
        elif isinstance(existing, list):
            existing.append(NEW_STRING_ENTRY)
        else:
            # convert existing scalar to list
            container["text"] = [{"text": existing}, NEW_STRING_ENTRY]
    else:
        inner.append(NEW_STRING_ENTRY)

    return data

def main(argv):
    time_value = parse_time_arg(argv)

    # 1) Ensure files exist (all-or-nothing)
    for p in (ATK_FILE, BEFORE_FILE, STRING_FILE):
        if not os.path.exists(p):
            print(f"Error: required file missing: {p}")
            sys.exit(1)

    # 2) Load everything (exit on invalid JSON)
    atk_data = load_json_or_err(ATK_FILE)
    before_data = load_json_or_err(BEFORE_FILE)
    string_data = load_json_or_err(STRING_FILE)

    # 3) Prepare modifications in memory (validate structures)
    atk_mod = prepare_atk_mod(atk_data, time_value)
    before_mod = prepare_before_mod(before_data)
    string_mod = prepare_string_mod(string_data)

    # 4) All validations passed — write atomically
    atomic_write(ATK_FILE, atk_mod)
    atomic_write(BEFORE_FILE, before_mod)
    atomic_write(STRING_FILE, string_mod)

    print(f"Success: appended new attack (time = {float(time_value)}). Files updated in '{PROJECT_DIR}/'.")

if __name__ == "__main__":
    main(sys.argv)