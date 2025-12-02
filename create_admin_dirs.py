import os
import pathlib

base_path = r"C:\TruongVanKhai\Project\uni_bot\frontend\src"

# Create admin directories
directories = [
    "app/admin",
    "app/admin/dashboard",
    "app/admin/chat-history",
    "app/admin/documents",
    "components/admin",
]

print("Creating directories...")
for dir_path in directories:
    full_path = os.path.join(base_path, dir_path.replace("/", "\\"))
    pathlib.Path(full_path).mkdir(parents=True, exist_ok=True)
    print(f"✓ Created: {dir_path}")

print("\n✓ All directories created successfully!")

# List created directories
admin_path = os.path.join(base_path, "app", "admin")
print(f"\nContents of {admin_path}:")
for item in os.listdir(admin_path):
    print(f"  - {item}")
