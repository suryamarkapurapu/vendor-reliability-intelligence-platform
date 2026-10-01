import asyncio
import json
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from sqlalchemy import text
from app.database import SessionLocal, engine

async def backup_and_audit():
    print(f"Connecting to DB: {engine.url}")
    assert "vrip_db_qa" in str(engine.url), "Must be QA db"

    async with SessionLocal() as s:
        # Check all tables in database
        tables_res = await s.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name
        """))
        tables = [r[0] for r in tables_res.fetchall()]
        print(f"Total tables found: {len(tables)}")
        
        counts = {}
        for t in tables:
            cnt_res = await s.execute(text(f'SELECT COUNT(*) FROM "{t}"'))
            counts[t] = cnt_res.scalar()
        
        print("\nTable Counts:")
        for t, c in counts.items():
            print(f"  {t}: {c}")

        # Check users
        users_res = await s.execute(text("SELECT user_id, username, email, role_id, is_active FROM users"))
        users = users_res.fetchall()
        print("\nUsers:")
        for u in users:
            print(f"  {u}")

        # Check roles
        roles_res = await s.execute(text("SELECT role_id, role_name FROM roles"))
        roles = roles_res.fetchall()
        print("\nRoles:")
        for r in roles:
            print(f"  {r}")

        # Check vendor categories
        cat_res = await s.execute(text("SELECT category_id, category_name FROM vendor_categories"))
        cats = cat_res.fetchall()
        print("\nVendor Categories:")
        for c in cats:
            print(f"  {c}")

if __name__ == "__main__":
    asyncio.run(backup_and_audit())
