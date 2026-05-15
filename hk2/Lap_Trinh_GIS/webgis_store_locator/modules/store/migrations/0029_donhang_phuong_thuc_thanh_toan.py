from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("gis_store", "0028_alter_khuyenmai_ma_code"),
    ]

    operations = [
        migrations.AddField(
            model_name="donhang",
            name="phuong_thuc_thanh_toan",
            field=models.CharField(
                choices=[
                    ("cod", "Thanh toán khi nhận hàng"),
                    ("bank_transfer", "Chuyển khoản ngân hàng"),
                    ("ewallet", "Ví điện tử"),
                ],
                default="cod",
                max_length=30,
                verbose_name="Phương thức thanh toán",
            ),
        ),
    ]
