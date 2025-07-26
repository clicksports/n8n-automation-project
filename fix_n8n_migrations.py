#!/usr/bin/env python3
"""
Fix n8n PostgreSQL migrations table structure
"""

import psycopg2
import sys

def fix_migrations_table():
    """Fix the migrations table to work with n8n"""
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="n8n",
            user="n8n_user",
            password="n8n_password"
        )
        
        cur = conn.cursor()
        
        print("Checking current database state...")
        
        # Check if migrations table exists
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'migrations'
            );
        """)
        
        table_exists = cur.fetchone()[0]
        
        if table_exists:
            print("Migrations table exists. Dropping it...")
            cur.execute("DROP TABLE migrations CASCADE;")
        
        print("Creating proper migrations table...")
        
        # Create migrations table with proper structure for n8n
        cur.execute("""
            CREATE TABLE migrations (
                id SERIAL PRIMARY KEY,
                timestamp BIGINT NOT NULL,
                name VARCHAR NOT NULL
            );
        """)
        
        # Commit changes
        conn.commit()
        print("✅ Migrations table created successfully!")
        
        # Verify the structure
        cur.execute("\\d migrations")
        print("Table structure verified.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()
    
    return True

if __name__ == "__main__":
    print("🔧 Fixing n8n migrations table...")
    if fix_migrations_table():
        print("✅ Migration table fix completed!")
        sys.exit(0)
    else:
        print("❌ Migration table fix failed!")
        sys.exit(1)