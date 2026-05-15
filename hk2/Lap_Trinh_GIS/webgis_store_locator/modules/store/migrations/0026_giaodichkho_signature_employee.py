from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("gis_store", "0025_giaodichkho"),
    ]

    operations = [
        migrations.AddField(
            model_name="giaodichkho",
            name="chu_ky",
            field=models.ImageField(blank=True, null=True, upload_to="signatures/", verbose_name="Chữ ký nhân viên"),
        ),
        migrations.AddField(
            model_name="giaodichkho",
            name="nhan_vien",
            field=models.ForeignKey(blank=True, null=True, on_delete=models.deletion.SET_NULL, related_name="giao_dich_kho", to="gis_store.nhanvien", verbose_name="Nhân viên ký"),
        ),
    ]
