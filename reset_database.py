"""
Reset script to completely start fresh with PostgreSQL
This will stop containers, remove volumes, and start fresh
"""

import subprocess
import sys
import os
import time

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()}")
        else:
            print(f"⚠️  {description} had issues: {result.stderr.strip()}")
        return result.returncode == 0
    except Exception as e:
        print(f"❌ {description} failed: {e}")
        return False

def main():
    """Main reset function"""
    print("🔄 KarsFinance Database Reset")
    print("=" * 40)
    
    # Step 1: Stop and remove containers
    print("\n📦 Stopping and removing containers...")
    run_command("docker-compose down", "Stopping containers")
    
    # Step 2: Remove volumes (this deletes all data)
    print("\n🗑️  Removing database volumes...")
    run_command("docker volume rm financialweb_postgres_data 2>/dev/null || true", "Removing postgres volume")
    
    # Step 3: Pull latest images
    print("\n📥 Pulling latest images...")
    run_command("docker-compose pull", "Pulling PostgreSQL image")
    
    # Step 4: Start fresh PostgreSQL
    print("\n🚀 Starting fresh PostgreSQL...")
    if not run_command("docker-compose up -d postgres", "Starting PostgreSQL container"):
        print("❌ Failed to start PostgreSQL. Check Docker is running.")
        sys.exit(1)
    
    # Step 5: Wait for PostgreSQL to be ready
    print("\n⏳ Waiting for PostgreSQL to be ready...")
    time.sleep(10)  # Give PostgreSQL time to start
    
    # Step 6: Test connection
    print("\n🔌 Testing database connection...")
    try:
        import psycopg2
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database="karsfinance_db",
            user="postgres",
            password="postgres"
        )
        conn.close()
        print("✅ Database connection successful")
    except ImportError:
        print("⚠️  psycopg2 not installed, skipping connection test")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("   PostgreSQL might still be starting up. Wait a bit longer.")
        return False
    
    print("\n🎉 Reset completed successfully!")
    print("\n📝 Next steps:")
    print("1. Run: python setup_database.py")
    print("2. Start API: python api.py")
    print("3. Test: http://localhost:8000")
    
    return True

if __name__ == "__main__":
    main()
