import json
import os
import sys

file = "Project/EditorListATK.json"

if os.path.exists(file):
    with open(file, "r") as f:
      print(json.dumps(json.load(f), indent=2))
else:
    print("Ur file doesn’t exist")

"""import json

with open("myfile.json", "r") as f:
    data = json.load(f)

print(json.dumps(data, indent=2))"""