# Risk Register - Workshop Tool Inventory System

## Overview

This document identifies known limitations, edge cases, and potential risks in the Workshop Tool Inventory System. It serves as a reference for operators and developers to understand system constraints and plan mitigation strategies.

---

## Critical Risks

### R-001: Data Inconsistency from Concurrent Operations

**Risk Level:** HIGH

**Description:**
Multiple users performing operations on the same item simultaneously could lead to race conditions.

**Scenario:**
- User A checks out an item
- User B simultaneously tries to check out the same item
- Both operations might succeed if not properly synchronized

**Current Mitigation:**
- Django ORM uses database-level transactions
- Item status checked before each operation
- `@transaction.atomic` decorator on critical operations

**Remaining Risk:**
- Very tight race conditions (milliseconds) might still occur
- No explicit row-level locking implemented

**Recommended Actions:**
1. Add `select_for_update()` on critical item queries
2. Implement optimistic locking with version fields
3. Add retry logic for concurrent modification errors

**Workaround:**
- Train users to refresh admin page before operations
- Implement periodic reconciliation checks

---

### R-002: Lost Barcode Images on Media Storage Failure

**Risk Level:** HIGH

**Description:**
Barcode images stored in `media/barcodes/` could be lost if media storage fails or is not backed up.

**Impact:**
- Items lose their barcode images
- Labels cannot be regenerated without images
- Manual barcode recreation required

**Current Mitigation:**
- Barcode text stored in database (can regenerate image)
- Barcode generation is deterministic

**Remaining Risk:**
- Media files not automatically backed up
- No verification of media file integrity

**Recommended Actions:**
1. Implement automated media file backups
2. Add admin action to regenerate missing barcode images
3. Store barcodes in cloud storage (S3, etc.) with redundancy
4. Add periodic media file integrity checks

**Workaround:**
- Use "Generate Barcodes" admin action to recreate images
- Manual backup of media directory

---

### R-003: CSV Import Data Validation Bypass

**Risk Level:** MEDIUM

**Description:**
While CSV import validates data, malformed CSV files could cause unexpected behavior.

**Scenarios:**
- Very large CSV files (>10MB) could cause memory issues
- Special characters in serial numbers might cause encoding issues
- Malicious CSV content (though no code execution possible)

**Current Mitigation:**
- All rows validated before import
- Transaction rollback on any error
- File size limits enforced

**Remaining Risk:**
- No explicit CSV injection protection
- Large files could slow down server
- Unicode handling not extensively tested

**Recommended Actions:**
1. Add explicit CSV injection checks (formulas starting with =, +, -, @)
2. Implement streaming CSV parsing for large files
3. Add progress indicator for large imports
4. Test with various character encodings

**Workaround:**
- Limit CSV imports to trusted users only
- Review CSV files before import
- Import in smaller batches

---

## Medium Risks

### R-004: Stock Calculation Performance Degradation

**Risk Level:** MEDIUM

**Description:**
Stock calculations are performed dynamically by counting items. With very large datasets (100k+ items per product), this could become slow.

**Impact:**
- Dashboard loads slowly
- Admin list pages slow
- Low stock alerts delayed

**Current Mitigation:**
- Database indexes on status field
- Queries optimized with select_related/prefetch_related
- Tested with 100k items

**Remaining Risk:**
- No caching implemented
- No materialized views for stock counts
- Multiple products with 100k+ items each not tested

**Recommended Actions:**
1. Implement Redis caching for stock counts
2. Add cache invalidation on item status changes
3. Consider materialized views for very large datasets
4. Add database partitioning for ItemInstance table

**Workaround:**
- Limit products to reasonable item counts
- Archive old/inactive items
- Run stock reports during off-peak hours

---

### R-005: Audit Log Growth

**Risk Level:** MEDIUM

**Description:**
django-simple-history creates a history record for every change. With high transaction volume, history tables could grow very large.

**Impact:**
- Database size increases rapidly
- Queries on history tables become slow
- Backup/restore times increase

**Current Mitigation:**
- History tables indexed
- Only critical models have history enabled

**Remaining Risk:**
- No automatic history archival
- No history retention policy
- Old history never deleted

**Recommended Actions:**
1. Implement history retention policy (e.g., keep 2 years)
2. Archive old history to separate database
3. Add periodic cleanup job for old history
4. Consider partitioning history tables by date

**Workaround:**
- Manual cleanup of old history records
- Database maintenance during off-peak hours

---

### R-006: Overdue Return Detection Accuracy

**Risk Level:** MEDIUM

**Description:**
Overdue returns are calculated based on `expected_return_date`. If system clock is wrong or timezone issues occur, calculations could be inaccurate.

**Impact:**
- Items marked overdue when they're not
- Actual overdue items not detected
- Incorrect dashboard statistics

**Current Mitigation:**
- Using Django's timezone-aware datetime
- All dates stored in UTC

**Remaining Risk:**
- Server timezone misconfiguration
- Daylight saving time edge cases
- No validation of expected_return_date reasonableness

**Recommended Actions:**
1. Add validation for expected_return_date (max 90 days)
2. Add server time monitoring
3. Add timezone configuration checks in deployment
4. Display timezone in admin interface

**Workaround:**
- Manual review of overdue items
- Adjust expected_return_date if needed

---

## Low Risks

### R-007: Serial Number Collision

**Risk Level:** LOW

**Description:**
While serial numbers have unique constraint, manual entry could lead to confusion if similar serial numbers are used.

**Scenarios:**
- "SN-001" vs "SN-0001" vs "SN-00001"
- Case sensitivity issues
- Leading/trailing whitespace

**Current Mitigation:**
- Database unique constraint
- Whitespace stripped on validation
- Clear error messages on duplicate

**Remaining Risk:**
- No normalization of serial numbers
- Case-sensitive comparison (PostgreSQL default)

**Recommended Actions:**
1. Implement serial number normalization (uppercase, trim)
2. Add serial number format validation
3. Suggest serial numbers during creation

**Workaround:**
- Establish serial number format policy
- Train users on consistent format

---

### R-008: PDF Label Generation Memory Usage

**Risk Level:** LOW

**Description:**
Generating PDF labels for many items (1000+) could consume significant memory.

**Impact:**
- Server memory spike
- Slow PDF generation
- Potential timeout

**Current Mitigation:**
- PDF generated in-memory
- Reasonable page limits (21 labels per page)

**Remaining Risk:**
- No limit on number of items selected
- No streaming PDF generation
- Large barcodes increase memory usage

**Recommended Actions:**
1. Add limit on PDF generation (max 500 items)
2. Implement streaming PDF generation
3. Add progress indicator for large batches

**Workaround:**
- Generate labels in smaller batches
- Use pagination in admin

---

### R-009: Maintenance Cost Tracking Accuracy

**Risk Level:** LOW

**Description:**
Maintenance costs are manually entered. No validation ensures accuracy or prevents typos.

**Impact:**
- Incorrect cost statistics
- Budget tracking inaccurate
- Financial reporting errors

**Current Mitigation:**
- Decimal field with precision
- Optional field (can be left blank)

**Remaining Risk:**
- No validation of reasonable cost ranges
- No currency conversion
- No cost approval workflow

**Recommended Actions:**
1. Add cost range validation (e.g., 0-10000)
2. Add cost approval workflow for high amounts
3. Add currency field if multi-currency needed

**Workaround:**
- Manual review of maintenance costs
- Periodic cost audits

---

### R-010: Location Hierarchy Depth Limit

**Risk Level:** LOW

**Description:**
Location model supports hierarchical structure (parent-child), but no depth limit enforced.

**Impact:**
- Very deep hierarchies could cause performance issues
- Recursive queries could be slow
- UI display issues with deep nesting

**Current Mitigation:**
- Simple parent foreign key
- Most queries don't traverse hierarchy

**Remaining Risk:**
- No maximum depth validation
- No circular reference prevention
- Recursive queries not optimized

**Recommended Actions:**
1. Add maximum depth validation (e.g., 5 levels)
2. Add circular reference check
3. Use django-mptt for efficient hierarchy queries

**Workaround:**
- Keep location hierarchy shallow (2-3 levels max)
- Avoid circular references manually

---

## Edge Cases and Known Limitations

### L-001: Consumable Item Tracking

**Limitation:**
Consumable items are deleted from database when consumed. No history of individual consumable items exists after consumption.

**Impact:**
- Cannot track which specific consumable item was used
- Only transaction record remains

**Rationale:**
- Consumables are not individually tracked after use
- Reduces database size

**Workaround:**
- Transaction records provide consumption history
- Use batch/lot numbers in serial_number field if needed

---

### L-002: Bulk Operation Limit

**Limitation:**
Bulk operations limited to 100 items at a time.

**Impact:**
- Large operations must be split into batches
- Time-consuming for very large operations

**Rationale:**
- Prevents server overload
- Ensures reasonable response times
- Reduces risk of timeout

**Workaround:**
- Use CSV import for very large operations
- Split operations into multiple batches

---

### L-003: No Multi-Warehouse Support

**Limitation:**
System designed for single warehouse operation. No built-in support for multiple warehouses or inter-warehouse transfers.

**Impact:**
- Cannot track items across multiple physical locations
- No transfer workflow between warehouses

**Workaround:**
- Use Location hierarchy to represent different warehouses
- Manual coordination for transfers

**Future Enhancement:**
- Add Warehouse model
- Add transfer workflow
- Add inter-warehouse transaction type

---

### L-004: No Reservation System

**Limitation:**
No ability to reserve items for future checkout. Items are either available or checked out.

**Impact:**
- Cannot plan future tool allocation
- First-come-first-served only

**Workaround:**
- Manual coordination via notes
- Use expected_return_date to plan

**Future Enhancement:**
- Add reservation status
- Add reservation workflow
- Add reservation expiration

---

### L-005: No Barcode Scanner Integration

**Limitation:**
System does not integrate directly with barcode scanners. Barcodes must be manually entered or scanned into text fields.

**Impact:**
- Manual data entry required
- Potential for typos

**Workaround:**
- Use barcode scanner in keyboard emulation mode
- Scanner types directly into serial number field

**Future Enhancement:**
- Add dedicated barcode scanning interface
- Add mobile app for scanning

---

### L-006: No Email Notifications

**Limitation:**
System does not send email notifications for overdue returns, low stock, or maintenance completion.

**Impact:**
- Users must check dashboard manually
- Delayed response to issues

**Workaround:**
- Regular dashboard review
- Manual communication

**Future Enhancement:**
- Add email notification system
- Add configurable notification rules
- Add SMS notifications

---

### L-007: No Mobile App

**Limitation:**
System is web-based admin interface only. No dedicated mobile app.

**Impact:**
- Less convenient for field workers
- Requires laptop/desktop access

**Workaround:**
- Admin interface is responsive
- Works on tablets
- Basic functionality on mobile browsers

**Future Enhancement:**
- Develop mobile app
- Add offline capability
- Add barcode scanning in app

---

## Data Integrity Risks

### D-001: Manual Status Changes

**Risk:**
Admin users can manually change item status without creating transactions.

**Impact:**
- Status and transaction history could become inconsistent
- Audit trail incomplete

**Mitigation:**
- Train users to use proper workflows
- Restrict direct status changes to managers only
- Periodic reconciliation checks

---

### D-002: Deleted Users

**Risk:**
If a user is deleted, their transaction history remains but user reference is lost.

**Impact:**
- Cannot identify who performed historical transactions
- Audit trail incomplete

**Mitigation:**
- Use `on_delete=models.PROTECT` for user foreign keys
- Deactivate users instead of deleting
- Archive user data before deletion

---

### D-003: Product/Category Changes

**Risk:**
Changing product category or workshop unit affects historical context.

**Impact:**
- Historical reports might be confusing
- SKU codes don't change (still reflect old category)

**Mitigation:**
- django-simple-history tracks changes
- Avoid changing product categories
- Create new product if major change needed

---

## Operational Risks

### O-001: Insufficient Training

**Risk:**
Users not properly trained on system workflows could make errors.

**Impact:**
- Incorrect data entry
- Workflow violations
- Data inconsistency

**Mitigation:**
- Comprehensive user training
- Written procedures
- Regular refresher training

---

### O-002: Lack of Physical Inventory Reconciliation

**Risk:**
System data could drift from physical reality if not regularly reconciled.

**Impact:**
- System shows items as available when they're not
- Lost items not detected
- Stock counts inaccurate

**Mitigation:**
- Periodic physical inventory counts
- Reconciliation procedure
- Investigation of discrepancies

**Recommended Schedule:**
- Full inventory: Annually
- Spot checks: Monthly
- High-value items: Quarterly

---

### O-003: Backup Failure

**Risk:**
Automated backups could fail without detection.

**Impact:**
- Data loss in case of system failure
- No recovery point

**Mitigation:**
- Monitor backup success
- Test restore procedure monthly
- Multiple backup locations
- Alert on backup failure

---

## Mitigation Priority Matrix

| Risk ID | Risk Level | Likelihood | Impact | Priority | Status |
|---------|------------|------------|--------|----------|--------|
| R-001   | HIGH       | Medium     | High   | P1       | Open   |
| R-002   | HIGH       | Low        | High   | P2       | Open   |
| R-003   | MEDIUM     | Low        | Medium | P3       | Open   |
| R-004   | MEDIUM     | Medium     | Medium | P2       | Open   |
| R-005   | MEDIUM     | High       | Low    | P3       | Open   |
| R-006   | MEDIUM     | Low        | Medium | P3       | Open   |
| R-007   | LOW        | Low        | Low    | P4       | Open   |
| R-008   | LOW        | Low        | Low    | P4       | Open   |
| R-009   | LOW        | Medium     | Low    | P4       | Open   |
| R-010   | LOW        | Low        | Low    | P4       | Open   |

**Priority Levels:**
- P1: Address before production deployment
- P2: Address within first month of operation
- P3: Address within first quarter
- P4: Address as resources permit

---

## Risk Review Schedule

- **Weekly:** Review critical risks (HIGH level)
- **Monthly:** Review all risks, update status
- **Quarterly:** Comprehensive risk assessment, add new risks
- **Annually:** Full risk register review and update

---

## Document Control

**Version:** 1.0  
**Last Updated:** 2025-05-01  
**Next Review:** 2025-06-01  
**Owner:** System Administrator  
**Approver:** Workshop Manager
