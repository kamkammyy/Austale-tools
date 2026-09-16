import json
import os

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
"Project/EditorListCameraEffectATK.json"]  # Add your JSON files here

old_value = -1   # ← the current indexATK value you want to change
new_value = 4   # ← the new value you want to set it to

# === CORE FUNCTION ===
def replace_indexATK(obj):
    """Recursively go through JSON and replace 'indexATK' values."""
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