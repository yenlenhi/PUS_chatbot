#!/usr/bin/env python3
"""
Script to check existing data in SQLite database before migration
"""
import sqlite3
import os
from pathlib import Path
import json

def check_sqlite_data():
    """Check data in SQLite database"""
    db_path = Path("data/embeddings/chatbot.db")
    
    if not db_path.exists():
        print(f"❌ SQLite database not found at {db_path}")
        return
    
    print(f"📂 SQLite Database: {db_path}")
    print(f"📊 File size: {db_path.stat().st_size / 1024 / 1024:.2f} MB")
    print()
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print("=" * 60)
        print("📋 TABLES IN SQLITE DATABASE")
        print("=" * 60)
        
        if not tables:
            print("❌ No tables found in database")
            return
        
        total_records = 0
        
        for table_name, in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            total_records += count
            
            # Get column info
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            print(f"\n📊 Table: {table_name}")
            print(f"   Records: {count}")
            print(f"   Columns: {len(columns)}")
            for col_id, col_name, col_type, not_null, default, pk in columns:
                print(f"      - {col_name} ({col_type})")
            
            # Show sample data for non-empty tables
            if count > 0:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 1")
                sample = cursor.fetchone()
                print(f"   Sample record: {sample[:2] if len(sample) > 2 else sample}...")
        
        print()
        print("=" * 60)
        print(f"📈 TOTAL RECORDS: {total_records}")
        print("=" * 60)
        
        # Detailed stats for chunks and embeddings
        print("\n🔍 DETAILED STATISTICS:")
        
        cursor.execute("SELECT COUNT(*) FROM chunks")
        chunks_count = cursor.fetchone()[0]
        print(f"   Chunks: {chunks_count}")
        
        cursor.execute("SELECT COUNT(*) FROM embeddings")
        embeddings_count = cursor.fetchone()[0]
        print(f"   Embeddings: {embeddings_count}")
        
        cursor.execute("SELECT COUNT(*) FROM conversations")
        conversations_count = cursor.fetchone()[0]
        print(f"   Conversations: {conversations_count}")
        
        # Check embedding dimensions
        if embeddings_count > 0:
            cursor.execute("SELECT embedding FROM embeddings LIMIT 1")
            sample_embedding = cursor.fetchone()[0]
            if sample_embedding:
                try:
                    embedding_list = json.loads(sample_embedding)
                    print(f"   Embedding dimensions: {len(embedding_list)}")
                except:
                    print(f"   Embedding format: {type(sample_embedding)}")
        
        conn.close()
        print("\n✅ SQLite check completed successfully!")
        
    except Exception as e:
        print(f"❌ Error checking SQLite database: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_sqlite_data()

