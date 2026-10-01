"""
Safe cleanup script for vrip_db_qa.
Preserves roles, vendor categories, and primary admin accounts.
Deletes all business transaction records respecting foreign key constraints.
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from sqlalchemy import text
from app.database import SessionLocal, engine

async def clean_qa_database():
    assert "vrip_db_qa" in str(engine.url), f"Refusing to run on non-QA database: {engine.url}"
    print(f"Connecting to QA database: {engine.url}")

    async with SessionLocal() as s:
        # Step 1: Clean leaf transaction tables first
        tables_to_clean = [
            "message_attachments",
            "messages",
            "delivery_tracking",
            "invoices",
            "purchase_order_items",
            "purchase_orders",
            "contracts",
            "procurement_requests",
            "vendor_ratings",
            "vendor_issues",
            "vendor_performance_metrics",
            "vendor_reliability_scores",
            "reliability_score_history",
            "certifications",
            "compliance_records",
            "vendor_documents",
            "vendor_contacts",
            "activity_logs",
            "notifications",
            "password_reset_tokens",
            "reports",
        ]

        for t in tables_to_clean:
            try:
                await s.execute(text(f"DELETE FROM {t}"))
                print(f"Cleared table: {t}")
            except Exception as e:
                print(f"Error clearing {t}: {e}")
                await s.rollback()

        # Step 2: Clear vendors table (all FKs referencing vendors are now deleted)
        try:
            await s.execute(text("DELETE FROM vendors"))
            print("Cleared table: vendors")
        except Exception as e:
            print(f"Error clearing vendors: {e}")
            await s.rollback()

        # Step 3: Clean test users, keeping active admins
        try:
            # Preserve primary admin accounts
            await s.execute(text("""
                DELETE FROM users 
                WHERE username NOT IN ('admin_vendor', 'amar', 'sai', 'admin')
            """))
            print("Cleaned test users (preserved admin accounts)")
        except Exception as e:
            print(f"Error cleaning users: {e}")
            await s.rollback()

        # Step 4: Reset user settings for preserved admin
        try:
            await s.execute(text("DELETE FROM user_settings WHERE user_id NOT IN (SELECT user_id FROM users)"))
            print("Cleaned orphan user settings")
        except Exception as e:
            print(f"Error cleaning user_settings: {e}")
            await s.rollback()

        await s.commit()
        print("\n=== VERIFYING QA DATABASE COUNTS ===")
        all_business_tables = [
            "vendors", "procurement_requests", "purchase_orders", "purchase_order_items",
            "contracts", "messages", "invoices", "delivery_tracking", "vendor_ratings",
            "vendor_issues", "vendor_performance_metrics", "reports"
        ]
        all_zero = True
        for t in all_business_tables:
            r = await s.execute(text(f"SELECT COUNT(*) FROM {t}"))
            cnt = r.scalar()
            print(f"  {t}: {cnt}")
            if cnt != 0:
                all_zero = False

        print("\n=== REFERENCE DATA ===")
        r_roles = await s.execute(text("SELECT COUNT(*) FROM roles"))
        r_cats = await s.execute(text("SELECT COUNT(*) FROM vendor_categories"))
        r_users = await s.execute(text("SELECT username, email, role_id FROM users"))
        print(f"  roles: {r_roles.scalar()}")
        print(f"  vendor_categories: {r_cats.scalar()}")
        print(f"  users: {r_users.fetchall()}")

        if all_zero:
            print("\nSUCCESS: All business tables are clean with 0 records!")
        else:
            print("\nWARNING: Some business tables still have records!")

if __name__ == "__main__":
    asyncio.run(clean_qa_database())
