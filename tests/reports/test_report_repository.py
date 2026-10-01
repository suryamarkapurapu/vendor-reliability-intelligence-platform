"""
Unit tests for Reports Repository — Phase 2B Refactor.
Tests import validation, class structure, method signatures, type hints,
singleton pattern, package-level exports, read-only enforcement,
and confirms all business logic has been removed from the repository.

NOTE: These are structural and contract tests that do NOT require a live database
connection. Full integration tests against a PostgreSQL instance are deferred to CI.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


import inspect
import sys

PASS = 0
FAIL = 0


def check(name, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  [PASS] {name}")
    else:
        FAIL += 1
        print(f"  [FAIL] {name} -- {detail}")


# =============================================================
# TEST 1: Module Imports
# =============================================================
print("\n=== TEST 1: Module Imports ===")

try:
    from app.repositories.report_repository import ReportRepository, report_repository
    check("Direct import ReportRepository", True)
    check("Direct import report_repository singleton", True)
except ImportError as e:
    check("Direct import ReportRepository", False, str(e))
    check("Direct import report_repository singleton", False, str(e))

try:
    from app.repositories import ReportRepository as PkgReportRepo
    from app.repositories import report_repository as pkg_report_repo
    check("Package import ReportRepository", PkgReportRepo is ReportRepository)
    check("Package import report_repository", pkg_report_repo is report_repository)
except ImportError as e:
    check("Package import ReportRepository", False, str(e))
    check("Package import report_repository", False, str(e))


# =============================================================
# TEST 2: Singleton Pattern
# =============================================================
print("\n=== TEST 2: Singleton Pattern ===")

check("report_repository is instance of ReportRepository",
      isinstance(report_repository, ReportRepository))

# Verify all other repositories still import correctly
try:
    from app.repositories import (
        AnalyticsRepository,
        analytics_repository,
        DeliveryRepository,
        delivery_repository,
        InvoiceRepository,
        invoice_repository,
        ProcurementRepository,
        procurement_repository,
        UserRepository,
        user_repository,
        VendorPerformanceRepository,
        vendor_performance_repository,
        VendorRepository,
        vendor_repository,
    )
    check("Existing repository imports preserved", True)
except ImportError as e:
    check("Existing repository imports preserved", False, str(e))


# =============================================================
# TEST 3: Repository Method Existence
# =============================================================
print("\n=== TEST 3: Repository Method Existence ===")

expected_methods = [
    "get_vendor_performance_report_data",
    "get_procurement_report_data",
    "get_purchase_order_report_data",
    "get_compliance_report_data",
    "get_contract_report_data",
    "get_report_summary_data",
    "get_report_history",
]

for method_name in expected_methods:
    has_method = hasattr(report_repository, method_name) and callable(
        getattr(report_repository, method_name)
    )
    check(f"Method exists: {method_name}", has_method)


# =============================================================
# TEST 4: Async Method Verification
# =============================================================
print("\n=== TEST 4: Async Method Verification ===")

for method_name in expected_methods:
    method = getattr(report_repository, method_name, None)
    if method:
        is_async = inspect.iscoroutinefunction(method)
        check(f"{method_name} is async", is_async)
    else:
        check(f"{method_name} is async", False, "method not found")


# =============================================================
# TEST 5: Method Signature Verification
# =============================================================
print("\n=== TEST 5: Method Signature Verification ===")

# All methods should accept 'db' as first positional arg (after self)
for method_name in expected_methods:
    method = getattr(report_repository, method_name, None)
    if method:
        sig = inspect.signature(method)
        params = list(sig.parameters.keys())
        has_db = "db" in params
        check(f"{method_name} has 'db' parameter", has_db, f"params={params}")
    else:
        check(f"{method_name} has 'db' parameter", False, "method not found")

# Methods with search/filter params
search_methods = {
    "get_vendor_performance_report_data": ["search"],
    "get_procurement_report_data": ["search"],
    "get_purchase_order_report_data": ["search", "status"],
    "get_compliance_report_data": ["search"],
    "get_contract_report_data": ["search", "status"],
    "get_report_history": ["search", "category", "status", "page", "page_size"],
}

for method_name, expected_params in search_methods.items():
    method = getattr(report_repository, method_name, None)
    if method:
        sig = inspect.signature(method)
        actual_params = list(sig.parameters.keys())
        for param in expected_params:
            check(
                f"{method_name} has '{param}' param",
                param in actual_params,
                f"actual={actual_params}",
            )
    else:
        for param in expected_params:
            check(f"{method_name} has '{param}' param", False, "method not found")


# =============================================================
# TEST 6: Return Type Annotations
# =============================================================
print("\n=== TEST 6: Return Type Annotations ===")

for method_name in expected_methods:
    method = getattr(report_repository, method_name, None)
    if method:
        sig = inspect.signature(method)
        has_return = sig.return_annotation != inspect.Parameter.empty
        check(f"{method_name} has return annotation", has_return)
    else:
        check(f"{method_name} has return annotation", False, "method not found")


# =============================================================
# TEST 7: Docstrings
# =============================================================
print("\n=== TEST 7: Docstrings ===")

for method_name in expected_methods:
    method = getattr(report_repository, method_name, None)
    if method:
        has_docstring = method.__doc__ is not None and len(method.__doc__.strip()) > 10
        check(f"{method_name} has docstring", has_docstring)
    else:
        check(f"{method_name} has docstring", False, "method not found")

# Class-level docstring
check("ReportRepository class docstring",
      ReportRepository.__doc__ is not None and len(ReportRepository.__doc__.strip()) > 10)


# =============================================================
# TEST 8: No Write Methods (Read-Only Verification)
# =============================================================
print("\n=== TEST 8: No Write Methods (Read-Only Verification) ===")

write_patterns = ["create", "update", "delete", "insert", "upsert", "save", "remove"]
public_methods = [m for m in dir(report_repository) if not m.startswith("_")]

for pattern in write_patterns:
    violating = [m for m in public_methods if pattern in m.lower()]
    check(
        f"No '{pattern}' methods found",
        len(violating) == 0,
        f"found: {violating}" if violating else "",
    )


# =============================================================
# TEST 9: Architecture Verification — No ORM, No Writes
# =============================================================
print("\n=== TEST 9: Architecture Verification ===")

import importlib
repo_module = importlib.import_module("app.repositories.report_repository")
source_file = inspect.getfile(repo_module)

with open(source_file, "r", encoding="utf-8") as f:
    source = f.read()

# Should not define a Base/ORM model class
check("No Base import for model definition",
      "class Base" not in source and "DeclarativeBase" not in source)

# Should not have db.add, db.commit, db.rollback
check("No db.add (read-only)", "db.add(" not in source)
check("No db.commit (read-only)", "db.commit()" not in source)
check("No db.rollback (read-only)", "db.rollback()" not in source)

# Should use existing models
check("Uses Vendor model", "Vendor" in source)
check("Uses PurchaseOrder model", "PurchaseOrder" in source)
check("Uses ProcurementRequest model", "ProcurementRequest" in source)
check("Uses DeliveryTracking model", "DeliveryTracking" in source)
check("Uses VendorIssue model", "VendorIssue" in source)
check("Uses VendorRating model", "VendorRating" in source)
check("Uses Invoice model", "Invoice" in source)


# =============================================================
# TEST 10: Business Logic Removed — No Scoring or Classification
# =============================================================
print("\n=== TEST 10: Business Logic Removed ===")

# --- Composite scoring / weighting must NOT exist ---
check("No composite score weighting (* 0.4)",
      "* 0.4" not in source and "*0.4" not in source)
check("No composite score weighting (* 0.3)",
      "* 0.3" not in source and "*0.3" not in source)
check("No composite score weighting (* 0.2)",
      "* 0.2" not in source and "*0.2" not in source)
check("No composite score weighting (* 0.1)",
      "* 0.1" not in source and "*0.1" not in source)

# --- Risk classification must NOT exist ---
check("No risk_level assignment", "risk_level" not in source)
check("No 'HIGH' risk string literal",
      '"HIGH"' not in source and "'HIGH'" not in source)
check("No 'MEDIUM' risk string literal",
      '"MEDIUM"' not in source and "'MEDIUM'" not in source)
# 'LOW' could appear in other contexts, check for risk-related LOW
check("No 'LOW' risk classification",
      "risk_level" not in source)

# --- Derived rates / percentages must NOT be computed ---
check("No fulfillment_rate", "fulfillment_rate" not in source)
check("No renewal_rate", "renewal_rate" not in source)
check("No compliance_score", "compliance_score" not in source)
check("No delivery_score", "delivery_score" not in source)
check("No quality_score", "quality_score" not in source)
check("No overall_score", "overall_score" not in source)
check("No overall_compliance", "overall_compliance" not in source)

# --- No percentage formula (count / total * 100) ---
check("No '* 100.0' percentage calculation", "* 100.0" not in source)
check("No '* 100' percentage calculation", "* 100)" not in source)

# --- No / 5.0 rating normalization ---
check("No '/ 5.0' rating normalization", "/ 5.0" not in source)

# --- No 86400 seconds-to-days conversion ---
check("No 86400 unit conversion in repo", "86400" not in source)


# =============================================================
# TEST 11: Business Logic Removed — No Contract Fabrication
# =============================================================
print("\n=== TEST 11: No Contract Fabrication ===")

# Should not map PO status to contract lifecycle
check("No 'ACTIVE' contract status mapping",
      source.count('"ACTIVE"') == 0 and source.count("'ACTIVE'") == 0)
check("No 'EXPIRING' contract status mapping",
      '"EXPIRING"' not in source and "'EXPIRING'" not in source)
check("No 'COMPLETED' contract status mapping",
      '"COMPLETED"' not in source and "'COMPLETED'" not in source)

# Should not generate contract-like fields from PO data
check("No 'contract_id' field fabrication", "'contract_id'" not in source and '"contract_id"' not in source)
check("No 'contract_number' field fabrication", "'contract_number'" not in source and '"contract_number"' not in source)
check("No 'contract_type' field fabrication", "'contract_type'" not in source and '"contract_type"' not in source)
check("No 'days_until_expiration' field fabrication",
      "'days_until_expiration'" not in source and '"days_until_expiration"' not in source)
check("No title generation ('PO ' prefix)", '"PO "' not in source and "f\"PO " not in source)


# =============================================================
# TEST 12: Business Logic Removed — No Audit Assumption
# =============================================================
print("\n=== TEST 12: No Audit Assumption ===")

# VendorRating should NOT be treated as audit/compliance check
check("No 'total_audits' key in source", "'total_audits" not in source and '"total_audits' not in source)
check("No 'audits_checked' in source", "audits_checked" not in source)
check("No 'compliance_type' assignment from issue_type",
      '"compliance_type"' not in source and "'compliance_type'" not in source)
check("No severity assignment based on status",
      '"severity":' not in source and "'severity':" not in source)


# =============================================================
# TEST 13: No UI Catalogue / Hardcoded Metadata
# =============================================================
print("\n=== TEST 13: No UI Catalogue ===")

check("No 'report_catalogue' in source", "report_catalogue" not in source)
check("No hardcoded report descriptions", "Comprehensive vendor scoring" not in source)
check("No hardcoded report names", "Vendor Performance Report" not in source)
check("No ReportCategory schema import",
      "from app.schemas.reports import" not in source)
check("No 'violation_status' mapping", "violation_status" not in source)
check("No 'compliant_vendors_count' key",
      "'compliant_vendors_count'" not in source and '"compliant_vendors_count"' not in source)
check("No 'reports_by_category' hardcoded mapping",
      '"reports_by_category"' not in source and "'reports_by_category'" not in source)
check("No 'reports_by_status' hardcoded mapping",
      '"reports_by_status"' not in source and "'reports_by_status'" not in source)


# =============================================================
# TEST 14: Backward Compatibility of Other Repositories
# =============================================================
print("\n=== TEST 14: Backward Compatibility of Other Repositories ===")

check("AnalyticsRepository is class", inspect.isclass(AnalyticsRepository))
check("VendorPerformanceRepository is class", inspect.isclass(VendorPerformanceRepository))
check("ProcurementRepository is class", inspect.isclass(ProcurementRepository))
check("InvoiceRepository is class", inspect.isclass(InvoiceRepository))
check("DeliveryRepository is class", inspect.isclass(DeliveryRepository))
check("VendorRepository is class", inspect.isclass(VendorRepository))
check("UserRepository is class", inspect.isclass(UserRepository))

# Verify singletons still work
check("analytics_repository singleton", isinstance(analytics_repository, AnalyticsRepository))
check("vendor_performance_repository singleton",
      isinstance(vendor_performance_repository, VendorPerformanceRepository))
check("procurement_repository singleton", isinstance(procurement_repository, ProcurementRepository))


# =============================================================
# SUMMARY
# =============================================================
print(f"\n{'=' * 50}")
print(f"  RESULTS: {PASS} passed, {FAIL} failed, {PASS + FAIL} total")
print(f"{'=' * 50}\n")

sys.exit(0 if FAIL == 0 else 1)
