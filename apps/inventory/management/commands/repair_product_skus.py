from django.core.management.base import BaseCommand
from django.db import transaction

from apps.inventory.models import Product
from core.services.sku_service import SKUService


class Command(BaseCommand):
    help = "Check product SKU integrity and optionally repair missing/invalid SKUs."

    def add_arguments(self, parser):
        parser.add_argument(
            "--fix",
            action="store_true",
            help="Apply fixes for missing/invalid SKUs.",
        )
        parser.add_argument(
            "--product-id",
            type=int,
            help="Only check/fix a specific product id.",
        )

    def handle(self, *args, **options):
        fix = options["fix"]
        product_id = options.get("product_id")

        qs = Product.objects.select_related("workshop_unit", "category").order_by("id")
        if product_id:
            qs = qs.filter(id=product_id)

        checked = 0
        missing = 0
        invalid = 0
        fixed = 0

        for product in qs:
            checked += 1
            expected = SKUService.generate_sku(product)
            current = (product.sku_code or "").strip()

            if not current:
                missing += 1
                self.stdout.write(
                    self.style.WARNING(
                        f"[MISSING] product_id={product.id} expected={expected}"
                    )
                )
                if fix:
                    with transaction.atomic():
                        Product.objects.filter(pk=product.pk).update(sku_code=expected)
                    fixed += 1
                continue

            if current != expected:
                invalid += 1
                self.stdout.write(
                    self.style.WARNING(
                        f"[INVALID] product_id={product.id} current={current} expected={expected}"
                    )
                )
                if fix:
                    with transaction.atomic():
                        Product.objects.filter(pk=product.pk).update(sku_code=expected)
                    fixed += 1

        summary = (
            f"checked={checked} missing={missing} invalid={invalid} fixed={fixed} fix_mode={fix}"
        )

        if missing == 0 and invalid == 0:
            self.stdout.write(self.style.SUCCESS(f"SKU integrity OK: {summary}"))
            return

        if fix:
            self.stdout.write(self.style.SUCCESS(f"SKU repair complete: {summary}"))
        else:
            self.stdout.write(self.style.ERROR(f"SKU integrity issues found: {summary}"))
            self.stdout.write("Run again with --fix to repair.")
