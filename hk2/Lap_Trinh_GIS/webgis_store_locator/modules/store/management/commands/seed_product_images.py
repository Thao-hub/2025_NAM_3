from pathlib import Path

from django.core.management.base import BaseCommand

from modules.store.models import SanPham


IMAGE_MAPPING = {
    ("Froster Cầu Vồng (Size L)", "Froster Cau Vong (Size L)"): "froster_cau_vong.jpg",
    ("Mì Trộn Indomie Trứng Ốp La Xúc Xích", "Mi Tron Indomie Trung Op La Xuc Xich"): "mi_tron_indomio_trung_op_la_xuc_xich_1.jpg",
    ("Bánh Bao Trứng Muối (Hấp nóng)", "Banh Bao Trung Muoi (Hap nong)"): "BB_Trung_Muoi_1.jpg",
    ("Bánh Mì Ốp La 2 Trứng", "Banh Mi Op La 2 Trung"): "BM_Op_La_2Trung_1.jpg",
    ("Cà Phê Bạc Xỉu Đá (Ly lớn)", "Ca Phe Bac Xiu Da (Ly lon)"): "CF_Bac_Xiu.jpg",
    ("Xôi Lá Chuối (Thịt Kho Tàu)", "Xoi La Chuoi (Thit Kho Tau)"): "xoi_la_chuoi_thit_kho_tau_1.jpg",
    ("Tokbokki Xúc Xích Sốt Cay (Ly)", "Tokbokki Xuc Xich Sot Cay (Ly)"): "tokbokki_xuc_xich_sot_cay_ly_2.jpg",
    ("Nước Ép Dưa Hấu Youus 230ml", "Nuoc Ep Dua Hau Youus 230ml"): "nuoc_ep_dua_hau_youus_1.jpg",
    ("Sandwich Inkigayo",): "sandwich_inkigayo_1.jpg",
    ("Bắp Rang Bơ Vị Phô Mai Youus", "Bap Rang Bo Vi Pho Mai Youus"): "bap_rang_bo_pho_mai_youus_1.jpg",
    ("Lẩu Chả Cá Omok (Ly)", "Lau Cha Ca Omok (Ly)"): "lau_cha_ca_omok_ly.jpg",
    ("Cơm Nắm Tôm Mayonnaise", "Com Nam Tom Mayonnaise"): "C_Nam_Tom_my.jpg",
    ("Mì Hảo Hảo Tôm Chua Cay (Gói)", "Mi Hao Hao Tom Chua Cay (Goi)"): "mi_hao_hao_tom_chua_cay.jpg",
    ("Mì Ly Modern Lẩu Thái Tôm", "Mi Ly Modern Lau Thai Tom"): "mi_ly_modern_lau_thai_tom_1.jpg",
    ("Nước Ngọt Coca-Cola Zero 320ml", "Nuoc Ngot Coca-Cola Zero 320ml"): "caca_zero_1.jpg",
    ("Nước Tăng Lực Sting Dâu 330ml", "Nuoc Tang Luc Sting Dau 330ml"): "sting_dau_1.jpg",
    ("Nước Tinh Khiết Aquafina 500ml", "Nuoc Tinh Khiet Aquafina 500ml"): "aquafina_1.jpg",
    ("Snack Khoai Tây O'Star Vị Kim Chi 63g", "Snack Khoai Tay O'Star Vi Kim Chi 63g"): "ostar_kimchi_1.jpg",
    ("Sữa Tươi TH True Milk Có Đường 180ml", "Sua Tuoi TH True Milk Co Duong 180ml"): "TH_180_co_duong_1.jpg",
}


class Command(BaseCommand):
    help = "Gán ảnh sản phẩm từ thư mục media/images vào các bản ghi sản phẩm."

    def add_arguments(self, parser):
        parser.add_argument(
            "--source-dir",
            default="media/images",
            help="Thư mục chứa ảnh sản phẩm, mặc định là media/images",
        )

    def handle(self, *args, **options):
        source_dir = Path(options["source_dir"])
        updated = 0
        missing = []

        for product_names, filename in IMAGE_MAPPING.items():
            image_path = source_dir / filename
            if not image_path.exists():
                missing.append(filename)
                continue

            updated += SanPham.objects.filter(ten__in=product_names).update(hinh_anh=f"images/{filename}")

        self.stdout.write(self.style.SUCCESS(f"Đã cập nhật {updated} ảnh sản phẩm."))
        if missing:
            self.stdout.write(self.style.WARNING(f"Thiếu {len(missing)} file ảnh: {', '.join(missing)}"))
