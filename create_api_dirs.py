import os
import pathlib

base_path = r"C:\TruongVanKhai\Project\uni_bot\frontend\src\app\api"

# Create API directories
directories = [
    "admin/documents/[filename]",
    "admin/stats",
    "admin/chat-history"
]

print("Creating API directories...")
for dir_path in directories:
    full_path = os.path.join(base_path, dir_path.replace('/', '\\'))
    pathlib.Path(full_path).mkdir(parents=True, exist_ok=True)
    print(f"✓ Created: {dir_path}")

print("\n✓ All API directories created successfully!")
