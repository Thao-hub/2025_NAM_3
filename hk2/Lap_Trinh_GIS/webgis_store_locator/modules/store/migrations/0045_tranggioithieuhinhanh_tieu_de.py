from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("gis_store", "0044_tranggioithieuhinhanh"),
    ]

    operations = [
        migrations.AddField(
            model_name="tranggioithieuhinhanh",
            name="tieu_de",
            field=models.CharField(blank=True, max_length=150, verbose_name="Tiêu đề ảnh"),
        ),
    ]
