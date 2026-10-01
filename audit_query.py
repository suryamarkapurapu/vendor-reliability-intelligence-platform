"""Audit query script - READ ONLY - DO NOT MODIFY DATABASE"""
import asyncio
from sqlalchemy import text
from app.database import SessionLocal

async def main():
    async with SessionLocal() as s:
        # Check active users and their password hashes
        r = await s.execute(text("SELECT username, email, password_hash, role_id, is_active FROM users WHERE is_active = true"))
        print("=== ACTIVE USERS ===")
        for row in r.fetchall():
            print(f"  {row[0]} | {row[1]} | hash={row[2][:40]}... | role_id={row[3]} | active={row[4]}")

        # Check roles
        r2 = await s.execute(text("SELECT role_id, role_name FROM roles ORDER BY role_id"))
        print("\n=== ROLES ===")
        for row in r2.fetchall():
            print(f"  {row[0]}: {row[1]}")

        # Check settings
        r3 = await s.execute(text("SELECT setting_id, user_id, company_name, theme, timezone, email_notifications, sms_notifications FROM user_settings LIMIT 5"))
        print("\n=== USER SETTINGS ===")
        rows = r3.fetchall()
        if not rows:
            print("  No settings records found")
        for row in rows:
            print(f"  sid={str(row[0])[:8]} | uid={str(row[1])[:8]} | company={row[2]} | theme={row[3]} | tz={row[4]} | email_notif={row[5]} | sms_notif={row[6]}")

        # Count all key tables
        tables = ['vendors', 'procurement_requests', 'purchase_orders', 'contracts', 'messages', 'invoices', 'deliveries', 'vendor_ratings', 'vendor_issues', 'vendor_performance_metrics', 'vendor_categories']
        print("\n=== TABLE COUNTS ===")
        for t in tables:
            try:
                r = await s.execute(text(f"SELECT COUNT(*) FROM {t}"))
                print(f"  {t}: {r.scalar()}")
            except Exception as e:
                print(f"  {t}: ERROR - {e}")
                await s.rollback()

        # All tables
        r14 = await s.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name"))
        print("\n=== ALL TABLES ===")
        for row in r14.fetchall():
            print(f"  {row[0]}")

        # Sample vendor data
        try:
            rv = await s.execute(text("SELECT vendor_id, company_name, vendor_code, status FROM vendors LIMIT 5"))
            print("\n=== SAMPLE VENDORS ===")
            for row in rv.fetchall():
                print(f"  {str(row[0])[:8]}... | {row[1]} | {row[2]} | {row[3]}")
        except Exception as e:
            print(f"\n=== SAMPLE VENDORS: ERROR - {e} ===")
            await s.rollback()

        # Sample PO data
        try:
            rp = await s.execute(text("SELECT po_id, po_number, vendor_id, status, total_amount FROM purchase_orders LIMIT 5"))
            print("\n=== SAMPLE PURCHASE ORDERS ===")
            for row in rp.fetchall():
                print(f"  {str(row[0])[:8]}... | {row[1]} | vendor={str(row[2])[:8]}... | {row[3]} | amt={row[4]}")
        except Exception as e:
            print(f"\n=== SAMPLE POs: ERROR - {e} ===")
            await s.rollback()

asyncio.run(main())
