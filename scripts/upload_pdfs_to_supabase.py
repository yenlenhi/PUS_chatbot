"""
Upload all PDFs to Supabase Storage
"""

import requests
from pathlib import Path

# Supabase Configuration
SUPABASE_URL = "https://thessjemstjljfbkvzih.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRoZXNzamVtc3RqbGpmYmt2emloIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NzI5OTYzMiwiZXhwIjoyMDgyODc1NjMyfQ.wwO_vinoN1mhUkKDae6f_ao65QBBMt2Q5OonFk_k_Q8"

# Storage bucket name
BUCKET_NAME = "documents"

# PDF directory - search recursively
PDF_DIR = Path("data")


def create_bucket():
    """Create storage bucket if not exists"""
    url = f"{SUPABASE_URL}/storage/v1/bucket"
    headers = {
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "apikey": SUPABASE_KEY,
        "Content-Type": "application/json",
    }

    # Check if bucket exists
    response = requests.get(url, headers=headers)
    buckets = response.json()

    bucket_exists = (
        any(b.get("name") == BUCKET_NAME for b in buckets)
        if isinstance(buckets, list)
        else False
    )

    if not bucket_exists:
        print(f"📦 Creating bucket '{BUCKET_NAME}'...")
        data = {
            "id": BUCKET_NAME,
            "name": BUCKET_NAME,
            "public": True,  # Make files publicly accessible
            "file_size_limit": 52428800,  # 50MB limit
        }
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            print(f"  ✅ Bucket '{BUCKET_NAME}' created!")
        else:
            print(f"  ⚠️ Bucket creation response: {response.text}")
    else:
        print(f"  ✅ Bucket '{BUCKET_NAME}' already exists")


def upload_file(file_path: Path):
    """Upload a single file to Supabase Storage"""
    file_name = file_path.name

    url = f"{SUPABASE_URL}/storage/v1/object/{BUCKET_NAME}/{file_name}"
    headers = {
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "apikey": SUPABASE_KEY,
    }

    with open(file_path, "rb") as f:
        file_data = f.read()

    # Determine content type
    content_type = "application/pdf"
    headers["Content-Type"] = content_type

    response = requests.post(url, headers=headers, data=file_data)

    if response.status_code == 200:
        public_url = (
            f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET_NAME}/{file_name}"
        )
        return True, public_url
    else:
        # Try upsert if file exists
        response = requests.put(url, headers=headers, data=file_data)
        if response.status_code == 200:
            public_url = (
                f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET_NAME}/{file_name}"
            )
            return True, public_url
        return False, response.text


def main():
    print("=" * 60)
    print("📤 UPLOAD PDFs TO SUPABASE STORAGE")
    print("=" * 60)

    # Create bucket
    create_bucket()

    # Find all PDFs recursively in all subdirectories
    pdf_files = list(PDF_DIR.rglob("*.pdf"))
    print(f"\n📄 Found {len(pdf_files)} PDF files in data/ and subdirectories")

    # Show breakdown by folder
    folders = {}
    for pdf in pdf_files:
        folder = str(pdf.parent.relative_to(PDF_DIR))
        if folder not in folders:
            folders[folder] = []
        folders[folder].append(pdf.name)

    for folder, files in folders.items():
        print(f"   📁 {folder}: {len(files)} files")

    # Upload each file
    print("\n🚀 Uploading files...")
    uploaded = []
    failed = []

    for pdf in pdf_files:
        file_size = pdf.stat().st_size / 1024 / 1024  # MB
        print(f"\n  📎 {pdf.name} ({file_size:.2f} MB)")

        success, result = upload_file(pdf)
        if success:
            print("     ✅ Uploaded!")
            print(f"     🔗 {result}")
            uploaded.append({"name": pdf.name, "url": result})
        else:
            print(f"     ❌ Failed: {result[:100]}")
            failed.append(pdf.name)

    # Summary
    print("\n" + "=" * 60)
    print("📊 UPLOAD SUMMARY")
    print("=" * 60)
    print(f"  ✅ Uploaded: {len(uploaded)}")
    print(f"  ❌ Failed: {len(failed)}")

    if uploaded:
        print("\n📎 Uploaded files:")
        for f in uploaded:
            print(f"  - {f['name']}")
            print(f"    URL: {f['url']}")

    if failed:
        print("\n❌ Failed files:")
        for f in failed:
            print(f"  - {f}")

    # Save URLs to file
    if uploaded:
        import json

        with open("data/pdf_urls.json", "w", encoding="utf-8") as f:
            json.dump(uploaded, f, ensure_ascii=False, indent=2)
        print("\n💾 URLs saved to data/pdf_urls.json")

    print("\n🎉 Done!")


if __name__ == "__main__":
    main()
