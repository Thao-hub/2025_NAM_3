from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("gis_store", "0034_xacnhanthanhtoan"),
    ]

    operations = [
        migrations.AddField(
            model_name="giaodichkho",
            name="signed_at",
            field=models.DateTimeField(blank=True, null=True, verbose_name="Thời gian ký"),
        ),
        migrations.AddField(
            model_name="giaodichkho",
            name="signed_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="giao_dich_kho_da_ky",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Người ký",
            ),
        ),
        migrations.AddField(
            model_name="giaodichkho",
            name="signed_ip",
            field=models.CharField(blank=True, max_length=45, verbose_name="IP ký"),
        ),
        migrations.AddField(
            model_name="giaodichkho",
            name="signed_user_agent",
            field=models.CharField(blank=True, max_length=255, verbose_name="Trình duyệt ký"),
        ),
        migrations.AddField(
            model_name="giaodichkho",
            name="otp_code_hash",
            field=models.CharField(blank=True, max_length=128, verbose_name="Mã OTP (hash)"),
        ),
        migrations.AddField(
            model_name="giaodichkho",
            name="otp_expires_at",
            field=models.DateTimeField(blank=True, null=True, verbose_name="Hết hạn OTP"),
        ),
        migrations.AddField(
            model_name="giaodichkho",
            name="otp_verified_at",
            field=models.DateTimeField(blank=True, null=True, verbose_name="Xác nhận OTP lúc"),
        ),
        migrations.AddField(
            model_name="giaodichkho",
            name="otp_verified_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="giao_dich_kho_xac_nhan_otp",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Người xác nhận OTP",
            ),
        ),
        migrations.AddField(
            model_name="giaodichkho",
            name="otp_verified_ip",
            field=models.CharField(blank=True, max_length=45, verbose_name="IP xác nhận OTP"),
        ),
        migrations.AddField(
            model_name="giaodichkho",
            name="otp_verified_user_agent",
            field=models.CharField(blank=True, max_length=255, verbose_name="Trình duyệt xác nhận OTP"),
        ),
        migrations.AddField(
            model_name="giaodichkho",
            name="otp_recipient_email",
            field=models.EmailField(blank=True, max_length=254, verbose_name="Email nhận OTP"),
        ),
    ]
