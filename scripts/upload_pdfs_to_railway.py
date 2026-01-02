"""
Script to upload PDF files to Railway volume
This script creates a tar archive of all PDF files and uploads to Railway
"""

import tarfile
from pathlib import Path

# Directories containing PDFs
PDF_DIRS = [
    "data/DU LIEU AI",
    "data/forms",
    "data/new_pdf",
    "data/not_process",
    "data/not_process_1",
    "data/not_process_2",
    "data/pdfs",
    "data/processed",
]


def create_pdf_archive():
    """Create tar.gz archive of all PDF files preserving directory structure"""
    print("📦 Creating PDF archive...")

    base_dir = Path(__file__).parent.parent
    archive_path = base_dir / "pdfs_backup.tar.gz"

    with tarfile.open(archive_path, "w:gz") as tar:
        for pdf_dir in PDF_DIRS:
            dir_path = base_dir / pdf_dir
            if dir_path.exists():
                # Count PDFs in this directory
                pdf_files = list(dir_path.rglob("*.pdf"))
                print(f"  Adding {len(pdf_files)} PDFs from {pdf_dir}")

                for pdf_file in pdf_files:
                    # Keep relative path structure
                    arcname = pdf_file.relative_to(base_dir)
                    tar.add(pdf_file, arcname=arcname)

    size_mb = archive_path.stat().st_size / (1024 * 1024)
    print(f"✅ Archive created: {archive_path} ({size_mb:.2f} MB)")
    return archive_path


def upload_to_railway(archive_path):
    """Upload archive to Railway and extract it"""
    print("\n🚀 Uploading to Railway...")

    # Upload file to Railway volume
    service_name = "PUS_chatbot"
    volume_path = "/app/data"

    print(f"  Uploading to {service_name}:{volume_path}")

    # Copy archive to Railway
    cmd = (
        f'railway run --service {service_name} -- sh -c "cat > /tmp/pdfs_backup.tar.gz"'
    )
    print(f"  Command: {cmd}")
    print("  Note: Run this manually with: ")
    print(
        f'    cat "{archive_path}" | railway run --service {service_name} -- sh -c "cat > /tmp/pdfs_backup.tar.gz && cd /app && tar -xzf /tmp/pdfs_backup.tar.gz && rm /tmp/pdfs_backup.tar.gz"'
    )

    return True


def main():
    print("=" * 60)
    print("Upload PDFs to Railway Volume")
    print("=" * 60)

    # Step 1: Create archive
    archive_path = create_pdf_archive()

    # Step 2: Provide upload instructions
    print("\n" + "=" * 60)
    print("📋 Upload Instructions:")
    print("=" * 60)
    print("\nOption 1: Using Railway CLI (Recommended)")
    print("-" * 60)
    print("Run this command in PowerShell:")
    print(
        f'Get-Content "{archive_path}" -Raw -AsByteStream | railway run --service PUS_chatbot -- sh -c "cat > /tmp/pdfs.tar.gz && cd /app && tar -xzf /tmp/pdfs.tar.gz && rm /tmp/pdfs.tar.gz && ls -lh data/"'
    )

    print("\n\nOption 2: Using Railway Dashboard")
    print("-" * 60)
    print("1. Go to Railway Dashboard")
    print("2. Select PUS_chatbot service")
    print("3. Go to 'Volumes' tab")
    print("4. Use the file browser to upload files")
    print(f"5. Upload this file: {archive_path}")

    print("\n\nOption 3: Deploy with volume sync (Best for production)")
    print("-" * 60)
    print("Add this to your railway.json:")
    print(
        """{
  "deploy": {
    "numReplicas": 1,
    "healthcheckPath": "/health",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  },
  "build": {
    "builder": "NIXPACKS"
  }
}"""
    )
    print(
        "\nThen add data/ to .railwayignore (if not already) to avoid uploading with each deploy"
    )

    print("\n" + "=" * 60)
    print("✅ Archive ready for upload!")
    print("=" * 60)


if __name__ == "__main__":
    main()
