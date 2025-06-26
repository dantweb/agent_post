import os
import sys
import subprocess
from datetime import datetime
from dotenv import load_dotenv

# Setup paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SRC_DIR = os.path.join(BASE_DIR, 'src')
sys.path.insert(0, SRC_DIR)

# ✅ Import after setting sys.path
from message_repository import MessageRepository
from message import Message

# Load environment variables
load_dotenv(dotenv_path=os.path.join(BASE_DIR, '.env'))
db_url = os.getenv('DATABASE_URL')

if not db_url:
    print("❌ DATABASE_URL not set in .env.")
    sys.exit(1)

def create_database_if_missing():
    from sqlalchemy_utils import database_exists, create_database
    from sqlalchemy import create_engine

    engine = create_engine(db_url)
    if not database_exists(engine.url):
        print(f"🛠️  Creating database: {engine.url.database}")
        create_database(engine.url)
    else:
        print(f"✅ Database already exists: {engine.url.database}")

def run_migrations():
    print("📦 Running Alembic migrations...")
    alembic_ini_path = os.path.join(BASE_DIR, 'alembic.ini')
    if not os.path.exists(alembic_ini_path):
        print("❌ alembic.ini not found. Have you run 'alembic init alembic'?")
        sys.exit(1)
    try:
        subprocess.run(['alembic', 'upgrade', 'head'], check=True, cwd=BASE_DIR)
    except subprocess.CalledProcessError as e:
        print(f"❌ Alembic migration failed: {e}")
        sys.exit(1)

def add_demo_messages():
    print("📝 Adding demo messages...")
    repo = MessageRepository(db_url=db_url)
    if repo.find_all():
        print("⚠️  Messages already exist. Skipping demo inserts.")
        return

    now = datetime.now()
    demo_messages = [
        Message(id=1, created_at=now, collected_at=now, delivered_at=None, from_address="alice", to_address="bob", data="Hello Bob!"),
        Message(id=2, created_at=now, collected_at=now, delivered_at=None, from_address="carol", to_address="dave", data="Data update."),
        Message(id=3, created_at=now, collected_at=now, delivered_at=None, from_address="eve", to_address="mallory", data="Security alert."),
    ]

    for msg in demo_messages:
        repo.save(msg)

    print(f"✅ {len(demo_messages)} demo messages added.")

if __name__ == "__main__":
    print("🚀 Starting setup...")
    create_database_if_missing()
    run_migrations()
    add_demo_messages()
    print("✅ Setup complete.")
