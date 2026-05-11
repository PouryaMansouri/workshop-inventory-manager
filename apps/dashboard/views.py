from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from apps.inventory.models import WorkshopUnit, ItemCheckConfirmation
from apps.users.models import UserExtension
from apps.transactions.models import Transaction

from core.selectors.transactions import TransactionSelector


def _build_user_menu(user) -> list[dict]:
    """Build quick navigation menu based on user access."""
    menu = [
        {"title": "خانه", "url": "/home/"},
        {"title": "ابزارهای فعال من", "url": "/my-tools/"},
        {"title": "تاریخچه ابزارهای من", "url": "/my-tools/history/"},
    ]

    if user.is_staff:
        menu.append({"title": "پنل مدیریت", "url": "/admin/"})

    can_view_reports = user.is_staff or user.has_perm("transactions.view_transaction")
    if can_view_reports:
        menu.extend(
            [
                {"title": "گزارش اقلام تجویلی", "url": "/reports/assigned-items/"},
                {"title": "جستجوی ابزارهای افراد", "url": "/reports/holder-tools/"},
            ]
        )

    menu.append({"title": "خروج", "url": "/accounts/logout/"})
    return menu


@login_required(login_url="/login/")
def home_view(request):
    """Home page with role-aware navigation."""
    context = {
        "menu_links": _build_user_menu(request.user),
    }
    return render(request, "dashboard/home.html", context)


@login_required(login_url="/login/")
def logout_view(request):
    """Logout endpoint that accepts GET for menu/button compatibility."""
    logout(request)
    return HttpResponseRedirect("/login/")


def _ensure_reports_access(user) -> None:
    """Ensure user can access operational reports."""
    if user.is_staff or user.has_perm("transactions.view_transaction"):
        return
    raise PermissionDenied("شما دسترسی مشاهده این گزارش را ندارید.")


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
        "menu_links": _build_user_menu(request.user),
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
        "menu_links": _build_user_menu(request.user),
    }
    return render(request, "dashboard/my_tools_history.html", context)


@login_required(login_url="/login/")
def assigned_items_report_view(request):
    """Assigned items report with filters."""
    _ensure_reports_access(request.user)
    holder_id = request.GET.get("holder_id")
    workshop_unit_id = request.GET.get("workshop_unit_id")
    active_param = request.GET.get("active")
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    is_active = None
    if active_param == "1":
        is_active = True
    elif active_param == "0":
        is_active = False

    rows = TransactionSelector.get_assigned_items_rows(
        holder_id=int(holder_id) if holder_id else None,
        workshop_unit_id=int(workshop_unit_id) if workshop_unit_id else None,
        is_active=is_active,
        start_date=start_date or None,
        end_date=end_date or None,
    )

    context = {
        "rows": rows,
        "count": len(rows),
        "menu_links": _build_user_menu(request.user),
        "holders": User.objects.filter(is_active=True).order_by("first_name", "last_name", "username"),
        "workshop_units": WorkshopUnit.objects.all().order_by("name"),
        "filters": {
            "holder_id": holder_id or "",
            "workshop_unit_id": workshop_unit_id or "",
            "active": active_param or "",
            "start_date": start_date or "",
            "end_date": end_date or "",
        },
    }
    return render(request, "dashboard/assigned_items_report.html", context)


@login_required(login_url="/login/")
def assigned_items_report_export_xlsx(request):
    """Export assigned-items report to Excel."""
    _ensure_reports_access(request.user)
    from openpyxl import Workbook

    holder_id = request.GET.get("holder_id")
    workshop_unit_id = request.GET.get("workshop_unit_id")
    active_param = request.GET.get("active")
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    is_active = None
    if active_param == "1":
        is_active = True
    elif active_param == "0":
        is_active = False

    rows = TransactionSelector.get_assigned_items_rows(
        holder_id=int(holder_id) if holder_id else None,
        workshop_unit_id=int(workshop_unit_id) if workshop_unit_id else None,
        is_active=is_active,
        start_date=start_date or None,
        end_date=end_date or None,
    )

    wb = Workbook()
    ws = wb.active
    ws.title = "Assigned Items"
    ws.append([
        "نام تحویل گیرنده",
        "واحد",
        "نام کالا",
        "کد",
        "سریال",
        "شروع بازه نگهداری",
        "پایان بازه نگهداری",
        "وضعیت",
        "آخرین تاییدکننده چک",
        "زمان آخرین تایید",
    ])
    for row in rows:
        ws.append([
            row["holder_name"],
            row["workshop_unit"],
            row["item_name"],
            row["code"],
            row["serial"],
            row["holding_range_start"].strftime("%Y-%m-%d %H:%M"),
            row["holding_range_end"].strftime("%Y-%m-%d %H:%M"),
            "فعال" if row["is_active"] else "بسته",
            row["last_check_by"] or "-",
            row["last_check_at"].strftime("%Y-%m-%d %H:%M") if row["last_check_at"] else "-",
        ])

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="assigned_items_report.xlsx"'
    wb.save(response)
    return response


@login_required(login_url="/login/")
def holder_tools_lookup_view(request):
    """Search active checked-out tools by phone number or personnel code."""
    _ensure_reports_access(request.user)
    query = (request.GET.get("q") or "").strip()
    rows = []
    holder = None
    error = ""
    success = ""
    confirmation_history_rows = []

    if request.method == "POST":
        if not request.user.is_staff:
            raise PermissionDenied("فقط کاربران staff مجاز به ثبت تایید دوره‌ای هستند.")
        query = (request.POST.get("q") or "").strip()
        notes = (request.POST.get("notes") or "").strip()
        selected_ids = request.POST.getlist("selected_txn_ids")

        extension = UserExtension.objects.select_related("user").filter(
            phone_number=query
        ).first()
        if extension is None:
            extension = UserExtension.objects.select_related("user").filter(
                personnel_code=query
            ).first()

        if extension is None:
            error = "کاربری با این شماره موبایل یا کد پرسنلی پیدا نشد."
        else:
            holder = extension.user
            active_checkouts = TransactionSelector.get_checked_out_items().filter(user=holder)
            if selected_ids:
                active_checkouts = active_checkouts.filter(id__in=selected_ids)
            else:
                active_checkouts = active_checkouts.none()

            confirmations = []
            for txn in active_checkouts:
                confirmations.append(
                    ItemCheckConfirmation(
                        item=txn.item,
                        confirmed_by=request.user,
                        checkout_transaction=txn,
                        notes=notes,
                    )
                )
            if confirmations:
                ItemCheckConfirmation.objects.bulk_create(confirmations)
                success = f"تایید دوره‌ای برای {len(confirmations)} ابزار ثبت شد."
            else:
                error = "هیچ ابزار فعالی برای تایید انتخاب نشده است."

    if query:
        extension = UserExtension.objects.select_related("user").filter(
            phone_number=query
        ).first()
        if extension is None:
            extension = UserExtension.objects.select_related("user").filter(
                personnel_code=query
            ).first()

        if extension is None:
            error = "کاربری با این شماره موبایل یا کد پرسنلی پیدا نشد."
        else:
            holder = extension.user
            active_tools = TransactionSelector.get_checked_out_items().filter(user=holder)
            active_txn_ids = list(active_tools.values_list("id", flat=True))

            latest_by_txn = {}
            history_by_txn = {}
            if active_txn_ids:
                confirmations = (
                    ItemCheckConfirmation.objects.filter(checkout_transaction_id__in=active_txn_ids)
                    .select_related("confirmed_by", "checkout_transaction", "item")
                    .order_by("checkout_transaction_id", "-confirmed_at")
                )
                for conf in confirmations:
                    if conf.checkout_transaction_id not in latest_by_txn:
                        latest_by_txn[conf.checkout_transaction_id] = conf
                    history_by_txn.setdefault(conf.checkout_transaction_id, []).append(
                        {
                            "confirmed_by": conf.confirmed_by.get_full_name() or conf.confirmed_by.username,
                            "confirmed_at": conf.confirmed_at,
                            "notes": conf.notes or "-",
                        }
                    )

                # One flat table for full confirmation history of this holder's active tools
                for conf in confirmations:
                    confirmation_history_rows.append(
                        {
                            "transaction_id": conf.checkout_transaction_id,
                            "item_name": conf.item.product.name,
                            "barcode": conf.item.barcode,
                            "confirmed_by": conf.confirmed_by.get_full_name() or conf.confirmed_by.username,
                            "confirmed_at": conf.confirmed_at,
                            "notes": conf.notes or "-",
                        }
                    )

            for txn in active_tools:
                latest_check = latest_by_txn.get(txn.id)
                rows.append(
                    {
                        "item_name": txn.item.product.name,
                        "barcode": txn.item.barcode,
                        "serial": txn.item.serial_number,
                        "transaction_id": txn.id,
                        "date_out": txn.date_out,
                        "expected_return_date": txn.expected_return_date,
                        "is_overdue": txn.is_overdue,
                        "last_check_by": (
                            (latest_check.confirmed_by.get_full_name() or latest_check.confirmed_by.username)
                            if latest_check
                            else "-"
                        ),
                        "last_check_at": latest_check.confirmed_at if latest_check else None,
                        "last_check_notes": latest_check.notes if (latest_check and latest_check.notes) else "-",
                        "check_history": history_by_txn.get(txn.id, []),
                    }
                )

    context = {
        "query": query,
        "rows": rows,
        "count": len(rows),
        "holder": holder,
        "error": error,
        "success": success,
        "confirmation_history_rows": confirmation_history_rows,
        "menu_links": _build_user_menu(request.user),
    }
    return render(request, "dashboard/holder_tools_lookup.html", context)
