from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("gis_store", "0036_nhanvien_co_quyen_nhap_kho"),
    ]

    operations = [
        migrations.CreateModel(
            name="TonKhoAudit",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("loai", models.CharField(choices=[("import", "Nhập kho"), ("export", "Xuất kho")], max_length=20, verbose_name="Loại giao dịch")),
                ("so_luong", models.PositiveIntegerField(default=0, verbose_name="Số lượng")),
                ("ton_truoc", models.IntegerField(default=0, verbose_name="Tồn trước")),
                ("ton_sau", models.IntegerField(default=0, verbose_name="Tồn sau")),
                ("hanh_dong", models.CharField(choices=[("create", "Tạo giao dịch"), ("update", "Cập nhật giao dịch"), ("delete", "Xóa giao dịch")], max_length=20, verbose_name="Hành động")),
                ("ly_do", models.TextField(blank=True, verbose_name="Lý do")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Thời gian")),
                ("cua_hang", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="audit_logs", to="gis_store.cuahang", verbose_name="Cửa hàng")),
                ("created_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="ton_kho_audit_logs", to=settings.AUTH_USER_MODEL, verbose_name="Người thao tác")),
                ("giao_dich", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="audit_logs", to="gis_store.giaodichkho", verbose_name="Giao dịch kho")),
                ("san_pham", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="audit_logs", to="gis_store.sanpham", verbose_name="Sản phẩm")),
            ],
            options={
                "verbose_name": "Nhật ký tồn kho",
                "verbose_name_plural": "Nhật ký tồn kho",
                "ordering": ["-created_at", "-id"],
            },
        ),
    ]
