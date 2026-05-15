from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("gis_store", "0035_giaodichkho_signature_otp_log"),
    ]

    operations = [
        migrations.AddField(
            model_name="nhanvien",
            name="co_quyen_nhap_kho",
            field=models.BooleanField(default=True, verbose_name="Được nhập kho"),
        ),
    ]
