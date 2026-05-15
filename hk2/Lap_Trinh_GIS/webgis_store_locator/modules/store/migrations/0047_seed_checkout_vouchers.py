from django.db import migrations


PROMO_UPDATES = {
    "Combo Thần Thánh: Mì Trộn + Pepsi": {
        "ma_code": "COMBO5K",
        "loai_giam": "fixed",
        "gia_tri_giam": 5000,
        "gia_tri_don_hang_toi_thieu": 0,
        "giam_toi_da": None,
        "dang_ap_dung": True,
    },
    "Mua 2 Tặng 1: Froster Cầu Vồng": {
        "ma_code": "FROSTER33",
        "loai_giam": "percent",
        "gia_tri_giam": 33,
        "gia_tri_don_hang_toi_thieu": 0,
        "giam_toi_da": None,
        "dang_ap_dung": True,
    },
    "Mua 1 Tặng 1: Dòng sản phẩm Youus": {
        "ma_code": "YOUUS50",
        "loai_giam": "percent",
        "gia_tri_giam": 50,
        "gia_tri_don_hang_toi_thieu": 0,
        "giam_toi_da": None,
        "dang_ap_dung": True,
    },
    "Combo Hàn Quốc: Tokbokki + Nước suối": {
        "ma_code": "TOK10",
        "loai_giam": "percent",
        "gia_tri_giam": 10,
        "gia_tri_don_hang_toi_thieu": 0,
        "giam_toi_da": None,
        "dang_ap_dung": True,
    },
}


def seed_checkout_vouchers(apps, schema_editor):
    KhuyenMai = apps.get_model("gis_store", "KhuyenMai")

    for promo_name, values in PROMO_UPDATES.items():
        voucher = KhuyenMai.objects.filter(ten=promo_name).order_by("pk").first()
        if voucher is None:
            continue
        for field_name, field_value in values.items():
            setattr(voucher, field_name, field_value)
        voucher.save(update_fields=list(values.keys()))
        voucher.cua_hang.clear()


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("gis_store", "0046_tranggioithieuhinhanh_nhom"),
    ]

    operations = [
        migrations.RunPython(seed_checkout_vouchers, noop_reverse),
    ]
