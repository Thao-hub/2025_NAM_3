from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("gis_store", "0045_tranggioithieuhinhanh_tieu_de"),
    ]

    operations = [
        migrations.AddField(
            model_name="tranggioithieuhinhanh",
            name="nhom",
            field=models.CharField(blank=True, db_index=True, max_length=50, verbose_name="Nhóm ảnh"),
        ),
    ]
