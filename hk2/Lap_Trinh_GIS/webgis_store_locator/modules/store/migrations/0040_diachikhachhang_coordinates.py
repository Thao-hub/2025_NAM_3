from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ("gis_store", "0039_danhgiacuahang_tepdanhgiacuahang"),
    ]

    operations = [
        migrations.AddField(
            model_name="diachikhachhang",
            name="kinh_do",
            field=models.FloatField(
                blank=True,
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(-180),
                    django.core.validators.MaxValueValidator(180),
                ],
                verbose_name="Kinh độ giao hàng",
            ),
        ),
        migrations.AddField(
            model_name="diachikhachhang",
            name="vi_do",
            field=models.FloatField(
                blank=True,
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(-90),
                    django.core.validators.MaxValueValidator(90),
                ],
                verbose_name="Vĩ độ giao hàng",
            ),
        ),
    ]
