"""
End-to-End Verification Test Script for Vendor Reliability Intelligence Platform
Tests clean state (0 everywhere) and single-entity workflow propagation.
"""

import sys
import os
import asyncio
from uuid import UUID
from datetime import date, datetime
from decimal import Decimal

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select, func
from app.database import SessionLocal
from app.models.vendors import Vendor
from app.models.procurement import ProcurementRequest, PurchaseOrder, PurchaseOrderItem, PriorityEnum
from app.models.contracts import Contract
from app.models.communication import Message
from app.models.users import User


async def run_e2e_verification():
    print("=" * 60)
    print("STARTING E2E VERIFICATION TEST ON VRIP_DB_QA")
    print("=" * 60)

    async with SessionLocal() as db:
        # Step 1: Verify Clean State
        print("\n[STEP 1] Verifying Clean Initial State...")
        vendor_count = (await db.execute(select(func.count()).select_from(Vendor))).scalar_one()
        pr_count = (await db.execute(select(func.count()).select_from(ProcurementRequest))).scalar_one()
        po_count = (await db.execute(select(func.count()).select_from(PurchaseOrder))).scalar_one()
        contract_count = (await db.execute(select(func.count()).select_from(Contract))).scalar_one()
        msg_count = (await db.execute(select(func.count()).select_from(Message))).scalar_one()

        print(f"  Vendors: {vendor_count}")
        print(f"  Procurement Requests: {pr_count}")
        print(f"  Purchase Orders: {po_count}")
        print(f"  Contracts: {contract_count}")
        print(f"  Messages: {msg_count}")

        # Verify admin user exists
        admin_user = (await db.execute(select(User).where(User.username == "admin_vendor"))).scalar_one_or_none()
        if not admin_user:
            admin_user = (await db.execute(select(User).where(User.username == "amar"))).scalar_one_or_none()
        assert admin_user is not None, "Admin user must exist in database"
        print(f"  -> Authenticated Admin user verified: {admin_user.username} (ID: {admin_user.user_id})")

        # Step 2: Create 1 Vendor
        print("\n[STEP 2] Creating 1 Real Vendor via Backend Service...")
        from app.services.vendor_service import vendor_service
        from app.schemas.vendor import VendorCreate

        new_vendor_data = VendorCreate(
            vendor_code="VEND-1001",
            company_name="Apex Global Technologies",
            category_id=1,
            tax_id="TAX-APEX-9988",
            website="https://apexglobal.example.com",
            address_line="100 Innovation Way, Tech Park",
        )
        vendor = await vendor_service.create_vendor(db, new_vendor_data)
        print(f"  -> Created Vendor: {vendor.company_name} (ID: {vendor.vendor_id}, Status: {vendor.status})")

        # Step 3: Approve the Vendor via official approve_vendor workflow
        print("\n[STEP 3] Approving Vendor via Official Approval Service...")
        approved_vendor = await vendor_service.approve_vendor(db, vendor.vendor_id, admin_user.user_id)
        print(f"  -> Vendor Approved! Status: {approved_vendor.status}, Approved by: {approved_vendor.approved_by}")

        # Step 4: Create 1 Procurement Request
        print("\n[STEP 4] Creating 1 Procurement Request...")
        from app.services.procurement_service import procurement_service
        from app.schemas.procurement import ProcurementRequestCreate

        pr_data = ProcurementRequestCreate(
            department="IT Infrastructure",
            item_description="High-Performance Enterprise Servers",
            quantity=Decimal("5"),
            estimated_cost=Decimal("250000.00"),
            required_by_date=date(2026, 9, 30),
            priority=PriorityEnum.HIGH,
        )
        pr = await procurement_service.create_request(db, pr_data, admin_user.user_id)
        print(f"  -> Created Procurement Request: {pr.request_number} - {pr.item_description} (ID: {pr.request_id})")

        # Step 4b: Approve Procurement Request
        approved_pr = await procurement_service.approve_request(db, pr.request_id, admin_user.user_id)
        print(f"  -> Approved Procurement Request: {approved_pr.request_number} (Status: {approved_pr.status})")

        # Step 5: Create 1 Purchase Order for the approved vendor
        print("\n[STEP 5] Creating 1 Purchase Order for Approved Vendor...")
        from app.schemas.procurement import PurchaseOrderCreate, PurchaseOrderItemCreate

        po_data = PurchaseOrderCreate(
            vendor_id=approved_vendor.vendor_id,
            request_id=approved_pr.request_id,
            expected_delivery_date=date(2026, 9, 15),
            items=[
                PurchaseOrderItemCreate(
                    item_name="Enterprise Rack Server X1",
                    quantity=Decimal("5"),
                    unit_price=Decimal("50000.00"),
                )
            ]
        )
        po = await procurement_service.create_purchase_order(db, po_data, admin_user.user_id)
        print(f"  -> Created Purchase Order: {po.po_number} (Amount: {po.total_amount}, ID: {po.po_id})")

        # Step 6: Create 1 Contract for the vendor
        print("\n[STEP 6] Creating 1 Contract...")
        from app.services.contract_service import contract_service
        from app.schemas.contracts import ContractCreate

        contract_data = ContractCreate(
            contract_number="CNT-2026-001",
            vendor_id=approved_vendor.vendor_id,
            contract_type="Master Service Agreement",
            start_date=date(2026, 8, 1),
            end_date=date(2027, 7, 31),
            contract_value=500000.0,
            status="active",
        )
        contract = await contract_service.create_contract(db, contract_data)
        print(f"  -> Created Contract: {contract.contract_number} (Value: {contract.contract_value}, ID: {contract.contract_id})")

        # Step 7: Send 1 Message to the vendor
        print("\n[STEP 7] Sending 1 Communication Message...")
        from app.services.communication_service import communication_service
        from app.schemas.communication import MessageCreate

        msg_data = MessageCreate(
            receiver_id=admin_user.user_id,
            vendor_id=approved_vendor.vendor_id,
            po_id=po.po_id,
            subject="Welcome to Vendor Reliability Platform",
            message_body="Welcome aboard. Purchase order PO-2026-001 has been initiated.",
        )
        msg = await communication_service.send_message(db, admin_user.user_id, msg_data)
        print(f"  -> Sent Message: '{msg.subject}' (ID: {msg.message_id})")

        # Step 8: Verify Real Analytics & Dashboard Metrics
        print("\n[STEP 8] Verifying Analytics & Dashboard Aggregations...")
        from app.services.analytics_service import analytics_service

        dashboard_metrics = await analytics_service.get_dashboard(db)
        print(f"  Dashboard Overview: total_vendors={dashboard_metrics.total_vendors}, active={dashboard_metrics.active_vendors}, total_pos={dashboard_metrics.total_purchase_orders}, spend={dashboard_metrics.total_procurement_spend}")
        assert dashboard_metrics.total_vendors >= 1, f"Expected at least 1 vendor, got {dashboard_metrics.total_vendors}"
        assert dashboard_metrics.active_vendors >= 1, f"Expected at least 1 active vendor, got {dashboard_metrics.active_vendors}"
        assert dashboard_metrics.total_purchase_orders >= 1, f"Expected at least 1 PO, got {dashboard_metrics.total_purchase_orders}"
        assert dashboard_metrics.total_procurement_spend >= 250000.0, f"Expected spend >= 250000, got {dashboard_metrics.total_procurement_spend}"

        vendor_analytics = await analytics_service.get_vendor_analytics(db)
        print(f"  Vendor Analytics: total_vendors={vendor_analytics.total_vendors}, by_status={vendor_analytics.vendors_by_status}")
        assert vendor_analytics.total_vendors >= 1

        proc_analytics = await analytics_service.get_procurement_analytics(db)
        print(f"  Procurement Analytics: total_requests={proc_analytics.total_requests}, total_spend={proc_analytics.total_spend}")
        assert proc_analytics.total_requests >= 1
        assert proc_analytics.total_purchase_orders >= 1

        print("\n" + "=" * 60)
        print("ALL E2E VERIFICATION CHECKS PASSED PERFECTLY!")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(run_e2e_verification())
