import json
import os
import sys

# === USAGE CHECK ===
if len(sys.argv) != 2:
    print("❌ Usage: python auto_increment.py <increment_value>")
    print("Example: python auto_increment.py 1   → adds +1 to all indexATK")
    print("         python auto_increment.py -1  → subtracts 1 from all indexATK")
    sys.exit(1)

# Get increment value from command-line argument
try:
    increment_value = int(sys.argv[1])
except ValueError:
    print("❌ Increment value must be an integer.")
    sys.exit(1)

# === CONFIGURATION ===
input_files = ["Project/EditorAddBoxSetter.json",
"Project/EditorListBoneATK.json",
"Project/EditorListChangeSoulSetter.json",
"Project/EditorListChangeSoulSetterGra.json",
"Project/EditorListCircleBoneATK.json",
"Project/EditorListCircleGasterATK.json",
"Project/EditorListGasterATK.json",
"Project/EditorListHeartPosSetterATK.json",
"Project/EditorListPlatformATK.json",
"Project/EditorListTeleportATK.json",
"Project/EditorListWarningBoxATK.json",
"Project/EditorListCameraEffectATK.json"]  # Add your files here

# === AUTO-SET ORDER ===
reverse_order = increment_value > 0  # end→start for +, start→end for -

# === CORE FUNCTION ===
def increment_indexATK(obj):
    """Recursively go through JSON and modify 'indexATK' values."""
    if isinstance(obj, dict):
        items = list(obj.items())
        if reverse_order:
            items = reversed(items)
        for key, value in items:
            if key == "indexATK" and isinstance(value, int):
                obj[key] = value + increment_value
            else:
                increment_indexATK(value)
    elif isinstance(obj, list):
        iterable = reversed(obj) if reverse_order else obj
        for item in iterable:
            increment_indexATK(item)

# === PROCESS ALL FILES ===
for file in input_files:
    if not os.path.exists(file):
        print(f"⚠️  File not found: {file}")
        continue

    with open(file, "r", encoding="utf-8") as f:
        data = json.load(f)

    increment_indexATK(data)

    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"✅ Processed: {file}")

print(f"\n🎉 Done! All 'indexATK' values {'increased' if increment_value > 0 else 'decreased'} by {abs(increment_value)}.")