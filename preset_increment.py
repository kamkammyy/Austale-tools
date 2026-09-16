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
"Project/EditorListCameraEffectATK.json"]  # Add your files here
increment_value = 1  # +1 to increase, -1 to decrease

# === AUTO-SET ORDER ===
reverse_order = increment_value > 0  # end→start for +1, start→end for -1

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

    # === SAVE RESULT IN PLACE ===
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"✅ Processed: {file}")

print(f"\n🎉 Done! All 'indexATK' values {'increased' if increment_value > 0 else 'decreased'} by {abs(increment_value)}.")