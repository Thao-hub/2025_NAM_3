from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("gis_store", "0043_tranggioithieu"),
    ]

    operations = [
        migrations.CreateModel(
            name="TrangGioiThieuHinhAnh",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("hinh_anh", models.ImageField(upload_to="about/", verbose_name="Hình ảnh")),
                ("chu_thich", models.CharField(blank=True, max_length=150, verbose_name="Chú thích")),
                ("thu_tu", models.PositiveIntegerField(default=0, verbose_name="Thứ tự")),
                (
                    "trang",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        related_name="hinh_anh_phu",
                        to="gis_store.tranggioithieu",
                        verbose_name="Trang giới thiệu",
                    ),
                ),
            ],
            options={
                "verbose_name": "Ảnh trang giới thiệu",
                "verbose_name_plural": "Ảnh trang giới thiệu",
                "ordering": ["thu_tu", "id"],
            },
        ),
    ]
