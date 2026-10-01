import asyncio
import json
import os
import sys
from datetime import datetime, date
from uuid import UUID

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from sqlalchemy import text
from app.database import SessionLocal, engine

from decimal import Decimal
import enum

def json_serial(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, UUID):
        return str(obj)
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, enum.Enum):
        return obj.value
    if isinstance(obj, bytes):
        return obj.hex()
    return str(obj)

async def create_backup():
    assert "vrip_db_qa" in str(engine.url), "Must be QA db"
    print(f"Creating backup of {engine.url}...")
    
    backup_data = {}
    async with SessionLocal() as s:
        tables_res = await s.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name
        """))
        tables = [r[0] for r in tables_res.fetchall()]

        for t in tables:
            rows_res = await s.execute(text(f'SELECT * FROM "{t}"'))
            columns = list(rows_res.keys())
            rows = rows_res.fetchall()
            backup_data[t] = [dict(zip(columns, row)) for row in rows]
            print(f"Backed up {t}: {len(rows)} rows")

    os.makedirs("database", exist_ok=True)
    backup_file = "database/vrip_db_qa_backup.json"
    with open(backup_file, "w", encoding="utf-8") as f:
        json.dump(backup_data, f, default=json_serial, indent=2)
    print(f"\nBackup successfully saved to {backup_file}")

if __name__ == "__main__":
    asyncio.run(create_backup())
