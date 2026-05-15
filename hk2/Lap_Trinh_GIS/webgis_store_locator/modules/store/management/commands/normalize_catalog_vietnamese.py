from django.core.management.base import BaseCommand

from modules.store.models import (
    ChuoiCuaHang,
    CuaHang,
    KhuyenMai,
    NhaCungCap,
    NhanVien,
    NhomSanPham,
    SanPham,
    ThuongHieu,
)


PRODUCT_NAME_MAP = {
    "Froster Cau Vong (Size L)": "Froster Cầu Vồng (Size L)",
    "Mi Tron Indomie Trung Op La Xuc Xich": "Mì Trộn Indomie Trứng Ốp La Xúc Xích",
    "Banh Bao Trung Muoi (Hap nong)": "Bánh Bao Trứng Muối (Hấp nóng)",
    "Banh Mi Op La 2 Trung": "Bánh Mì Ốp La 2 Trứng",
    "Ca Phe Bac Xiu Da (Ly lon)": "Cà Phê Bạc Xỉu Đá (Ly lớn)",
    "Xoi La Chuoi (Thit Kho Tau)": "Xôi Lá Chuối (Thịt Kho Tàu)",
    "Tokbokki Xuc Xich Sot Cay (Ly)": "Tokbokki Xúc Xích Sốt Cay (Ly)",
    "Nuoc Ep Dua Hau Youus 230ml": "Nước Ép Dưa Hấu Youus 230ml",
    "Bap Rang Bo Vi Pho Mai Youus": "Bắp Rang Bơ Vị Phô Mai Youus",
    "Lau Cha Ca Omok (Ly)": "Lẩu Chả Cá Omok (Ly)",
    "Com Nam Tom Mayonnaise": "Cơm Nắm Tôm Mayonnaise",
    "Mi Hao Hao Tom Chua Cay (Goi)": "Mì Hảo Hảo Tôm Chua Cay (Gói)",
    "Mi Ly Modern Lau Thai Tom": "Mì Ly Modern Lẩu Thái Tôm",
    "Nuoc Ngot Coca-Cola Zero 320ml": "Nước Ngọt Coca-Cola Zero 320ml",
    "Nuoc Tang Luc Sting Dau 330ml": "Nước Tăng Lực Sting Dâu 330ml",
    "Nuoc Tinh Khiet Aquafina 500ml": "Nước Tinh Khiết Aquafina 500ml",
    "Snack Khoai Tay O'Star Vi Kim Chi 63g": "Snack Khoai Tây O'Star Vị Kim Chi 63g",
    "Sua Tuoi TH True Milk Co Duong 180ml": "Sữa Tươi TH True Milk Có Đường 180ml",
}

GROUP_NAME_MAP = {
    "Do an che bien nong (Hot Food)": "Đồ ăn chế biến nóng (Hot Food)",
    "Do uong pha che (Barista/Froster)": "Đồ uống pha chế (Barista/Froster)",
    "Mi an lien & Thuc pham dong hop": "Mì ăn liền & Thực phẩm đóng hộp",
    "Nuoc giai khat & Do uong lanh": "Nước giải khát & Đồ uống lạnh",
    "Snack & Banh keo": "Snack & Bánh kẹo",
    "Sua & Che pham tu sua": "Sữa & Chế phẩm từ sữa",
    "Hoa my pham & Ca nhan": "Hóa mỹ phẩm & Cá nhân",
}

SUPPLIER_NAME_MAP = {
    "Cong ty TNHH Vong Tron Do (Red Circle)": "Công ty TNHH Vòng Tròn Đỏ (Red Circle)",
    "Cong ty TNHH Thuc Pham Orion Vina": "Công ty TNHH Thực Phẩm Orion Vina",
}

BRAND_NAME_MAP = {
    "Youus (Han Quoc)": "Youus (Hàn Quốc)",
    "Hao Hao": "Hảo Hảo",
}

CHAIN_NAME_MAP = {
    "CIRCLEK": "Circle K",
}

STORE_NAME_MAP = {
    "Circle K Viet Nam": "Circle K Việt Nam",
}

SUPPLIER_NAME_MAP.update(
    {
        "GS Retail Viet Nam": "GS Retail Việt Nam",
        "Suntory PepsiCo Vietnam": "Suntory PepsiCo Việt Nam",
        "Coca-Cola Vietnam": "Coca-Cola Việt Nam",
        "Acecook Vietnam": "Acecook Việt Nam",
        "GS Retail Vietnam": "GS Retail Việt Nam",
        "Suntory PepsiCo Viet Nam": "Suntory PepsiCo Việt Nam",
        "Coca-Cola Viet Nam": "Coca-Cola Việt Nam",
        "Acecook Viet Nam": "Acecook Việt Nam",
    }
)

PROMO_NAME_MAP = {
    "Combo Than Thanh: Mi Tron + Pepsi": "Combo Thần Thánh: Mì Trộn + Pepsi",
    "Mua 2 Tang 1: Froster Cau Vong": "Mua 2 Tặng 1: Froster Cầu Vồng",
    "Mua 1 Tang 1: Dong san pham Youus": "Mua 1 Tặng 1: Dòng sản phẩm Youus",
    "Combo Han Quoc: Tokbokki + Nuoc suoi": "Combo Hàn Quốc: Tokbokki + Nước suối",
}

CHAIN_DESCRIPTION_MAP = {
    "Take it easy. Chuoi cua hang tien loi mo cua 24/7, noi tieng voi do an che bien tai cho.": "Take it easy. Chuỗi cửa hàng tiện lợi mở cửa 24/7, nổi tiếng với đồ ăn chế biến tại chỗ.",
    "Lifestyle Platform. Chuoi cua hang tien loi Han Quoc, mang den trai nghiem am thuc Han Quoc.": "Lifestyle Platform. Chuỗi cửa hàng tiện lợi Hàn Quốc, mang đến trải nghiệm ẩm thực Hàn Quốc.",
}

NAME_TOKEN_MAP = {
    "Nguyen": "Nguyễn",
    "Tran": "Trần",
    "Le": "Lê",
    "Pham": "Phạm",
    "Vo": "Võ",
    "Do": "Đỗ",
    "Hoang": "Hoàng",
    "Bui": "Bùi",
    "Huynh": "Huỳnh",
    "Phan": "Phan",
    "Vu": "Vũ",
    "Dang": "Đặng",
    "Van": "Văn",
    "Thi": "Thị",
    "Duc": "Đức",
    "Thanh": "Thanh",
    "Ngoc": "Ngọc",
    "Tuan": "Tuấn",
    "Huu": "Hữu",
    "Xuan": "Xuân",
    "Tan": "Tân",
    "Thu": "Thu",
    "Trang": "Trang",
    "Vy": "Vy",
    "Khanh": "Khánh",
    "Uyen": "Uyên",
    "Nhung": "Nhung",
    "Dung": "Dũng",
    "Quan": "Quân",
    "Phuc": "Phúc",
    "Binh": "Bình",
    "Mai": "Mai",
    "Long": "Long",
    "Em": "Em",
    "An": "An",
    "Giang": "Giang",
    "Han": "Hân",
    "Cuong": "Cường",
    "Minh": "Minh",
    "Gia": "Gia",
}

ADDRESS_TOKEN_MAP = {
    "Viet Nam": "Việt Nam",
    "Quan": "Quận",
    "Q.": "Quận",
    "Phuong": "Phường",
    "P.": "Phường",
    "Duong": "Đường",
    "D.": "Đường",
    "So": "Số",
    "Ap": "Ấp",
    "Huyen": "Huyện",
    "Thi xa": "Thị xã",
    "Thi tran": "Thị trấn",
    "Thanh pho": "Thành phố",
}


def _apply_mapping(queryset, mapping):
    updated = 0
    for source, target in mapping.items():
        updated += queryset.filter(ten=source).update(ten=target)
    return updated


def _normalize_name(value: str) -> str:
    if not value:
        return value
    tokens = [t for t in value.replace("_", " ").split() if t]
    normalized = []
    for token in tokens:
        key = token.strip().title()
        normalized.append(NAME_TOKEN_MAP.get(key, key))
    return " ".join(normalized)


def _normalize_address(value: str) -> str:
    if not value:
        return value
    normalized = value
    normalized = normalized.replace("TPhườngHCM", "TP.HCM")
    normalized = normalized.replace("TPhuongHCM", "TP.HCM")
    normalized = normalized.replace("TP HCM", "TP.HCM")
    normalized = normalized.replace("TP. HCM", "TP.HCM")
    normalized = normalized.replace("TPHCM", "TP.HCM")
    normalized = normalized.replace("TP.HCM", "__TPHCM__")
    for source, target in ADDRESS_TOKEN_MAP.items():
        normalized = normalized.replace(source, target)
    normalized = normalized.replace("__TPHCM__", "TP.HCM")
    return normalized


def _apply_field_normalizer(queryset, field_name: str, normalizer):
    updated = 0
    for obj in queryset.only("id", field_name):
        raw_value = getattr(obj, field_name, "") or ""
        new_value = normalizer(raw_value)
        if new_value != raw_value:
            setattr(obj, field_name, new_value)
            obj.save(update_fields=[field_name])
            updated += 1
    return updated


def _apply_text_mapping(queryset, field_name: str, mapping):
    updated = 0
    for source, target in mapping.items():
        updated += queryset.filter(**{field_name: source}).update(**{field_name: target})
    return updated


class Command(BaseCommand):
    help = "Chuẩn hóa tên danh mục sản phẩm sang tiếng Việt có dấu."

    def handle(self, *args, **options):
        product_updated = _apply_mapping(SanPham.objects, PRODUCT_NAME_MAP)
        group_updated = _apply_mapping(NhomSanPham.objects, GROUP_NAME_MAP)
        supplier_updated = _apply_mapping(NhaCungCap.objects, SUPPLIER_NAME_MAP)
        brand_updated = _apply_mapping(ThuongHieu.objects, BRAND_NAME_MAP)
        chain_updated = _apply_mapping(ChuoiCuaHang.objects, CHAIN_NAME_MAP)
        store_updated = _apply_mapping(CuaHang.objects, STORE_NAME_MAP)
        promo_updated = _apply_mapping(KhuyenMai.objects, PROMO_NAME_MAP)
        staff_updated = _apply_field_normalizer(NhanVien.objects, "ho_ten", _normalize_name)
        staff_addr_updated = _apply_field_normalizer(NhanVien.objects, "dia_chi", _normalize_address)
        store_addr_updated = _apply_field_normalizer(CuaHang.objects, "dia_chi", _normalize_address)
        chain_desc_updated = _apply_text_mapping(ChuoiCuaHang.objects, "mo_ta", CHAIN_DESCRIPTION_MAP)

        self.stdout.write(
            self.style.SUCCESS(
                "Đã chuẩn hóa tiếng Việt: "
                f"{product_updated} sản phẩm, "
                f"{group_updated} nhóm, "
                f"{supplier_updated} nhà cung cấp, "
                f"{brand_updated} thương hiệu, "
                f"{chain_updated} chuỗi cửa hàng, "
                f"{store_updated} cửa hàng, "
                f"{promo_updated} khuyến mãi, "
                f"{staff_updated} nhân viên, "
                f"{staff_addr_updated} địa chỉ nhân viên, "
                f"{store_addr_updated} địa chỉ cửa hàng, "
                f"{chain_desc_updated} mô tả chuỗi cửa hàng."
            )
        )
