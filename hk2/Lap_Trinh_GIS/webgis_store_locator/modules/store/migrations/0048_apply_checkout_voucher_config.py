from django.db import migrations


PROMO_RULES = [
    {
        "match": ("mì trộn", "pepsi"),
        "ma_code": "COMBO5K",
        "loai_giam": "fixed",
        "gia_tri_giam": 5000,
    },
    {
        "match": ("froster",),
        "ma_code": "FROSTER33",
        "loai_giam": "percent",
        "gia_tri_giam": 33,
    },
    {
        "match": ("youus",),
        "ma_code": "YOUUS50",
        "loai_giam": "percent",
        "gia_tri_giam": 50,
    },
    {
        "match": ("tokbokki", "nước suối"),
        "ma_code": "TOK10",
        "loai_giam": "percent",
        "gia_tri_giam": 10,
    },
]


def apply_checkout_voucher_config(apps, schema_editor):
    KhuyenMai = apps.get_model("gis_store", "KhuyenMai")

    for voucher in KhuyenMai.objects.all().order_by("pk"):
        name = (getattr(voucher, "ten", "") or "").lower()
        matched_rule = None
        for rule in PROMO_RULES:
            if all(keyword in name for keyword in rule["match"]):
                matched_rule = rule
                break
        if matched_rule is None:
            continue

        voucher.ma_code = matched_rule["ma_code"]
        voucher.loai_giam = matched_rule["loai_giam"]
        voucher.gia_tri_giam = matched_rule["gia_tri_giam"]
        voucher.gia_tri_don_hang_toi_thieu = 0
        voucher.giam_toi_da = None
        voucher.dang_ap_dung = True
        voucher.save(
            update_fields=[
                "ma_code",
                "loai_giam",
                "gia_tri_giam",
                "gia_tri_don_hang_toi_thieu",
                "giam_toi_da",
                "dang_ap_dung",
            ]
        )
        voucher.cua_hang.clear()


class Migration(migrations.Migration):
    dependencies = [
        ("gis_store", "0047_seed_checkout_vouchers"),
    ]

    operations = [
        migrations.RunPython(apply_checkout_voucher_config, migrations.RunPython.noop),
    ]
