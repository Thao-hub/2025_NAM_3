from django.conf import settings
from django.db import migrations, models
from django.utils import timezone


def seed_opening_stock(apps, schema_editor):
    SanPham = apps.get_model("gis_store", "SanPham")
    GiaoDichKho = apps.get_model("gis_store", "GiaoDichKho")

    for product in SanPham.objects.filter(ton_kho__gt=0):
        if GiaoDichKho.objects.filter(san_pham=product).exists():
            continue
        GiaoDichKho.objects.create(
            san_pham=product,
            loai="import",
            so_luong=product.ton_kho,
            ton_truoc=0,
            ton_sau=product.ton_kho,
            ghi_chu="Khởi tạo tồn kho ban đầu",
            created_at=timezone.now(),
        )


def clear_seeded_opening_stock(apps, schema_editor):
    GiaoDichKho = apps.get_model("gis_store", "GiaoDichKho")
    GiaoDichKho.objects.filter(
        loai="import",
        ghi_chu="Khởi tạo tồn kho ban đầu",
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("gis_store", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="GiaoDichKho",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("loai", models.CharField(choices=[("import", "Nhập kho"), ("export", "Xuất kho")], max_length=20, verbose_name="Loại giao dịch")),
                ("so_luong", models.PositiveIntegerField(default=1, verbose_name="Số lượng")),
                ("ton_truoc", models.PositiveIntegerField(default=0, editable=False, verbose_name="Tồn trước")),
                ("ton_sau", models.PositiveIntegerField(default=0, editable=False, verbose_name="Tồn sau")),
                ("ghi_chu", models.TextField(blank=True, verbose_name="Ghi chú")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Thời gian tạo")),
                ("created_by", models.ForeignKey(blank=True, null=True, on_delete=models.deletion.SET_NULL, related_name="giao_dich_kho_da_tao", to=settings.AUTH_USER_MODEL, verbose_name="Người tạo")),
                ("don_hang", models.ForeignKey(blank=True, null=True, on_delete=models.deletion.SET_NULL, related_name="giao_dich_kho", to="gis_store.donhang", verbose_name="Đơn hàng liên quan")),
                ("san_pham", models.ForeignKey(on_delete=models.deletion.CASCADE, related_name="giao_dich_kho", to="gis_store.sanpham", verbose_name="Sản phẩm")),
            ],
            options={
                "verbose_name": "Giao dịch kho",
                "verbose_name_plural": "Giao dịch kho",
                "ordering": ["-created_at", "-id"],
            },
        ),
        migrations.RunPython(seed_opening_stock, clear_seeded_opening_stock),
    ]

