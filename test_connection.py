"""
Simple script to test PostgreSQL connection
"""

import os
from sqlalchemy import create_engine, text

def test_connection():
    """Test PostgreSQL connection with different connection strings"""
    
    # Try different connection strings
    connection_strings = [
        "postgresql://postgres:postgres@localhost:5432/karsfinance_db",
        "postgresql://postgres:postgres@127.0.0.1:5432/karsfinance_db",
        "postgresql://postgres:postgres@host.docker.internal:5432/karsfinance_db",
    ]
    
    print("🔌 Testing PostgreSQL connections...")
    print("=" * 50)
    
    for i, conn_str in enumerate(connection_strings, 1):
        print(f"\n{i}. Testing: {conn_str}")
        try:
            engine = create_engine(conn_str)
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1 as test"))
                row = result.fetchone()
                if row and row[0] == 1:
                    print("✅ Connection successful!")
                    
                    # Try to list databases
                    try:
                        result = conn.execute(text("SELECT datname FROM pg_database WHERE datistemplate = false;"))
                        databases = [row[0] for row in result.fetchall()]
                        print(f"📋 Available databases: {databases}")
                    except Exception as e:
                        print(f"⚠️  Could not list databases: {e}")
                    
                    return conn_str
                else:
                    print("❌ Connection failed - unexpected result")
        except Exception as e:
            print(f"❌ Connection failed: {e}")
    
    print("\n❌ All connection attempts failed")
    return None

def check_docker_status():
    """Check if Docker containers are running"""
    print("\n🐳 Checking Docker status...")
    print("=" * 30)
    
    try:
        import subprocess
        result = subprocess.run(["docker", "ps"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Docker is running")
            if "karsfinance_postgres" in result.stdout:
                print("✅ PostgreSQL container is running")
            else:
                print("⚠️  PostgreSQL container not found")
                print("Try: docker-compose up -d postgres")
        else:
            print("❌ Docker is not running or not accessible")
    except Exception as e:
        print(f"❌ Could not check Docker status: {e}")

if __name__ == "__main__":
    check_docker_status()
    working_connection = test_connection()
    
    if working_connection:
        print(f"\n🎉 Working connection string: {working_connection}")
        print("\n💡 Update your DATABASE_URL or api.py with this connection string")
    else:
        print("\n❌ No working connection found")
        print("\n🔧 Troubleshooting steps:")
        print("1. Make sure Docker is running")
        print("2. Run: docker-compose up -d postgres")
        print("3. Wait 10-15 seconds for PostgreSQL to start")
        print("4. Check: docker logs karsfinance_postgres")
