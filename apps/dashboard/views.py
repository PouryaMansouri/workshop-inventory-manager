from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone

from core.selectors.transactions import TransactionSelector


@login_required(login_url="/login/")
def my_tools_view(request):
    """Show currently checked out tools for the logged-in user."""
    active_tools = TransactionSelector.get_checked_out_items().filter(user=request.user)

    rows = []
    today = timezone.now().date()
    for txn in active_tools:
        days_out = (today - txn.date_out.date()).days
        days_left = None
        if txn.expected_return_date:
            days_left = (txn.expected_return_date - today).days

        sku = txn.item.product.sku_code or ""
        serial = txn.item.serial_number or ""
        barcode = txn.item.barcode or ""

        # Avoid visually duplicated codes when serial already contains SKU prefix.
        # Example:
        # serial:  ELEC-SCREWDRIVER-000004-0029
        # barcode: ELEC-SCREWDRIVER-000004-ELEC-SCREWDRIVER-000004-0029
        serial_compact = serial
        if sku and serial.startswith(f"{sku}-"):
            serial_compact = serial[len(sku) + 1 :]

        barcode_display = barcode
        if serial and barcode.endswith(serial):
            barcode_display = serial
        elif sku and barcode.startswith(f"{sku}-{sku}-"):
            barcode_display = barcode[len(sku) + 1 :]

        rows.append(
            {
                "transaction_id": txn.id,
                "item_name": txn.item.product.name,
                "barcode": barcode_display,
                "serial": serial_compact,
                "date_out": txn.date_out,
                "expected_return_date": txn.expected_return_date,
                "days_out": days_out,
                "days_left": days_left,
                "is_overdue": txn.is_overdue,
            }
        )

    context = {
        "rows": rows,
        "count": len(rows),
    }
    return render(request, "dashboard/my_tools.html", context)


@login_required(login_url="/login/")
def my_tools_history_view(request):
    """Show transaction history for the logged-in user."""
    transactions = TransactionSelector.get_user_transactions(request.user)

    rows = []
    for txn in transactions:
        status_text = "-"
        return_date = txn.returned_at

        if txn.transaction_type == "checkout":
            if txn.returned_at:
                status_text = "تحویل بسته شده"
            elif txn.is_overdue:
                status_text = "تحویل معوقه"
            else:
                status_text = "تحویل فعال"
        elif txn.transaction_type == "return":
            status_text = "بازگشت انجام شده"
            # Return transaction stores return time in date_out.
            return_date = txn.date_out
        elif txn.transaction_type == "lost":
            status_text = "گم‌شده"
        elif txn.transaction_type == "damaged":
            status_text = "خراب"
        elif txn.transaction_type == "consume":
            status_text = "مصرف شده"

        rows.append(
            {
                "id": txn.id,
                "item_name": txn.item.product.name,
                "barcode": txn.item.barcode,
                "serial": txn.item.serial_number,
                "type": txn.transaction_type,
                "type_display": txn.get_transaction_type_display(),
                "date_out": txn.date_out,
                "expected_return_date": txn.expected_return_date,
                "returned_at": return_date,
                "status_text": status_text,
                "notes": txn.notes,
            }
        )

    context = {
        "rows": rows,
        "count": len(rows),
    }
    return render(request, "dashboard/my_tools_history.html", context)
