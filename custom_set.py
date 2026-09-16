import json
import os
import sys

# === USAGE CHECK ===
if len(sys.argv) != 3:
    print("❌ Usage: python auto_set.py <old_value> <new_value>")
    sys.exit(1)

# Get old/new values from command-line arguments
try:
    old_value = int(sys.argv[1])
    new_value = int(sys.argv[2])
except ValueError:
    print("❌ Both values must be integers.")
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

# === CORE FUNCTION ===
def replace_indexATK(obj):
    """Recursively replace 'indexATK' values."""
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key == "indexATK" and value == old_value:
                obj[key] = new_value
            else:
                replace_indexATK(value)
    elif isinstance(obj, list):
        for item in obj:
            replace_indexATK(item)

# === PROCESS ALL FILES ===
for file in input_files:
    if not os.path.exists(file):
        print(f"⚠️  File not found: {file}")
        continue

    with open(file, "r", encoding="utf-8") as f:
        data = json.load(f)

    replace_indexATK(data)

    # overwrite the same file
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"✅ Updated: {file}")

print(f"\n🎉 Done! All 'indexATK': {old_value} changed to {new_value}.")