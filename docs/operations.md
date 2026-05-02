# Operations Guide - Workshop Tool Inventory System

## Daily Operations

### Morning Checklist

1. **Check Dashboard**
   - Review overdue returns
   - Check low stock alerts
   - Review recent transactions

2. **Process Returns**
   - Filter items by "تحویل داده شده" (Checked Out)
   - Select overdue items
   - Contact users for return
   - Process returns as items come in

3. **Review Maintenance**
   - Check items in maintenance
   - Update maintenance status
   - Return fixed items to service

### Checkout Process

**Standard Checkout:**
1. Go to ItemInstance admin
2. Search for item by barcode or serial number
3. Verify item status is "موجود" (Available)
4. Select item(s)
5. Choose "تحویل ابزار به کاربر" action
6. Select user
7. Set expected return date (typically 7 days)
8. Add notes if needed
9. Submit

**Bulk Checkout:**
1. Filter items by status "موجود"
2. Select multiple items (max 100)
3. Choose "تحویل ابزار به کاربر" action
4. Select user
5. Set expected return date
6. Submit

### Return Process

**Standard Return:**
1. Go to ItemInstance admin
2. Filter by "تحویل داده شده" (Checked Out)
3. Search for item or user
4. Select item(s)
5. Choose "بازگشت ابزار" action
6. Add notes about condition
7. Submit

**Damaged Return:**
1. Select checked-out item
2. Choose "علامت‌گذاری به عنوان خراب" action
3. Add description of damage
4. Submit
5. Item status changes to "خراب" (Damaged)
6. Create maintenance log if repairable

### Maintenance Workflow

**Report Maintenance:**
1. Select item(s)
2. Choose "گزارش تعمیر" action
3. Enter description of issue
4. Submit
5. Item status changes to "در تعمیر" (Maintenance)

**Process Maintenance:**
1. Go to MaintenanceLog admin
2. Find reported item
3. Update status to "در حال تعمیر" (In Repair)
4. When fixed:
   - Update status to "تعمیر شده" (Fixed)
   - Enter repair cost
   - Set date_fixed
5. Return item to service:
   - Go to ItemInstance admin
   - Change status to "موجود" (Available)

**Discard Item:**
1. If item is beyond repair
2. Update maintenance status to "اسقاط" (Discarded)
3. Item remains in system for audit trail

---

## Weekly Operations

### Stock Review

**Check Low Stock:**
1. Review dashboard "Low Stock Products" widget
2. For each low stock product:
   - Check if more items are on order
   - Check if items are in maintenance
   - Consider purchasing more
3. Document decisions

**Reconciliation:**
1. Select a category for spot check
2. Physically count items
3. Compare with system count
4. Investigate discrepancies
5. Update system if needed

### User Management

**Add New User:**
1. Go to Users admin
2. Click "Add User"
3. Enter username and password
4. Set email and full name
5. Assign to appropriate group:
   - Warehouse Manager
   - Warehouse Staff
   - Workshop Worker
   - Auditor
6. Save

**Deactivate User:**
1. Go to Users admin
2. Find user
3. Uncheck "Active" status
4. Do NOT delete (preserves audit trail)
5. Save

### Report Generation

**Transaction Report:**
1. Go to Transaction admin
2. Apply filters:
   - Date range
   - Transaction type
   - User
3. Export to CSV if needed

**Maintenance Report:**
1. Go to MaintenanceLog admin
2. Filter by date range
3. Review costs and repair times
4. Export to CSV if needed

---

## Monthly Operations

### Inventory Audit

**Full Category Audit:**
1. Select a category (rotate monthly)
2. Generate list of all items in category
3. Physically locate each item
4. Verify:
   - Item exists
   - Status is correct
   - Location is correct
   - Condition matches status
5. Document findings
6. Update system as needed

**Reconciliation Report:**
```
Category: Wrenches
Audit Date: 2025-05-01
Auditor: John Doe

System Count: 150
Physical Count: 148
Discrepancies: 2

Missing Items:
- WRN-045 (Last seen: 2025-04-15, User: Jane Smith)
- WRN-089 (Last seen: 2025-04-20, User: Bob Jones)

Actions Taken:
- Contacted users
- Marked items as lost
- Ordered replacements
```

### Maintenance Review

**Analyze Maintenance Costs:**
1. Go to MaintenanceLog admin
2. Filter by last month
3. Review:
   - Total repair costs
   - Average repair time
   - Most frequently repaired items
   - Items with high repair costs
4. Consider:
   - Replacing frequently repaired items
   - Training on proper tool use
   - Better storage/handling procedures

### User Activity Review

**Review User Transactions:**
1. Go to Transaction admin
2. Group by user
3. Identify:
   - Users with overdue returns
   - Users with frequent damage reports
   - Inactive users
4. Take action:
   - Contact users with issues
   - Provide training if needed
   - Deactivate inactive users

---

## Bulk Operations

### CSV Import

**Prepare CSV File:**
```csv
product_sku,serial_number,location
COL-WRN-001,NEW-001,Main Warehouse
COL-WRN-001,NEW-002,Main Warehouse
COL-WRN-001,NEW-003,Shelf A
```

**Import Process:**
1. Verify CSV format is correct
2. Check that all product SKUs exist
3. Check that all locations exist
4. Ensure serial numbers are unique
5. Go to ItemInstance admin
6. Choose "وارد کردن از فایل CSV" action
7. Upload file
8. Review results
9. If errors, fix CSV and retry

**Common Import Errors:**
- Product SKU not found → Create product first
- Serial number already exists → Use unique serials
- Location not found → Create location first
- Invalid CSV format → Check header row

### Bulk Location Change

**Move Items to New Location:**
1. Go to ItemInstance admin
2. Filter by current location
3. Select items to move (max 100)
4. Choose "تغییر مکان" action
5. Select new location
6. Submit

**Note:** Cannot move checked-out items. Return them first.

### Generate Barcode Labels

**Print Labels for New Items:**
1. Go to ItemInstance admin
2. Filter by recent items (e.g., last week)
3. Select items needing labels
4. Choose "تولید برچسب بارکد (PDF)" action
5. PDF downloads automatically
6. Print on A4 label sheets (70×40mm labels)
7. Apply labels to physical items

**Label Sheet Specifications:**
- Paper: A4 (210×297mm)
- Grid: 3 columns × 7 rows
- Label size: 70×40mm
- Labels per sheet: 21

---

## Common Scenarios

### Scenario 1: Item Lost in Field

**Steps:**
1. User reports item lost
2. Go to ItemInstance admin
3. Find item (search by barcode or serial)
4. If checked out:
   - Select item
   - Choose "علامت‌گذاری به عنوان گم شده" action
   - Add notes about circumstances
   - Submit
5. Item status changes to "گم شده" (Lost)
6. Stock count automatically decreases
7. Consider ordering replacement

### Scenario 2: Bulk Checkout for Project

**Steps:**
1. Receive list of tools needed for project
2. Go to ItemInstance admin
3. Search for each tool type
4. Filter by "موجود" (Available)
5. Select required items
6. Choose "تحویل ابزار به کاربر" action
7. Select project lead as user
8. Set expected return date (project end date)
9. Add notes: "Project XYZ"
10. Submit
11. Print checkout list for user

### Scenario 3: Emergency Tool Needed

**Steps:**
1. Check if tool is available
2. If available:
   - Quick checkout to user
   - Set short return date (1-2 days)
3. If checked out:
   - Contact current holder
   - Negotiate early return
   - Checkout to emergency user
4. If in maintenance:
   - Check if repair is complete
   - If yes, return to service and checkout
   - If no, find alternative tool

### Scenario 4: Annual Inventory Count

**Steps:**
1. Schedule inventory count (typically end of year)
2. Prepare:
   - Print list of all items by location
   - Assign teams to locations
   - Prepare count sheets
3. Count:
   - Physically count all items
   - Mark items as found
   - Note discrepancies
4. Reconcile:
   - Compare physical count to system
   - Investigate missing items
   - Update system
5. Report:
   - Document findings
   - Report to management
   - Plan corrective actions

### Scenario 5: New Product Category

**Steps:**
1. Create Category:
   - Go to Category admin
   - Add new category (e.g., "Power Tools")
   - Set code (e.g., "PWR")
2. Create Products:
   - Go to Product admin
   - Add products in new category
   - SKU auto-generates (e.g., "ELC-PWR-001")
3. Import Items:
   - Prepare CSV with new items
   - Import via CSV action
4. Generate Labels:
   - Select new items
   - Generate PDF labels
   - Print and apply

---

## Troubleshooting

### Issue: Product SKU Auto-Generation Failed

**SKU Logic:**
1. Product is inserted first to get `id`.
2. SKU is generated deterministically:
   - `WORKSHOP_CODE-CATEGORY_CODE-<PRODUCT_ID_PADDED_6>`
   - Example: `MECH-WRENCH-000123`
3. SKU is saved on the same product row.

**How to detect:**
```bash
python manage.py repair_product_skus --settings=config.settings.local
```

This reports:
- `MISSING`: empty `sku_code`
- `INVALID`: `sku_code` differs from expected deterministic value

**How to rerun/retry and fix:**
```bash
python manage.py repair_product_skus --settings=config.settings.local --fix
```

**Repair only one product:**
```bash
python manage.py repair_product_skus --settings=config.settings.local --product-id 123 --fix
```

**Operational guidance:**
- Run check after bulk import/migration.
- Add the check command to periodic operations.

### Issue: Cannot Checkout Item

**Possible Causes:**
1. Item status is not "Available"
   - Check item status
   - If checked out, return it first
   - If in maintenance, wait for repair
2. Item is lost or damaged
   - Cannot checkout lost/damaged items
   - Use different item
3. Permission denied
   - User lacks checkout permission
   - Contact administrator

### Issue: CSV Import Fails

**Possible Causes:**
1. Product SKU not found
   - Verify SKU exists in system
   - Create product if needed
2. Serial number already exists
   - Check for duplicates in CSV
   - Use unique serial numbers
3. Location not found
   - Verify location exists
   - Create location if needed
4. Invalid CSV format
   - Check header row: `product_sku,serial_number,location`
   - Check for extra columns
   - Check for encoding issues (use UTF-8)

### Issue: Barcode Labels Not Printing

**Possible Causes:**
1. PDF not downloading
   - Check browser settings
   - Allow pop-ups for site
2. Labels misaligned
   - Check printer settings (100% scale, no fit-to-page)
   - Use correct label sheets (70×40mm)
3. Barcodes not scanning
   - Print quality too low
   - Use higher quality printer
   - Regenerate barcodes

### Issue: Stock Count Incorrect

**Possible Causes:**
1. Items not returned properly
   - Check for unreturned checkouts
   - Process returns
2. Items marked wrong status
   - Review item statuses
   - Correct as needed
3. Physical items missing
   - Conduct physical count
   - Mark missing items as lost
4. Database inconsistency
   - Contact administrator
   - Run reconciliation query

---

## Best Practices

### Checkout Best Practices

1. **Always verify item condition** before checkout
2. **Set realistic return dates** (typically 7 days)
3. **Add notes** for special circumstances
4. **Confirm user identity** before checkout
5. **Print checkout receipt** if needed

### Return Best Practices

1. **Inspect item condition** on return
2. **Report damage immediately** if found
3. **Update location** if item moved
4. **Add notes** about condition
5. **Process returns promptly** (same day)

### Maintenance Best Practices

1. **Document issues clearly** in maintenance log
2. **Track repair costs** accurately
3. **Set realistic repair timelines**
4. **Communicate status** to users waiting for item
5. **Return to service promptly** when fixed

### Data Entry Best Practices

1. **Use consistent serial number format**
2. **Double-check before submitting**
3. **Add descriptive notes**
4. **Verify autocomplete selections**
5. **Review changes before saving**

### Security Best Practices

1. **Log out when leaving workstation**
2. **Don't share passwords**
3. **Report suspicious activity**
4. **Review audit logs regularly**
5. **Follow permission guidelines**

---

## Emergency Procedures

### System Down

1. **Switch to manual tracking**
   - Use paper checkout sheets
   - Record all transactions
2. **Contact IT support**
3. **When system returns:**
   - Enter manual transactions
   - Verify data integrity

### Data Loss

1. **Stop all operations**
2. **Contact administrator immediately**
3. **Do not attempt recovery yourself**
4. **Administrator will restore from backup**
5. **Verify data after restore**

### Security Breach

1. **Report immediately** to security team
2. **Change passwords** if compromised
3. **Review audit logs** for unauthorized access
4. **Document incident**
5. **Follow incident response plan**

---

## Contact Information

**System Administrator:**
- Email: admin@workshop.com
- Phone: +1-XXX-XXX-XXXX

**IT Support:**
- Email: support@workshop.com
- Phone: +1-XXX-XXX-XXXX

**Emergency Contact:**
- Phone: +1-XXX-XXX-XXXX (24/7)
