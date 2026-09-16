import os

# Get a list of items in the current directory that are folders
folders = [f for f in os.listdir('.') if os.path.isdir(f)]

# Check the number of folders
if len(folders) == 0:
    print("There are no folders in the current directory.")
elif len(folders) > 1:
    print("There is more than one folder in the current directory.")
else:
    # Only one folder, rename it
    old_name = folders[0]
    new_name = "Project"
    
    try:
        os.rename(old_name, new_name)
        print(f"Folder renamed successfully: '{old_name}' -> '{new_name}'")
    except Exception as e:
        print(f"Failed to rename folder '{old_name}': {e}")