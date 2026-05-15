from xml.parsers.expat import errors

import os
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


def _runtime_upload_path(folder: str, filename: str) -> str:
    base_name = os.path.basename(filename or "upload.bin")
    stem, ext = os.path.splitext(base_name)
    safe_stem = stem or "upload"
    return f"runtime/{folder}/{safe_stem}_{uuid.uuid4().hex[:10]}{ext.lower()}"


def product_image_upload_to(instance, filename: str) -> str:
    return _runtime_upload_path("images", filename)


def about_image_upload_to(instance, filename: str) -> str:
    return _runtime_upload_path("about", filename)


def receipt_image_upload_to(instance, filename: str) -> str:
    return _runtime_upload_path("receipts", filename)


class ThuongHieu(models.Model):
    ten = models.CharField("Tên thương hiệu", max_length=50, unique=True)

    class Meta:
        verbose_name = "Thương hiệu"
        verbose_name_plural = "Thương hiệu"

    def __str__(self) -> str:
        return self.ten


class NhaCungCap(models.Model):
    ten = models.CharField("Tên nhà cung cấp", max_length=120)
    ghi_chu = models.TextField("Ghi chú", blank=True)

    class Meta:
        verbose_name = "Nhà cung cấp"
        verbose_name_plural = "Nhà cung cấp"

    def __str__(self) -> str:
        return self.ten


class NhomSanPham(models.Model):
    ten = models.CharField("Tên nhóm sản phẩm", max_length=80, unique=True)

    class Meta:
        verbose_name = "Nhóm sản phẩm"
        verbose_name_plural = "Nhóm sản phẩm"

    def __str__(self) -> str:
        return self.ten


class SanPham(models.Model):
    LOW_STOCK_THRESHOLD = 5

    ten = models.CharField("Tên sản phẩm", max_length=120)
    gia_ban = models.DecimalField(
        "Giá bán",
        max_digits=12,
        decimal_places=0,
        default=0,
    )
    ton_kho = models.PositiveIntegerField("Tồn kho", default=0)

    nhom_san_pham = models.ForeignKey(
        "NhomSanPham",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Nhóm sản phẩm",
    )

    nha_cung_cap = models.ForeignKey(
        "NhaCungCap",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Nhà cung cấp",
    )

    thuong_hieu = models.ForeignKey(
        "ThuongHieu",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Thương hiệu",
    )

    hinh_anh = models.ImageField(
        "Hình ảnh sản phẩm",
        upload_to=product_image_upload_to,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Sản phẩm"
        verbose_name_plural = "Sản phẩm"

    def __str__(self) -> str:
        return self.ten

    @property
    def stock_level(self) -> str:
        if self.ton_kho <= 0:
            return "out"
        if self.ton_kho <= self.LOW_STOCK_THRESHOLD:
            return "low"
        return "ok"

    @property
    def stock_label(self) -> str:
        if self.stock_level == "out":
            return "Hết hàng"
        if self.stock_level == "low":
            return f"Sắp hết ({self.ton_kho})"
        return f"Còn {self.ton_kho}"

    @property
    def stock_hint(self) -> str:
        if self.stock_level == "out":
            return "Sản phẩm đang hết hàng."
        if self.stock_level == "low":
            return f"Chỉ còn {self.ton_kho} sản phẩm trong kho."
        return f"Còn {self.ton_kho} sản phẩm trong kho."

    @property
    def is_low_stock(self) -> bool:
        return self.stock_level == "low"


class HinhAnhSanPham(models.Model):
    san_pham = models.ForeignKey(
        "SanPham",
        on_delete=models.CASCADE,
        related_name="hinh_anh_phu",
        verbose_name="Sản phẩm",
    )
    hinh_anh = models.ImageField(
        "Ảnh sản phẩm",
        upload_to=product_image_upload_to,
        null=True,
        blank=True,
    )
    chu_thich = models.CharField("Chú thích", max_length=150, blank=True)
    thu_tu = models.PositiveIntegerField("Thứ tự", default=0)

    class Meta:
        verbose_name = "Hình ảnh sản phẩm"
        verbose_name_plural = "Hình ảnh sản phẩm"
        ordering = ["thu_tu", "id"]

    def __str__(self) -> str:
        return f"{self.san_pham.ten} - ảnh {self.pk}"


class ChuoiCuaHang(models.Model):
    ten = models.CharField("Tên chuỗi cửa hàng", max_length=100)
    mo_ta = models.TextField("Mô tả", blank=True)

    logo = models.ImageField(
        "Logo chuỗi",
        upload_to="logo/",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Chuỗi cửa hàng"
        verbose_name_plural = "Chuỗi cửa hàng"

    def __str__(self) -> str:
        return self.ten


class CuaHang(models.Model):
    LATITUDE_VALIDATORS = [MinValueValidator(-90), MaxValueValidator(90)]
    LONGITUDE_VALIDATORS = [MinValueValidator(-180), MaxValueValidator(180)]

    chuoi = models.ForeignKey(
        "ChuoiCuaHang",
        on_delete=models.CASCADE,
        verbose_name="Chuỗi cửa hàng",
    )

    ten = models.CharField("Tên cửa hàng", max_length=100)
    dia_chi = models.CharField("Địa chỉ", max_length=255)
    quan_huyen = models.CharField("Quận/Huyện", max_length=50)

    vi_do = models.FloatField("Vĩ độ (lat)", validators=LATITUDE_VALIDATORS)
    kinh_do = models.FloatField("Kinh độ (lng)", validators=LONGITUDE_VALIDATORS)
    mo_cua = models.TimeField("Giờ mở cửa", null=True, blank=True)
    dong_cua = models.TimeField("Giờ đóng cửa", null=True, blank=True)
    hoat_dong_24h = models.BooleanField("Hoạt động 24h", default=False)

    san_pham = models.ManyToManyField(
        "SanPham",
        blank=True,
        verbose_name="Sản phẩm",
    )

    class Meta:
        verbose_name = "Cửa hàng"
        verbose_name_plural = "Cửa hàng"

    def __str__(self) -> str:
        return f"{self.ten} ({self.chuoi.ten})"


class NhanVien(models.Model):
    cua_hang = models.ForeignKey(
        "CuaHang",
        on_delete=models.CASCADE,
        verbose_name="Cửa hàng",
    )

    ho_ten = models.CharField("Họ và tên", max_length=120)
    chuc_vu = models.CharField("Chức vụ", max_length=50, blank=True)
    co_quyen_nhap_kho = models.BooleanField("Được nhập kho", default=True)

    so_dien_thoai = models.CharField(
        "Số điện thoại",
        max_length=15,
        blank=True,
    )

    email = models.EmailField(
        "Email",
        blank=True,
    )

    dia_chi = models.CharField(
        "Địa chỉ",
        max_length=255,
        blank=True,
    )

    avatar = models.ImageField(
        "Ảnh nhân viên",
        upload_to="avatar/",
        blank=True,
        null=True,
        default="avatar/default.jpg",
    )

    class Meta:
        verbose_name = "Nhân viên"
        verbose_name_plural = "Nhân viên"

    def __str__(self) -> str:
        return f"{self.ho_ten} - {self.cua_hang.ten}"


class KhuyenMai(models.Model):
    DISCOUNT_TYPE_CHOICES = (
        ("fixed", "Giảm số tiền"),
        ("percent", "Giảm theo phần trăm"),
    )

    ten = models.CharField("Tên khuyến mãi", max_length=150)
    ma_code = models.CharField("Mã voucher", max_length=50, unique=True, db_index=True, null=True, blank=True)
    mo_ta = models.TextField("Mô tả", blank=True)
    loai_giam = models.CharField(
        "Loại giảm giá",
        max_length=20,
        choices=DISCOUNT_TYPE_CHOICES,
        default="fixed",
    )
    gia_tri_giam = models.DecimalField("Giá trị giảm", max_digits=12, decimal_places=0, default=0)
    gia_tri_don_hang_toi_thieu = models.DecimalField("Đơn tối thiểu", max_digits=12, decimal_places=0, default=0)
    giam_toi_da = models.DecimalField("Giảm tối đa", max_digits=12, decimal_places=0, null=True, blank=True)
    dang_ap_dung = models.BooleanField("Đang áp dụng", default=True)
    ngay_bat_dau = models.DateTimeField("Bắt đầu", null=True, blank=True)
    ngay_ket_thuc = models.DateTimeField("Kết thúc", null=True, blank=True)

    thuong_hieu = models.ManyToManyField(
        "ThuongHieu",
        blank=True,
        verbose_name="Áp dụng cho thương hiệu",
    )

    cua_hang = models.ManyToManyField(
        "CuaHang",
        blank=True,
        verbose_name="Áp dụng cho cửa hàng",
    )

    class Meta:
        verbose_name = "Khuyến mãi"
        verbose_name_plural = "Khuyến mãi"

    def __str__(self) -> str:
        return f"{self.ten} ({self.ma_code})" if self.ma_code else self.ten


class Notification(models.Model):
    level = models.CharField("Mức độ", max_length=20, default="error")
    title = models.CharField("Tiêu đề", max_length=200)
    message = models.TextField("Nội dung", blank=True)
    path = models.CharField("Đường dẫn", max_length=255, blank=True)
    method = models.CharField("Phương thức", max_length=10, blank=True)
    status_code = models.IntegerField("Mã lỗi", null=True, blank=True)
    resolved = models.BooleanField("Đã xử lý", default=False)
    created_at = models.DateTimeField("Thời gian", auto_now_add=True)

    class Meta:
        verbose_name = "Thông báo"
        verbose_name_plural = "Thông báo"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.title} ({self.status_code or '-'})"


def _trash_expiry():
    retention_days = getattr(settings, "TRASH_RETENTION_DAYS", 15)
    return timezone.now() + timezone.timedelta(days=retention_days)


class TrashRecord(models.Model):
    model_label = models.CharField("Model", max_length=100)
    object_id = models.CharField("ID", max_length=64)
    data = models.JSONField("Dữ liệu")
    deleted_at = models.DateTimeField("Thời gian xóa", auto_now_add=True)
    expires_at = models.DateTimeField("Hết hạn", default=_trash_expiry)

    class Meta:
        verbose_name = "Thùng rác"
        verbose_name_plural = "Thùng rác"
        ordering = ["-deleted_at"]

    def __str__(self) -> str:
        return f"{self.model_label} {self.object_id}"


class HoSoKhachHang(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ho_so_khach_hang",
        verbose_name="Tài khoản",
    )
    avatar = models.ImageField("Ảnh đại diện", upload_to="avatar/customers/", blank=True, null=True)
    so_dien_thoai = models.CharField("Số điện thoại", max_length=20, blank=True)
    dia_chi = models.CharField("Địa chỉ", max_length=255, blank=True)

    class Meta:
        verbose_name = "Hồ sơ khách hàng"
        verbose_name_plural = "Hồ sơ khách hàng"

    def __str__(self) -> str:
        return f"Hồ sơ {self.user.username}"


class DanhGiaCuaHang(models.Model):
    SO_SAO_VALIDATORS = [MinValueValidator(1), MaxValueValidator(5)]

    cua_hang = models.ForeignKey(
        "CuaHang",
        on_delete=models.CASCADE,
        related_name="danh_gia",
        verbose_name="Cửa hàng",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="danh_gia_cua_hang",
        verbose_name="Người dùng",
    )
    so_sao = models.PositiveSmallIntegerField("Số sao", validators=SO_SAO_VALIDATORS)
    binh_luan = models.TextField("Bình luận", blank=True)
    created_at = models.DateTimeField("Thời gian tạo", auto_now_add=True)
    updated_at = models.DateTimeField("Cập nhật lúc", auto_now=True)

    class Meta:
        verbose_name = "Đánh giá cửa hàng"
        verbose_name_plural = "Đánh giá cửa hàng"
        ordering = ["-created_at", "-id"]

        constraints = [
            models.UniqueConstraint(
                fields=["user", "cua_hang"],
                name="unique_user_store_review"
            )
        ]

    def __str__(self) -> str:
        return f"{self.cua_hang.ten} - {self.user.username} - {self.so_sao} sao"

class TepDanhGiaCuaHang(models.Model):
    LOAI_CHOICES = (
        ("image", "Hình ảnh"),
        ("video", "Video"),
    )

    danh_gia = models.ForeignKey(
        "DanhGiaCuaHang",
        on_delete=models.CASCADE,
        related_name="tep_dinh_kem",
        verbose_name="Đánh giá",
    )
    tep = models.FileField("Tệp", upload_to="reviews/")
    loai = models.CharField("Loại tệp", max_length=10, choices=LOAI_CHOICES)
    created_at = models.DateTimeField("Thời gian tạo", auto_now_add=True)

    class Meta:
        verbose_name = "Tệp đánh giá cửa hàng"
        verbose_name_plural = "Tệp đánh giá cửa hàng"
        ordering = ["created_at", "id"]

    def __str__(self) -> str:
        return f"{self.get_loai_display()} - đánh giá {self.danh_gia_id}"


class DiaChiKhachHang(models.Model):
    LOAI_DIA_CHI_CHOICES = (
        ("home", "Nhà riêng"),
        ("office", "Văn phòng"),
        ("other", "Khác"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="dia_chi_khach_hang",
        verbose_name="Tài khoản",
    )
    ho_ten_nguoi_nhan = models.CharField("Họ tên người nhận", max_length=120)
    so_dien_thoai = models.CharField("Số điện thoại", max_length=20)
    tinh_thanh = models.CharField("Tỉnh/Thành phố", max_length=120, blank=True)
    quan_huyen = models.CharField("Quận/Huyện", max_length=120, blank=True)
    phuong_xa = models.CharField("Khu vực", max_length=120, blank=True)
    dia_chi_cu_the = models.CharField("Địa chỉ cụ thể", max_length=255)
    vi_do = models.FloatField(
        "Vĩ độ giao hàng",
        null=True,
        blank=True,
        validators=CuaHang.LATITUDE_VALIDATORS,
    )
    kinh_do = models.FloatField(
        "Kinh độ giao hàng",
        null=True,
        blank=True,
        validators=CuaHang.LONGITUDE_VALIDATORS,
    )
    loai_dia_chi = models.CharField(
        "Loại địa chỉ",
        max_length=20,
        choices=LOAI_DIA_CHI_CHOICES,
        default="home",
    )
    mac_dinh = models.BooleanField("Địa chỉ mặc định", default=False)
    created_at = models.DateTimeField("Thời gian tạo", auto_now_add=True)

    class Meta:
        verbose_name = "Địa chỉ khách hàng"
        verbose_name_plural = "Địa chỉ khách hàng"
        ordering = ["-mac_dinh", "-created_at", "-id"]

    def __str__(self) -> str:
        return f"{self.user.username} - {self.ho_ten_nguoi_nhan}"

    @property
    def dia_chi_day_du(self) -> str:
        parts = [
            (self.dia_chi_cu_the or "").strip(),
            (self.phuong_xa or "").strip(),
            (self.quan_huyen or "").strip(),
            (self.tinh_thanh or "").strip(),
        ]
        return ", ".join(part for part in parts if part)

    @property
    def has_coordinates(self) -> bool:
        return self.vi_do is not None and self.kinh_do is not None


class GopYKhachHang(models.Model):
    ho_ten = models.CharField("Họ tên", max_length=120)
    email = models.EmailField("Email")
    so_dien_thoai = models.CharField("Số điện thoại", max_length=20, blank=True)
    chu_de = models.CharField("Chủ đề", max_length=150)
    noi_dung = models.TextField("Nội dung góp ý")
    da_phan_hoi = models.BooleanField("Đã phản hồi", default=False)
    created_at = models.DateTimeField("Thời gian tạo", auto_now_add=True)

    class Meta:
        verbose_name = "Góp ý khách hàng"
        verbose_name_plural = "Góp ý khách hàng"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.ho_ten} - {self.chu_de}"


class TrangGioiThieu(models.Model):
    tieu_de = models.CharField("Tiêu đề", max_length=180, default="Giới thiệu hệ thống")
    mo_ta_ngan = models.TextField("Mô tả ngắn", blank=True)
    noi_dung = models.TextField("Nội dung", blank=True)
    anh_bia = models.ImageField("Ảnh bìa", upload_to=about_image_upload_to, null=True, blank=True)
    anh_noi_dung_1 = models.ImageField("Ảnh nội dung 1", upload_to=about_image_upload_to, null=True, blank=True)
    anh_noi_dung_2 = models.ImageField("Ảnh nội dung 2", upload_to=about_image_upload_to, null=True, blank=True)
    anh_noi_dung_3 = models.ImageField("Ảnh nội dung 3", upload_to=about_image_upload_to, null=True, blank=True)
    cap_nhat_luc = models.DateTimeField("Cập nhật lúc", auto_now=True)

    class Meta:
        verbose_name = "Trang giới thiệu"
        verbose_name_plural = "Trang giới thiệu"

    def __str__(self) -> str:
        return self.tieu_de or "Trang giới thiệu"


class TrangGioiThieuHinhAnh(models.Model):
    trang = models.ForeignKey(
        "TrangGioiThieu",
        on_delete=models.CASCADE,
        related_name="hinh_anh_phu",
        verbose_name="Trang giới thiệu",
    )
    nhom = models.CharField("Nhóm ảnh", max_length=50, blank=True, db_index=True)
    tieu_de = models.CharField("Tiêu đề ảnh", max_length=150, blank=True)
    hinh_anh = models.ImageField("Hình ảnh", upload_to=about_image_upload_to)
    chu_thich = models.CharField("Chú thích", max_length=150, blank=True)
    thu_tu = models.PositiveIntegerField("Thứ tự", default=0)

    class Meta:
        verbose_name = "Ảnh trang giới thiệu"
        verbose_name_plural = "Ảnh trang giới thiệu"
        ordering = ["thu_tu", "id"]

    def __str__(self) -> str:
        return self.tieu_de or f"{self.trang.tieu_de} - ảnh {self.pk}"


class DonHang(models.Model):
    STATUS_CHOICES = (
        ("pending", "Chờ xử lý"),
        ("confirmed", "Đã xác nhận"),
        ("shipping", "Đang giao"),
        ("delivered", "Đã giao"),
        ("done", "Hoàn tất"),
        ("cancelled", "Đã hủy"),
    )
    PAYMENT_METHOD_CHOICES = (
        ("cod", "Thanh toán khi nhận hàng"),
        ("bank_transfer", "Chuyển khoản ngân hàng"),
        ("momo", "Ví MoMo"),
        ("ewallet", "Ví điện tử"),
    )
    PAYMENT_STATUS_CHOICES = (
        ("unpaid", "Chưa thanh toán"),
        ("paid", "Đã thanh toán"),
        ("awaiting_confirmation", "Chờ xác nhận chuyển khoản"),
        ("refunded", "Hoàn tiền"),
    )

    khach_hang = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Khách hàng",
    )
    ho_ten_nguoi_nhan = models.CharField("Họ tên người nhận", max_length=120)
    so_dien_thoai = models.CharField("Số điện thoại", max_length=20)
    dia_chi_giao_hang = models.CharField("Địa chỉ giao hàng", max_length=255)
    vi_do_giao_hang = models.FloatField(
        "Vĩ độ giao hàng",
        null=True,
        blank=True,
        validators=CuaHang.LATITUDE_VALIDATORS,
    )
    kinh_do_giao_hang = models.FloatField(
        "Kinh độ giao hàng",
        null=True,
        blank=True,
        validators=CuaHang.LONGITUDE_VALIDATORS,
    )
    ghi_chu = models.TextField("Ghi chú", blank=True)
    trang_thai = models.CharField("Trạng thái", max_length=20, choices=STATUS_CHOICES, default="pending")
    phuong_thuc_thanh_toan = models.CharField(
        "Phương thức thanh toán",
        max_length=30,
        choices=PAYMENT_METHOD_CHOICES,
        default="cod",
    )
    trang_thai_thanh_toan = models.CharField(
        "Trạng thái thanh toán",
        max_length=30,
        choices=PAYMENT_STATUS_CHOICES,
        default="unpaid",
    )
    tong_so_luong = models.PositiveIntegerField("Tổng số lượng", default=0)
    tong_tien_truoc_giam = models.DecimalField("Tổng tiền trước giảm", max_digits=12, decimal_places=0, default=0)
    giam_gia = models.DecimalField("Giảm giá", max_digits=12, decimal_places=0, default=0)
    tong_tien = models.DecimalField("Tổng tiền", max_digits=12, decimal_places=0, default=0)
    cua_hang_xu_ly = models.ForeignKey(
        "CuaHang",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="don_hang_xu_ly",
        verbose_name="Cửa hàng xử lý",
    )
    khuyen_mai = models.ForeignKey(
        "KhuyenMai",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="don_hang",
        verbose_name="Voucher áp dụng",
    )
    ma_voucher_ap_dung = models.CharField("Mã voucher áp dụng", max_length=50, blank=True)
    anh_bien_lai = models.ImageField(
        "Ảnh biên lai chuyển khoản",
        upload_to=receipt_image_upload_to,
        null=True,
        blank=True,
    )
    ma_giao_dich_thanh_toan = models.CharField("Mã giao dịch thanh toán", max_length=120, blank=True)
    thoi_gian_gui_bien_lai = models.DateTimeField("Thời gian gửi biên lai", null=True, blank=True)
    created_at = models.DateTimeField("Thời gian tạo", auto_now_add=True)

    class Meta:
        verbose_name = "Đơn hàng"
        verbose_name_plural = "Đơn hàng"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Đơn hàng {self.pk} - {self.khach_hang.username}"


class ChiTietDonHang(models.Model):
    don_hang = models.ForeignKey(
        "DonHang",
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Đơn hàng",
    )
    san_pham = models.ForeignKey(
        "SanPham",
        on_delete=models.CASCADE,
        verbose_name="Sản phẩm",
    )
    so_luong = models.PositiveIntegerField("Số lượng", default=1)
    don_gia = models.DecimalField("Đơn giá", max_digits=12, decimal_places=0, default=0)

    class Meta:
        verbose_name = "Chi tiết đơn hàng"
        verbose_name_plural = "Chi tiết đơn hàng"

    def __str__(self) -> str:
        return f"{self.san_pham.ten} x {self.so_luong}"


class XacNhanThanhToan(models.Model):
    ACTION_CHOICES = (
        ("submitted", "Đã gửi biên lai"),
        ("approved", "Đã duyệt biên lai"),
        ("rejected", "Đã từ chối biên lai"),
    )

    don_hang = models.ForeignKey(
        "DonHang",
        on_delete=models.CASCADE,
        related_name="lich_su_xac_nhan_thanh_toan",
        verbose_name="Đơn hàng",
    )
    hanh_dong = models.CharField(
        "Hành động",
        max_length=20,
        choices=ACTION_CHOICES,
    )
    ghi_chu = models.TextField("Ghi chú", blank=True)
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="xac_nhan_thanh_toan_da_thuc_hien",
        verbose_name="Người thực hiện",
    )
    created_at = models.DateTimeField("Thời gian tạo", auto_now_add=True)

    class Meta:
        verbose_name = "Xác nhận thanh toán"
        verbose_name_plural = "Xác nhận thanh toán"
        ordering = ["-created_at", "-id"]

    def __str__(self) -> str:
        return f"Đơn #{self.don_hang_id} - {self.get_hanh_dong_display()}"


class TonKhoCuaHang(models.Model):
    cua_hang = models.ForeignKey(
        "CuaHang",
        on_delete=models.CASCADE,
        related_name="ton_kho_san_pham",
        verbose_name="Cửa hàng",
    )
    san_pham = models.ForeignKey(
        "SanPham",
        on_delete=models.CASCADE,
        related_name="ton_kho_theo_cua_hang",
        verbose_name="Sản phẩm",
    )
    ton_kho = models.PositiveIntegerField("Tồn kho", default=0)
    updated_at = models.DateTimeField("Cập nhật lúc", auto_now=True)

    class Meta:
        verbose_name = "Tồn kho cửa hàng"
        verbose_name_plural = "Tồn kho cửa hàng"
        ordering = ["cua_hang__ten", "san_pham__ten"]
        constraints = [
            models.UniqueConstraint(
                fields=["cua_hang", "san_pham"],
                name="uniq_store_product_stock",
            )
        ]

    def __str__(self) -> str:
        return f"{self.cua_hang.ten} - {self.san_pham.ten}: {self.ton_kho}"


def _movement_signed_quantity(movement) -> int:
    return movement.so_luong if movement.loai == "import" else -movement.so_luong


def _validate_inventory_sequence(product, *, candidate=None, exclude_id=None):
    if product is None:
        return

    movements = list(
        GiaoDichKho.objects.filter(san_pham=product)
        .exclude(pk=exclude_id)
        .order_by("created_at", "id")
    )
    if candidate is not None:
        movements.append(candidate)
        movements.sort(
            key=lambda item: (
                item.created_at or timezone.now(),
                item.pk or 10**12,
            )
        )

    running = 0
    for movement in movements:
        delta = _movement_signed_quantity(movement)
        if running + delta < 0:
            raise ValidationError(
                {
                    "so_luong": (
                        f"Giao dịch '{movement}' làm tồn kho của {product.ten} bị âm."
                    )
                }
            )
        running += delta


def _validate_store_inventory_sequence(store, product, *, candidate=None, exclude_id=None):
    if store is None or product is None:
        return

    movements = list(
        GiaoDichKho.objects.filter(san_pham=product, cua_hang=store)
        .exclude(pk=exclude_id)
        .order_by("created_at", "id")
    )
    if candidate is not None and candidate.cua_hang_id == getattr(store, "pk", store) and candidate.san_pham_id == getattr(product, "pk", product):
        movements.append(candidate)
        movements.sort(
            key=lambda item: (
                item.created_at or timezone.now(),
                item.pk or 10**12,
            )
        )

    running = 0
    for movement in movements:
        delta = _movement_signed_quantity(movement)
        if running + delta < 0:
            raise ValidationError(
                {
                    "so_luong": (
                        f"Giao dịch '{movement}' làm tồn kho của {product.ten} tại {store.ten} bị âm."
                    )
                }
            )
        running += delta


def sync_product_stock(product):
    if product is None:
        return 0

    running = 0
    movement_rows = []
    movements = list(
        GiaoDichKho.objects.filter(san_pham=product).order_by("created_at", "id")
    )
    for movement in movements:
        ton_truoc = running
        running += _movement_signed_quantity(movement)
        movement_rows.append((movement.pk, ton_truoc, running))

    for movement_id, ton_truoc, ton_sau in movement_rows:
        GiaoDichKho.objects.filter(pk=movement_id).update(
            ton_truoc=ton_truoc,
            ton_sau=ton_sau,
        )

    if product.ton_kho != running:
        SanPham.objects.filter(pk=product.pk).update(ton_kho=running)
        product.ton_kho = running
    return running


def sync_store_stock(product, store):
    if product is None or store is None:
        return 0

    running = 0
    movements = list(
        GiaoDichKho.objects.filter(san_pham=product, cua_hang=store).order_by("created_at", "id")
    )
    for movement in movements:
        running += _movement_signed_quantity(movement)

    stock_row, _ = TonKhoCuaHang.objects.get_or_create(
        cua_hang=store,
        san_pham=product,
        defaults={"ton_kho": running},
    )
    if stock_row.ton_kho != running:
        TonKhoCuaHang.objects.filter(pk=stock_row.pk).update(ton_kho=running)
        stock_row.ton_kho = running
    return running


class GiaoDichKho(models.Model):
    TYPE_CHOICES = (
        ("import", "Nhập kho"),
        ("export", "Xuất kho"),
    )

    san_pham = models.ForeignKey(
        "SanPham",
        on_delete=models.CASCADE,
        related_name="giao_dich_kho",
        verbose_name="Sản phẩm",
    )
    cua_hang = models.ForeignKey(
        "CuaHang",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="giao_dich_kho",
        verbose_name="Cửa hàng",
    )
    nhan_vien = models.ForeignKey(
        "NhanVien",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="giao_dich_kho",
        verbose_name="Nhân viên ký",
    )
    loai = models.CharField("Loại giao dịch", max_length=20, choices=TYPE_CHOICES)
    so_luong = models.PositiveIntegerField("Số lượng", default=1)
    ton_truoc = models.PositiveIntegerField("Tồn trước", default=0, editable=False)
    ton_sau = models.PositiveIntegerField("Tồn sau", default=0, editable=False)
    don_hang = models.ForeignKey(
        "DonHang",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="giao_dich_kho",
        verbose_name="Đơn hàng liên quan",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="giao_dich_kho_da_tao",
        verbose_name="Người tạo",
    )
    ghi_chu = models.TextField("Ghi chú", blank=True)
    chu_ky = models.ImageField(
        "Chữ ký nhân viên",
        upload_to="signatures/",
        null=True,
        blank=True,
    )
    signed_at = models.DateTimeField("Thời gian ký", null=True, blank=True)
    signed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="giao_dich_kho_da_ky",
        verbose_name="Người ký",
    )
    signed_ip = models.CharField("IP ký", max_length=45, blank=True)
    signed_user_agent = models.CharField("Trình duyệt ký", max_length=255, blank=True)
    otp_code_hash = models.CharField("Mã OTP (hash)", max_length=128, blank=True)
    otp_expires_at = models.DateTimeField("Hết hạn OTP", null=True, blank=True)
    otp_verified_at = models.DateTimeField("Xác nhận OTP lúc", null=True, blank=True)
    otp_verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="giao_dich_kho_xac_nhan_otp",
        verbose_name="Người xác nhận OTP",
    )
    otp_verified_ip = models.CharField("IP xác nhận OTP", max_length=45, blank=True)
    otp_verified_user_agent = models.CharField("Trình duyệt xác nhận OTP", max_length=255, blank=True)
    otp_recipient_email = models.EmailField("Email nhận OTP", blank=True)
    created_at = models.DateTimeField("Thời gian tạo", auto_now_add=True)

    class Meta:
        verbose_name = "Giao dịch kho"
        verbose_name_plural = "Giao dịch kho"
        ordering = ["-created_at", "-id"]

    def __str__(self) -> str:
        store_suffix = f" @ {self.cua_hang.ten}" if self.cua_hang_id else ""
        return f"{self.get_loai_display()} - {self.san_pham.ten} x {self.so_luong}{store_suffix}"

    def clean(self):
        super().clean()
        if self.so_luong <= 0:
            raise ValidationError({"so_luong": "Số lượng phải lớn hơn 0."})
        if self.nhan_vien_id and self.nhan_vien and self.nhan_vien.cua_hang_id:
            if self.cua_hang_id and self.cua_hang_id != self.nhan_vien.cua_hang_id:
                raise ValidationError({"cua_hang": "Cửa hàng của giao dịch phải trùng với cửa hàng của nhân viên ký."})
            if not self.cua_hang_id:
                self.cua_hang = self.nhan_vien.cua_hang
        if self.loai == "export" and not self.cua_hang_id:
            if self.don_hang_id and self.don_hang and self.don_hang.cua_hang_xu_ly_id:
                self.cua_hang = self.don_hang.cua_hang_xu_ly
            else:
                raise ValidationError({"cua_hang": "Phiếu xuất kho cần gắn với một cửa hàng."})
        if self.loai == "import":
            errors = {}
            if not self.nhan_vien_id:
                errors["nhan_vien"] = "Phiếu nhập kho cần chọn nhân viên ký."
            elif self.nhan_vien and not self.nhan_vien.co_quyen_nhap_kho:
                errors["nhan_vien"] = "Nhân viên này không được quyền nhập kho."
            if not self.chu_ky and not getattr(self, "_skip_signature", False):
                errors["chu_ky"] = "Phiếu nhập kho cần có chữ ký nhân viên."
            if errors:
                raise ValidationError(errors)
        if not self.san_pham_id:
            return
        _validate_inventory_sequence(
            self.san_pham,
            candidate=self,
            exclude_id=self.pk,
        )
        if self.cua_hang_id:
            _validate_store_inventory_sequence(
                self.cua_hang,
                self.san_pham,
                candidate=self,
                exclude_id=self.pk,
            )

    def save(self, *args, **kwargs):
        old_store_id = None
        if self.pk:
            old_store_id = (
                GiaoDichKho.objects.filter(pk=self.pk)
                .values_list("cua_hang_id", flat=True)
                .first()
            )
        self.full_clean()
        super().save(*args, **kwargs)
        sync_product_stock(self.san_pham)
        if old_store_id and old_store_id != self.cua_hang_id:
            old_store = CuaHang.objects.filter(pk=old_store_id).first()
            if old_store:
                sync_store_stock(self.san_pham, old_store)
        if self.cua_hang_id:
            sync_store_stock(self.san_pham, self.cua_hang)

    def delete(self, *args, **kwargs):
        product = self.san_pham
        store = self.cua_hang
        _validate_inventory_sequence(product, exclude_id=self.pk)
        if store is not None:
            _validate_store_inventory_sequence(store, product, exclude_id=self.pk)
        result = super().delete(*args, **kwargs)
        sync_product_stock(product)
        if store is not None:
            sync_store_stock(product, store)
        return result


class TonKhoAudit(models.Model):
    ACTION_CHOICES = (
        ("create", "Tạo giao dịch"),
        ("update", "Cập nhật giao dịch"),
        ("delete", "Xóa giao dịch"),
    )

    giao_dich = models.ForeignKey(
        "GiaoDichKho",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
        verbose_name="Giao dịch kho",
    )
    san_pham = models.ForeignKey(
        "SanPham",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
        verbose_name="Sản phẩm",
    )
    cua_hang = models.ForeignKey(
        "CuaHang",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
        verbose_name="Cửa hàng",
    )
    loai = models.CharField("Loại giao dịch", max_length=20, choices=GiaoDichKho.TYPE_CHOICES)
    so_luong = models.PositiveIntegerField("Số lượng", default=0)
    ton_truoc = models.IntegerField("Tồn trước", default=0)
    ton_sau = models.IntegerField("Tồn sau", default=0)
    hanh_dong = models.CharField("Hành động", max_length=20, choices=ACTION_CHOICES)
    ly_do = models.TextField("Lý do", blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ton_kho_audit_logs",
        verbose_name="Người thao tác",
    )
    created_at = models.DateTimeField("Thời gian", auto_now_add=True)

    class Meta:
        verbose_name = "Nhật ký tồn kho"
        verbose_name_plural = "Nhật ký tồn kho"
        ordering = ["-created_at", "-id"]

    def __str__(self) -> str:
        target = self.san_pham.ten if self.san_pham_id else "Sản phẩm"
        return f"{self.get_hanh_dong_display()} - {target}"
