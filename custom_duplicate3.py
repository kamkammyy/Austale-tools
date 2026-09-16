import json
import sys
import os
import copy

# === Argument Parsing ===
if len(sys.argv) != 8:
    print("Usage: python custom_duplicate3.py [b|g|w|p] wait_inc waitToBeChanged_flag affect_layer_flag x_inc y_inc dup_count")
    sys.exit(1)

type_key = sys.argv[1].lower()
wait_inc = float(sys.argv[2])

waitToBeChanged_flag = sys.argv[3].lower() in ("true", "1", "yes")
affect_layer_flag = sys.argv[4].lower() in ("true", "1", "yes")

x_inc = float(sys.argv[5])
y_inc = float(sys.argv[6])
dup_count = int(sys.argv[7])

if dup_count <= 0:
    print("No duplicates requested (dup_count == 0). Nothing changed.")
    sys.exit(0)

# === File mapping ===
file_map = {
    "b": ("Project/EditorListBoneATK.json", "bone"),
    "g": ("Project/EditorListGasterATK.json", "gaster"),
    "w": ("Project/EditorListWarningBoxATK.json", "warnBox"),
    "p": ("Project/EditorListPlatformATK.json", "plat"),
}

if type_key not in file_map:
    print("Error: invalid type key. Must be one of [b, g, w, p].")
    sys.exit(1)

file_path, list_key = file_map[type_key]

if not os.path.exists(file_path):
    print(f"Error: file not found: {file_path}")
    sys.exit(1)

# === Load JSON ===
try:
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
except Exception as e:
    print(f"Error reading {file_path}: {e}")
    sys.exit(1)

if not isinstance(data, dict) or list_key not in data or not isinstance(data[list_key], list):
    print(f"Error: unexpected structure in {file_path}. Expected key '{list_key}' containing a list.")
    sys.exit(1)

items = data[list_key]

# === Find object with duplication ===
dup_index = None
for i, obj in enumerate(items):
    if isinstance(obj.get("duplication"), dict) and not obj["duplication"]:
        dup_index = i
        break

if dup_index is None:
    print("❌ No object with empty 'duplication' found. Cancelling.")
    sys.exit(1)

base_obj = items[dup_index]

# === Recursive modification ===
def adjust_fields(obj, i):
    if isinstance(obj, dict):
        for key, val in obj.items():
            if isinstance(val, (int, float)):
                if key == "waitToBeEnabled" and type_key in ("b", "g", "p"):
                    obj[key] = round(val + wait_inc * i, 6)
                elif key == "waitToBeChanged" and waitToBeChanged_flag:
                    obj[key] = round(val + wait_inc * i, 6)
                elif key == "startTime" and type_key == "w":
                    obj[key] = round(val + wait_inc * i, 6)
                elif key == "x":
                    obj[key] = round(val + x_inc * i, 6)
                elif key == "y":
                    obj[key] = round(val + y_inc * i, 6)
                elif key == "layer" and affect_layer_flag:
                    obj[key] = val + 1 * i
            else:
                adjust_fields(val, i)
    elif isinstance(obj, list):
        for elem in obj:
            adjust_fields(elem, i)

# === Create duplicates ===
duplicates = []
for i in range(1, dup_count + 1):
    new_obj = copy.deepcopy(base_obj)
    if "duplication" in new_obj:
        del new_obj["duplication"]
    adjust_fields(new_obj, i)
    duplicates.append(new_obj)

# Move duplication marker
if "duplication" in base_obj:
    del base_obj["duplication"]
duplicates[-1]["duplication"] = {}

# Insert new objects
items[dup_index + 1:dup_index + 1] = duplicates

# === Calculate highest timing ===
def find_highest_timing(obj, current_max=0.0):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, (int, float)):
                if type_key in ("b", "g", "p") and k == "waitToBeEnabled":
                    current_max = max(current_max, v)
                elif type_key == "w" and k == "startTime":
                    current_max = max(current_max, v)
            else:
                current_max = find_highest_timing(v, current_max)
    elif isinstance(obj, list):
        for e in obj:
            current_max = find_highest_timing(e, current_max)
    return current_max

highest = find_highest_timing(data)

# === Write JSON back ===
tmp_path = file_path + ".tmp"
with open(tmp_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
os.replace(tmp_path, file_path)

label = "startTime" if type_key == "w" else "waitToBeEnabled"
print("✅ Duplication complete.")
print(f"Highest {label} after duplication: {highest:.1f}")