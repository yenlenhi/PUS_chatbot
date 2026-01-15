"""
Generate secure JWT secret key for Railway deployment
"""

import secrets
import sys


def generate_jwt_secret():
    """Generate a secure 64-character hexadecimal secret key"""
    return secrets.token_hex(32)


def main():
    print("=" * 70)
    print("🔐 JWT Secret Key Generator for Railway Deployment")
    print("=" * 70)
    print()

    # Generate key
    secret_key = generate_jwt_secret()

    print("✅ Generated secure JWT secret key:")
    print()
    print(f"   {secret_key}")
    print()
    print("=" * 70)
    print("📋 Next Steps:")
    print("=" * 70)
    print()
    print("1. Copy the key above")
    print("2. Go to Railway Dashboard → Your Service → Variables")
    print("3. Add/Update variable:")
    print("   Key: JWT_SECRET_KEY")
    print(f"   Value: {secret_key}")
    print()
    print("4. Save and redeploy")
    print()
    print("⚠️  IMPORTANT:")
    print("   - Never commit this key to Git")
    print("   - Store it securely (password manager)")
    print("   - Rotate periodically (every 3-6 months)")
    print("=" * 70)
    print()

    # Additional keys
    print("Optional: Generate additional keys for other purposes:")
    print()
    print(f"REFRESH_TOKEN_SECRET: {secrets.token_hex(32)}")
    print(f"ENCRYPTION_KEY: {secrets.token_hex(32)}")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelled by user")
        sys.exit(1)
