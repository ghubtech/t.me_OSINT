import json
import logging
import asyncio
import aiosqlite
from datetime import datetime
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/tg_osint.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

DATA_DIR = Path("output")
DATA_DIR.mkdir(exist_ok=True)

async def save_to_json(data: dict, filename: str):
    """Save data to JSON file"""
    filepath = DATA_DIR / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False, default=str)
    logger.info(f"Data saved to {filepath}")

async def init_db():
    """Initialize SQLite database"""
    async with aiosqlite.connect("tg_osint.db") as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS members (
                id INTEGER PRIMARY KEY,
                group_id INTEGER,
                user_id INTEGER,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                is_admin BOOLEAN,
                timestamp TEXT
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY,
                chat_id INTEGER,
                message_id INTEGER,
                sender_id INTEGER,
                text TEXT,
                date TEXT,
                views INTEGER,
                forwards INTEGER
            )
        ''')
        await db.commit()
    logger.info("Database initialized.")

async def log_action(action: str, target: str, details: str = ""):
    """Log actions"""
    logger.info(f"Action: {action} | Target: {target} | Details: {details}")
