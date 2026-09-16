import json
import sys
import os
import copy
import tempfile

# === Command-line argument parsing ===
if len(sys.argv) != 7:
    print("Usage: python custom_duplicate2.py [b|g|w|p] wait_inc waitToBeChanged_flag x_inc y_inc dup_count")
    sys.exit(1)

type_arg = sys.argv[1].lower()
wait_inc = float(sys.argv[2])
waitToBeChanged_flag = sys.argv[3].lower() in ("true", "1")
x_inc = float(sys.argv[4])
y_inc = float(sys.argv[5])
dup_count = int(sys.argv[6])

file_map = {
    "b": ("Project/EditorListBoneATK.json", "bone"),
    "g": ("Project/EditorListGasterATK.json", "gaster"),
    "w": ("Project/EditorListWarningBoxATK.json", "warnBox"),
    "p": ("Project/EditorListPlatformATK.json", "plat")
}

if type_arg not in file_map:
    print(f"Error: unknown type '{type_arg}'. Must be one of b,g,w,p")
    sys.exit(1)

file_path, top_key = file_map[type_arg]

if not os.path.isfile(file_path):
    print(f"Error: file not found: {file_path}")
    sys.exit(1)

# === Load JSON file ===
try:
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
except Exception as e:
    print(f"Error reading JSON: {e}")
    sys.exit(1)

if top_key not in data or not isinstance(data[top_key], list):
    print(f"Error: expected list under key '{top_key}'")
    sys.exit(1)

items = data[top_key]

# === Find first object with empty duplication marker ===
base_idx = None
for idx, item in enumerate(items):
    if isinstance(item.get("duplication"), dict) and not item["duplication"]:
        base_idx = idx
        break

if base_idx is None:
    print("❌ No object with an empty 'duplication' field found. Cancelling.")
    sys.exit(1)

if dup_count == 0:
    print("No duplicates requested (dup_count == 0). Nothing changed.")
    sys.exit(0)

base_item = items[base_idx]

# === Recursive update function ===
def traverse_and_adjust(obj, i):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if type_arg != "w" and k == "waitToBeEnabled" and isinstance(v, (int, float)):
                obj[k] = round(v + wait_inc * i, 6)
            elif type_arg == "w" and k == "startTime" and isinstance(v, (int, float)):
                obj[k] = round(v + wait_inc * i, 6)
            elif waitToBeChanged_flag and k == "waitToBeChanged" and isinstance(v, (int, float)):
                obj[k] = round(v + wait_inc * i, 6)
            elif k == "x" and isinstance(v, (int, float)):
                obj[k] = round(v + x_inc * i, 6)
            elif k == "y" and isinstance(v, (int, float)):
                obj[k] = round(v + y_inc * i, 6)
            else:
                traverse_and_adjust(v, i)
    elif isinstance(obj, list):
        for elem in obj:
            traverse_and_adjust(elem, i)

# === Build duplicates ===
duplicates = []
for i in range(1, dup_count + 1):
    dup = copy.deepcopy(base_item)
    dup.pop("duplication", None)
    traverse_and_adjust(dup, i)
    duplicates.append(dup)

# === Insert duplicates and move duplication marker ===
items[base_idx + 1:base_idx + 1] = duplicates
# Remove duplication from original
if "duplication" in items[base_idx]:
    items[base_idx].pop("duplication")
# Add duplication to last duplicate
items[base_idx + dup_count]["duplication"] = {}

# === Write back to file atomically ===
try:
    fd, tmp_path = tempfile.mkstemp(dir=os.path.dirname(file_path), text=True)
    with os.fdopen(fd, "w", encoding="utf-8") as tmp_file:
        json.dump(data, tmp_file, indent=2, ensure_ascii=False)
    os.replace(tmp_path, file_path)
except Exception as e:
    print(f"Error writing file: {e}")
    sys.exit(1)

# === Compute highest wait/start time ===
def find_highest(obj):
    max_val = None
    if isinstance(obj, dict):
        for k, v in obj.items():
            if type_arg != "w" and k == "waitToBeEnabled" and isinstance(v, (int, float)):
                max_val = max(max_val, v) if max_val is not None else v
            elif type_arg == "w" and k == "startTime" and isinstance(v, (int, float)):
                max_val = max(max_val, v) if max_val is not None else v
            else:
                sub_max = find_highest(v)
                if sub_max is not None:
                    max_val = max(max_val, sub_max) if max_val is not None else sub_max
    elif isinstance(obj, list):
        for elem in obj:
            sub_max = find_highest(elem)
            if sub_max is not None:
                max_val = max(max_val, sub_max) if max_val is not None else sub_max
    return max_val

highest = find_highest(items)
if highest is None:
    if type_arg == "w":
        print("No startTime values found.")
    else:
        print("No waitToBeEnabled values found.")
else:
    label = "startTime" if type_arg == "w" else "waitToBeEnabled"
    print("✅ Duplication complete.")
    print(f"Highest {label} after duplication: {highest:.1f}")