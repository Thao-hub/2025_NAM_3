from __future__ import annotations

from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.utils import timezone

from modules.store.models import CuaHang, GiaoDichKho, NhanVien, SanPham, TonKhoCuaHang


SIGNATURE_GIF_BYTES = (
    b"GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!"
    b"\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00"
    b"\x00\x02\x02D\x01\x00;"
)
SIGNATURE_RELATIVE_PATH = "signatures/restock-bulk.gif"


def _ensure_signature_file() -> str:
    signature_path = Path(settings.MEDIA_ROOT) / SIGNATURE_RELATIVE_PATH
    signature_path.parent.mkdir(parents=True, exist_ok=True)
    if not signature_path.exists():
        signature_path.write_bytes(SIGNATURE_GIF_BYTES)
    return SIGNATURE_RELATIVE_PATH


def _aggregate_signed_product_totals(product_ids):
    import_totals = {
        row["san_pham_id"]: int(row["qty"] or 0)
        for row in GiaoDichKho.objects.filter(san_pham_id__in=product_ids, loai="import")
        .values("san_pham_id")
        .annotate(qty=Coalesce(Sum("so_luong"), 0))
    }
    export_totals = {
        row["san_pham_id"]: int(row["qty"] or 0)
        for row in GiaoDichKho.objects.filter(san_pham_id__in=product_ids, loai="export")
        .values("san_pham_id")
        .annotate(qty=Coalesce(Sum("so_luong"), 0))
    }
    return {
        product_id: int(import_totals.get(product_id, 0)) - int(export_totals.get(product_id, 0))
        for product_id in product_ids
    }


def _aggregate_signed_store_totals(store_ids, product_ids):
    import_totals = {
        (row["cua_hang_id"], row["san_pham_id"]): int(row["qty"] or 0)
        for row in GiaoDichKho.objects.filter(
            cua_hang_id__in=store_ids,
            san_pham_id__in=product_ids,
            loai="import",
        )
        .values("cua_hang_id", "san_pham_id")
        .annotate(qty=Coalesce(Sum("so_luong"), 0))
    }
    export_totals = {
        (row["cua_hang_id"], row["san_pham_id"]): int(row["qty"] or 0)
        for row in GiaoDichKho.objects.filter(
            cua_hang_id__in=store_ids,
            san_pham_id__in=product_ids,
            loai="export",
        )
        .values("cua_hang_id", "san_pham_id")
        .annotate(qty=Coalesce(Sum("so_luong"), 0))
    }
    totals = {}
    for store_id in store_ids:
        for product_id in product_ids:
            key = (store_id, product_id)
            totals[key] = int(import_totals.get(key, 0)) - int(export_totals.get(key, 0))
    return totals


def restock_products(*, target_stock: int, note: str, store_ids=None, trigger_threshold=None):
    if target_stock <= 0:
        raise ValueError("--target-stock must be greater than 0.")
    if not (note or "").strip():
        raise ValueError("Vui lòng nhập lý do điều chỉnh tồn kho.")
    if trigger_threshold is None:
        trigger_threshold = SanPham.LOW_STOCK_THRESHOLD
    try:
        trigger_threshold = int(trigger_threshold)
    except (TypeError, ValueError):
        raise ValueError("--trigger-threshold must be a valid integer.")
    if trigger_threshold < 0:
        raise ValueError("--trigger-threshold must be 0 or greater.")

    requested_store_ids = sorted({int(store_id) for store_id in (store_ids or [])})
    stores_qs = CuaHang.objects.order_by("pk")
    if requested_store_ids:
        stores_qs = stores_qs.filter(pk__in=requested_store_ids)
    stores = list(stores_qs)
    products = list(SanPham.objects.order_by("pk"))

    if requested_store_ids:
        found_store_ids = {store.pk for store in stores}
        missing_store_ids = [store_id for store_id in requested_store_ids if store_id not in found_store_ids]
        if missing_store_ids:
            raise LookupError("Store IDs not found: " + ", ".join(str(store_id) for store_id in missing_store_ids))

    if not stores:
        raise LookupError("No stores found to restock.")
    if not products:
        raise LookupError("No products found to restock.")

    signature_path = _ensure_signature_file()
    store_ids_list = [store.pk for store in stores]
    product_ids = [product.pk for product in products]
    product_totals = _aggregate_signed_product_totals(product_ids)
    store_stock_totals = _aggregate_signed_store_totals(store_ids_list, product_ids)

    stock_rows = list(
        TonKhoCuaHang.objects.filter(
            cua_hang_id__in=store_ids_list,
            san_pham_id__in=product_ids,
        )
    )
    stock_map = {(row.cua_hang_id, row.san_pham_id): row for row in stock_rows}

    employee_map = {}
    for employee in NhanVien.objects.filter(cua_hang_id__in=store_ids_list).order_by("cua_hang_id", "pk"):
        employee_map.setdefault(employee.cua_hang_id, employee)

    store_product_pairs = {(store.pk, product.pk) for store in stores for product in products}
    through_model = CuaHang.san_pham.through
    existing_links = set(
        through_model.objects.filter(
            cuahang_id__in=store_ids_list,
            sanpham_id__in=product_ids,
        ).values_list("cuahang_id", "sanpham_id")
    )

    created_employees = 0
    created_movements = 0
    imported_units = 0
    reconciled_stock_rows = 0

    with transaction.atomic():
        for store in stores:
            if store.pk in employee_map:
                continue
            employee = NhanVien.objects.create(
                cua_hang=store,
                ho_ten=f"Nhân viên nhập kho {store.ten}",
                chuc_vu="Kho",
            )
            employee_map[store.pk] = employee
            created_employees += 1

        missing_links = [
            through_model(cuahang_id=store_id, sanpham_id=product_id)
            for (store_id, product_id) in store_product_pairs - existing_links
        ]
        if missing_links:
            through_model.objects.bulk_create(missing_links, ignore_conflicts=True, batch_size=1000)

        new_movements = []
        rows_to_create = []
        rows_to_update = {}
        products_to_update = []
        created_at = timezone.now()

        for product in products:
            running_total = int(product_totals.get(product.pk, 0))
            for store in stores:
                key = (store.pk, product.pk)
                current_stock = int(store_stock_totals.get(key, 0))
                row = stock_map.get(key)

                if row is None:
                    row = TonKhoCuaHang(
                        cua_hang_id=store.pk,
                        san_pham_id=product.pk,
                        ton_kho=current_stock,
                    )
                    stock_map[key] = row
                    rows_to_create.append(row)
                    reconciled_stock_rows += 1
                elif int(row.ton_kho or 0) != current_stock:
                    row.ton_kho = current_stock
                    rows_to_update[key] = row
                    reconciled_stock_rows += 1

                if current_stock > trigger_threshold or current_stock >= target_stock:
                    continue

                delta = target_stock - current_stock
                new_movements.append(
                    GiaoDichKho(
                        san_pham_id=product.pk,
                        cua_hang_id=store.pk,
                        nhan_vien_id=employee_map[store.pk].pk,
                        loai="import",
                        so_luong=delta,
                        ton_truoc=running_total,
                        ton_sau=running_total + delta,
                        ghi_chu=note,
                        chu_ky=signature_path,
                        created_at=created_at,
                    )
                )
                running_total += delta
                imported_units += delta
                created_movements += 1
                store_stock_totals[key] = target_stock
                row.ton_kho = target_stock
                if key not in rows_to_update and row.pk:
                    rows_to_update[key] = row

            if int(product.ton_kho or 0) != running_total:
                product.ton_kho = running_total
                products_to_update.append(product)

        if new_movements:
            GiaoDichKho.objects.bulk_create(new_movements, batch_size=1000)
        if rows_to_create:
            TonKhoCuaHang.objects.bulk_create(rows_to_create, batch_size=1000)
        if rows_to_update:
            TonKhoCuaHang.objects.bulk_update(
                list(rows_to_update.values()),
                ["ton_kho", "updated_at"],
                batch_size=1000,
            )
        if products_to_update:
            SanPham.objects.bulk_update(products_to_update, ["ton_kho"], batch_size=500)

    return {
        "store_count": len(stores),
        "created_movements": created_movements,
        "imported_units": imported_units,
        "created_employees": created_employees,
        "reconciled_stock_rows": reconciled_stock_rows,
        "trigger_threshold": trigger_threshold,
    }


class Command(BaseCommand):
    help = (
        "Restock only store-product pairs that are empty or low, and "
        "reconcile store stock from inventory movements before importing."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--target-stock",
            type=int,
            default=25,
            help="Target stock quantity for low-stock store-product pairs. Default: 25",
        )
        parser.add_argument(
            "--trigger-threshold",
            type=int,
            default=SanPham.LOW_STOCK_THRESHOLD,
            help="Only restock store-product pairs with stock at or below this threshold.",
        )
        parser.add_argument(
            "--store-id",
            dest="store_ids",
            action="append",
            type=int,
            help="Restock a specific store by ID. Repeat this option to target multiple stores.",
        )
        parser.add_argument(
            "--store-ids",
            dest="store_ids_bulk",
            nargs="+",
            type=int,
            help="Restock multiple stores by ID in one command, e.g. --store-ids 1 2 3",
        )
        parser.add_argument(
            "--note",
            default="Nhập bù cho các cửa hàng đang thiếu hàng",
            help="Lý do điều chỉnh tồn kho cho các phiếu nhập tự động.",
        )

    def handle(self, *args, **options):
        target_stock = options["target_stock"]
        trigger_threshold = options["trigger_threshold"]
        note = (options["note"] or "").strip()
        single_store_ids = options.get("store_ids") or []
        bulk_store_ids = options.get("store_ids_bulk") or []
        requested_store_ids = []
        if single_store_ids:
            requested_store_ids.extend(single_store_ids)
        if bulk_store_ids:
            requested_store_ids.extend(bulk_store_ids)
        try:
            summary = restock_products(
                target_stock=target_stock,
                trigger_threshold=trigger_threshold,
                note=note,
                store_ids=requested_store_ids,
            )
        except ValueError as exc:
            self.stderr.write(self.style.ERROR(str(exc)))
            return
        except LookupError as exc:
            self.stderr.write(self.style.ERROR(str(exc)))
            return

        self.stdout.write(
            self.style.SUCCESS(
                "Restock completed: "
                f"{summary['store_count']} stores, "
                f"{summary['created_movements']} import movements, "
                f"{summary['imported_units']} units, "
                f"{summary['reconciled_stock_rows']} reconciled stock rows, "
                f"trigger threshold {summary['trigger_threshold']}."
            )
        )
