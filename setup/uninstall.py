import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy_utils import database_exists, drop_database
from dotenv import load_dotenv

# Setup paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
load_dotenv(dotenv_path=os.path.join(BASE_DIR, '.env'))

db_url = os.getenv('DATABASE_URL')

if not db_url:
    print("❌ DATABASE_URL not set in .env.")
    sys.exit(1)

def uninstall_database():
    print(f"🗑️ Attempting to drop database: {db_url}")
    engine = create_engine(db_url)

    if db_url.startswith('sqlite:///'):
        # SQLite: remove the .db file
        db_file = db_url.replace('sqlite:///', '')
        if os.path.exists(db_file):
            os.remove(db_file)
            print(f"✅ SQLite database file removed: {db_file}")
        else:
            print(f"⚠️ SQLite database file does not exist: {db_file}")
    else:
        # PostgreSQL or others
        if database_exists(engine.url):
            drop_database(engine.url)
            print("✅ Database dropped.")
        else:
            print("⚠️ Database does not exist.")

if __name__ == "__main__":
    uninstall_database()
