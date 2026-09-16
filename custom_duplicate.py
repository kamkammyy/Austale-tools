import json
import sys
import os
import copy

# File paths
BONE_PATH = "Project/EditorListBoneATK.json"
GASTER_PATH = "Project/EditorListGasterATK.json"


def adjust_wait_values(obj, wait_add, mult):
    """
    Recursively adjust all waitToBeEnabled values in an object.
    """
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "waitToBeEnabled" and isinstance(v, (int, float)):
                obj[k] = round(v + wait_add * mult, 6)
            else:
                adjust_wait_values(v, wait_add, mult)
    elif isinstance(obj, list):
        for item in obj:
            adjust_wait_values(item, wait_add, mult)


def find_and_duplicate(data, key, wait_add, dup_count):
    """
    Finds the object with duplication: {} and duplicates it dup_count times.
    Adjusts all waitToBeEnabled values in each duplicate.
    """
    items = data.get(key, [])
    target_index = None

    # Find object with duplication: {}
    for i, obj in enumerate(items):
        if isinstance(obj.get("duplication"), dict) and not obj["duplication"]:
            target_index = i
            break

    if target_index is None:
        print("❌ No object with an empty 'duplication' field found. Cancelling.")
        sys.exit(1)

    target = items[target_index]

    # Generate duplicates
    duplicates = []
    for i in range(1, dup_count + 1):
        dup = copy.deepcopy(target)
        dup.pop("duplication", None)  # remove the duplication tag
        adjust_wait_values(dup, wait_add, i)
        duplicates.append(dup)

    # Insert after target
    items[target_index + 1:target_index + 1] = duplicates
    data[key] = items
    return data


def get_highest_wait_value(data):
    """
    Finds the highest waitToBeEnabled value anywhere in the data.
    """
    highest = float("-inf")

    def recurse(obj):
        nonlocal highest
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k == "waitToBeEnabled" and isinstance(v, (int, float)):
                    highest = max(highest, v)
                recurse(v)
        elif isinstance(obj, list):
            for item in obj:
                recurse(item)

    recurse(data)
    return highest if highest != float("-inf") else None


def main():
    if len(sys.argv) != 4:
        print("Usage: python custom_duplicate.py [b/g] [wait_add] [dup_count]")
        sys.exit(1)

    target = sys.argv[1].lower()
    wait_add = float(sys.argv[2])
    dup_count = int(sys.argv[3])

    if target not in ("b", "g"):
        print("❌ Invalid target. Use 'b' for bone or 'g' for gaster.")
        sys.exit(1)

    file_path = BONE_PATH if target == "b" else GASTER_PATH
    key = "bone" if target == "b" else "gaster"

    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        sys.exit(1)

    # Load file
    with open(file_path, "r") as f:
        data = json.load(f)

    # Duplicate
    updated = find_and_duplicate(data, key, wait_add, dup_count)

    # Overwrite file
    with open(file_path, "w") as f:
        json.dump(updated, f, indent=2)

    # Print highest waitToBeEnabled
    highest = get_highest_wait_value(updated)
    if highest is not None:
        print(f"✅ Duplication complete.\nHighest waitToBeEnabled after duplication: {highest:.1f}")
    else:
        print("⚠️ No waitToBeEnabled values found.")


if __name__ == "__main__":
    main()