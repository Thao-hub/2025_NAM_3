from django.db import migrations, models


def seed_payment_status(apps, schema_editor):
    DonHang = apps.get_model("gis_store", "DonHang")
    DonHang.objects.filter(phuong_thuc_thanh_toan="bank_transfer").update(
        trang_thai_thanh_toan="awaiting_confirmation"
    )
    DonHang.objects.filter(phuong_thuc_thanh_toan__in=["cod", "ewallet"]).update(
        trang_thai_thanh_toan="unpaid"
    )


class Migration(migrations.Migration):

    dependencies = [
        ("gis_store", "0029_donhang_phuong_thuc_thanh_toan"),
    ]

    operations = [
        migrations.AddField(
            model_name="donhang",
            name="trang_thai_thanh_toan",
            field=models.CharField(
                choices=[
                    ("unpaid", "Chưa thanh toán"),
                    ("paid", "Đã thanh toán"),
                    ("awaiting_confirmation", "Chờ xác nhận chuyển khoản"),
                    ("refunded", "Hoàn tiền"),
                ],
                default="unpaid",
                max_length=30,
                verbose_name="Trạng thái thanh toán",
            ),
        ),
        migrations.RunPython(seed_payment_status, migrations.RunPython.noop),
    ]
