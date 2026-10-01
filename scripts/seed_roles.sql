-- =====================================================================
-- SEED DATA: Roles Table
-- Vendor Reliability Intelligence Platform
-- =====================================================================
-- Run this BEFORE creating any users.
-- Uses ON CONFLICT to be safely idempotent (re-runnable).
-- =====================================================================

INSERT INTO roles (role_name, description)
VALUES
    ('ADMIN', 'Administrator'),
    ('PROCUREMENT_MANAGER', 'Procurement Manager'),
    ('VENDOR', 'Vendor'),
    ('AUDITOR', 'Auditor')
ON CONFLICT (role_name) DO NOTHING;
