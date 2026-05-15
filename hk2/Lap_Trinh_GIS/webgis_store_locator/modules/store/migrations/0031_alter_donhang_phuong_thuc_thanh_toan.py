from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("gis_store", "0030_donhang_trang_thai_thanh_toan"),
    ]

    operations = [
        migrations.AlterField(
            model_name="donhang",
            name="phuong_thuc_thanh_toan",
            field=models.CharField(
                choices=[
                    ("cod", "Thanh toán khi nhận hàng"),
                    ("bank_transfer", "Chuyển khoản ngân hàng"),
                    ("momo", "Ví MoMo"),
                    ("ewallet", "Ví điện tử"),
                ],
                default="cod",
                max_length=30,
                verbose_name="Phương thức thanh toán",
            ),
        ),
    ]
