from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("gis_store", "0042_danhgiacuahang_unique_user_store_review"),
    ]

    operations = [
        migrations.CreateModel(
            name="TrangGioiThieu",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("tieu_de", models.CharField(default="Giới thiệu hệ thống", max_length=180, verbose_name="Tiêu đề")),
                ("mo_ta_ngan", models.TextField(blank=True, verbose_name="Mô tả ngắn")),
                ("noi_dung", models.TextField(blank=True, verbose_name="Nội dung")),
                ("anh_bia", models.ImageField(blank=True, null=True, upload_to="about/", verbose_name="Ảnh bìa")),
                ("anh_noi_dung_1", models.ImageField(blank=True, null=True, upload_to="about/", verbose_name="Ảnh nội dung 1")),
                ("anh_noi_dung_2", models.ImageField(blank=True, null=True, upload_to="about/", verbose_name="Ảnh nội dung 2")),
                ("anh_noi_dung_3", models.ImageField(blank=True, null=True, upload_to="about/", verbose_name="Ảnh nội dung 3")),
                ("cap_nhat_luc", models.DateTimeField(auto_now=True, verbose_name="Cập nhật lúc")),
            ],
            options={
                "verbose_name": "Trang giới thiệu",
                "verbose_name_plural": "Trang giới thiệu",
            },
        ),
    ]
