from django.conf import settings
from django.apps import apps
from django.contrib import admin
from django.contrib.admin.sites import NotRegistered
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.urls import reverse
from django.utils.html import format_html
from django.utils.text import capfirst
from django import forms
from decimal import Decimal

from .models import (
    ThuongHieu,
    NhaCungCap,
    NhomSanPham,
    SanPham,
    GiaoDichKho,
    HinhAnhSanPham,
    ChuoiCuaHang,
    CuaHang,
    NhanVien,
    KhuyenMai,
    HoSoKhachHang,
    DanhGiaCuaHang,
    TepDanhGiaCuaHang,
    DiaChiKhachHang,
    DonHang,
    ChiTietDonHang,
    TonKhoCuaHang,
    TonKhoAudit,
)


class StockLevelFilter(admin.SimpleListFilter):
    title = "Tồn kho"
    parameter_name = "stock_level"

    def lookups(self, request, model_admin):
        return (
            ("out", "Hết hàng"),
            ("low", "Sắp hết"),
            ("ok", "Ổn định"),
        )

    def queryset(self, request, queryset):
        value = self.value()
        threshold = SanPham.LOW_STOCK_THRESHOLD
        queryset = queryset.annotate(
            store_stock_total=Coalesce(Sum("ton_kho_theo_cua_hang__ton_kho"), 0)
        )
        if value == "out":
            return queryset.filter(store_stock_total__lte=0)
        if value == "low":
            return queryset.filter(store_stock_total__gt=0, store_stock_total__lte=threshold)
        if value == "ok":
            return queryset.filter(store_stock_total__gt=threshold)
        return queryset


def _img(field_file, size: int = 42, media_fallback: str | None = None):
    url = ""

    try:
        if field_file and getattr(field_file, "name", ""):
            url = field_file.url
    except Exception:
        url = ""

    if not url and media_fallback:
        url = settings.MEDIA_URL + media_fallback.lstrip("/")

    if not url:
        return "-"

    return format_html(
        '<img src="{}" loading="lazy" '
        'style="width:{}px;height:{}px;object-fit:cover;'
        'border-radius:10px;border:1px solid rgba(255,255,255,.18);" />',
        url,
        size,
        size,
    )



def _vi_permission_action(name: str) -> str:
    mapping = (
        ("Can add ", "Có thể thêm "),
        ("Can change ", "Có thể sửa "),
        ("Can delete ", "Có thể xóa "),
        ("Can view ", "Có thể xem "),
    )
    for src, dst in mapping:
        if name.startswith(src):
            return dst + name[len(src):]
    return name


def _app_verbose_name(app_label: str) -> str:
    try:
        return apps.get_app_config(app_label).verbose_name
    except LookupError:
        return app_label


class UserAdminViChangeForm(UserChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        rename = {
            "first_name": "Tên",
            "last_name": "Họ",
            "email": "Địa chỉ email",
        }
        for field_name, label in rename.items():
            field = self.fields.get(field_name)
            if field is not None:
                field.label = label

        password_field = self.fields.get("password")
        if password_field is not None and self.instance and self.instance.pk:
            reset_url = reverse("admin:auth_user_password_change", args=(self.instance.pk,))
            password_field.help_text = format_html(
                "Mật khẩu gốc không được lưu nên không thể xem lại mật khẩu hiện tại. "
                "Bạn có thể đổi mật khẩu bằng <a href=\"{}\">biểu mẫu này</a>.",
                reset_url,
            )

        groups_field = self.fields.get("groups")
        if groups_field is not None:
            groups_field.help_text = (
                "Người dùng sẽ nhận toàn bộ quyền của các nhóm được chọn. "
                "Giữ phím Ctrl/Command để chọn nhiều mục."
            )

        perms_field = self.fields.get("user_permissions")
        if perms_field is not None:
            perms_field.help_text = (
                "Quyền riêng được cấp trực tiếp cho người dùng. "
                "Giữ phím Ctrl/Command để chọn nhiều mục."
            )

            def _permission_label(obj):
                app_name = _app_verbose_name(obj.content_type.app_label)
                model_cls = obj.content_type.model_class()
                model_name = model_cls._meta.verbose_name if model_cls else obj.content_type.model
                action_name = _vi_permission_action(obj.name)
                return f"{capfirst(app_name)} | {capfirst(model_name)} | {action_name}"

            perms_field.label_from_instance = _permission_label


class UserAdminVi(DjangoUserAdmin):
    form = UserAdminViChangeForm

class CuaHangAdminForm(forms.ModelForm):
    class Meta:
        model = CuaHang
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in ("vi_do", "kinh_do"):
            field = self.fields.get(field_name)
            if field is not None:
                field.widget.attrs["readonly"] = "readonly"
                field.widget.attrs["title"] = "T\u1ecda \u0111\u1ed9 ch\u1ec9 \u0111\u01b0\u1ee3c l\u1ea5y t\u1eeb b\u1ea3n \u0111\u1ed3."
        san_pham_field = self.fields.get("san_pham")
        if san_pham_field is not None:
            san_pham_field.help_text = (
                "T\u00ecm nhanh v\u00e0 ch\u1ecdn theo ch\u1ebf \u0111\u1ed9 Ch\u1ecdn 1/Ch\u1ecdn nhi\u1ec1u b\u00ean d\u01b0\u1edbi danh s\u00e1ch."
            )

    def clean(self):
        cleaned = super().clean()
        lat = cleaned.get("vi_do")
        lon = cleaned.get("kinh_do")
        source = (self.data.get("_coord_from_map") or "").strip()

        changed = not bool(self.instance and self.instance.pk)

        if self.instance and self.instance.pk and lat is not None and lon is not None:
            old_lat = float(self.instance.vi_do)
            old_lon = float(self.instance.kinh_do)
            changed = abs(float(lat) - old_lat) > 1e-12 or abs(float(lon) - old_lon) > 1e-12

        if changed and source != "map":
            message = "C\u1ea7n ch\u1ed1t t\u1ecda \u0111\u1ed9 b\u1eb1ng c\u00e1ch click tr\u00ean b\u1ea3n \u0111\u1ed3 tr\u01b0\u1edbc khi l\u01b0u."
            self.add_error("vi_do", message)
            self.add_error("kinh_do", message)

        return cleaned


class KhuyenMaiAdminForm(forms.ModelForm):
    class Meta:
        model = KhuyenMai
        fields = "__all__"
        widgets = {
            "ma_code": forms.TextInput(
                attrs={
                    "placeholder": "Ví dụ: GIAM10 hoặc ONLINE50K",
                    "style": "text-transform:uppercase;",
                }
            ),
            "ten": forms.TextInput(attrs={"placeholder": "Ví dụ: Giảm 10% đơn online tháng này"}),
            "mo_ta": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Mô tả ngắn điều kiện áp dụng để admin khác dễ hiểu khi kiểm tra lại.",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["ma_code"].help_text = "Mã khách nhập ở checkout. Nên viết in hoa, không dấu, không khoảng trắng."
        self.fields["loai_giam"].help_text = "Chọn đúng kiểu giảm: phần trăm hoặc số tiền cố định."
        self.fields["gia_tri_giam"].help_text = "Nếu là phần trăm thì nhập 1-100. Nếu là tiền mặt thì nhập số tiền VND."
        self.fields["gia_tri_don_hang_toi_thieu"].help_text = "Đơn hàng phải đạt tối thiểu mức này mới dùng được voucher."
        self.fields["giam_toi_da"].help_text = "Chỉ nên nhập khi giảm theo phần trăm."
        self.fields["ngay_bat_dau"].help_text = "Để trống nếu muốn voucher có hiệu lực ngay."
        self.fields["ngay_ket_thuc"].help_text = "Để trống nếu chưa muốn giới hạn ngày hết hạn."
        self.fields["dang_ap_dung"].help_text = "Bỏ chọn để tạm khóa voucher mà vẫn giữ lại lịch sử cấu hình."
        self.fields["thuong_hieu"].help_text = "Nếu chọn thương hiệu, voucher chỉ áp dụng cho sản phẩm thuộc các thương hiệu này."
        self.fields["cua_hang"].help_text = "Nếu chọn cửa hàng, voucher sẽ được xem là ưu đãi tại cửa hàng và không áp dụng cho checkout online."

    def clean_ma_code(self):
        code = "".join((self.cleaned_data.get("ma_code") or "").upper().split())
        if not code:
            raise forms.ValidationError("Vui lòng nhập mã voucher.")
        qs = KhuyenMai.objects.filter(ma_code__iexact=code)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Mã voucher này đã tồn tại. Vui lòng dùng mã khác.")
        return code

    def clean(self):
        cleaned_data = super().clean()
        discount_type = cleaned_data.get("loai_giam")
        discount_value = cleaned_data.get("gia_tri_giam") or Decimal("0")
        max_discount = cleaned_data.get("giam_toi_da")
        start_at = cleaned_data.get("ngay_bat_dau")
        end_at = cleaned_data.get("ngay_ket_thuc")

        if discount_value <= 0:
            self.add_error("gia_tri_giam", "Giá trị giảm phải lớn hơn 0.")
        if discount_type == "percent" and discount_value > 100:
            self.add_error("gia_tri_giam", "Voucher phần trăm chỉ được nhập tối đa 100.")
        if discount_type == "fixed" and max_discount:
            self.add_error("giam_toi_da", "Giảm tối đa chỉ nên dùng cho voucher phần trăm.")
        if start_at and end_at and end_at <= start_at:
            self.add_error("ngay_ket_thuc", "Ngày kết thúc phải sau ngày bắt đầu.")
        return cleaned_data

    class Media:
        js = ("store/js/voucher_admin_preview.js",)


class NhanVienAdminForm(forms.ModelForm):
    class Meta:
        model = NhanVien
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        field = self.fields.get("co_quyen_nhap_kho")
        if field is not None:
            field.help_text = "Bật để nhân viên được quyền ký phiếu nhập kho."


@admin.register(ThuongHieu)
class ThuongHieuAdmin(admin.ModelAdmin):
    list_display = ("id", "ten")
    list_display_links = ("id", "ten")
    search_fields = ("ten",)
    ordering = ("ten",)
    list_per_page = 25


@admin.register(NhaCungCap)
class NhaCungCapAdmin(admin.ModelAdmin):
    list_display = ("id", "ten", "ghi_chu_short")
    list_display_links = ("id", "ten")
    search_fields = ("ten", "ghi_chu")
    ordering = ("ten",)
    list_per_page = 25

    @admin.display(description="Ghi chú")
    def ghi_chu_short(self, obj):
        return (obj.ghi_chu[:60] + "...") if obj.ghi_chu and len(obj.ghi_chu) > 60 else (obj.ghi_chu or "-")


@admin.register(NhomSanPham)
class NhomSanPhamAdmin(admin.ModelAdmin):
    list_display = ("id", "ten")
    list_display_links = ("id", "ten")
    search_fields = ("ten",)
    ordering = ("ten",)
    list_per_page = 25


@admin.register(SanPham)
class SanPhamAdmin(admin.ModelAdmin):
    list_display = ("id", "thumb", "ten", "gia_ban", "stock_badge", "nhom_san_pham", "thuong_hieu", "nha_cung_cap", "stock_history_link")
    list_display_links = ("id", "ten")
    list_filter = (StockLevelFilter, "nhom_san_pham", "thuong_hieu", "nha_cung_cap")
    search_fields = ("ten", "nhom_san_pham__ten", "thuong_hieu__ten", "nha_cung_cap__ten")
    list_select_related = ("nhom_san_pham", "thuong_hieu", "nha_cung_cap")
    ordering = ("ten",)
    list_per_page = 25
    autocomplete_fields = ("nhom_san_pham", "thuong_hieu", "nha_cung_cap")
    readonly_fields = ("ton_kho",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(
            store_stock_total=Coalesce(Sum("ton_kho_theo_cua_hang__ton_kho"), 0)
        )

    @admin.display(description="Ảnh")
    def thumb(self, obj):
        return _img(obj.hinh_anh, size=44)

    @admin.display(description="Tồn kho", ordering="store_stock_total")
    def stock_badge(self, obj):
        qty = int(getattr(obj, "store_stock_total", 0) or 0)
        if qty <= 0:
            bg = "#fee2e2"
            color = "#b91c1c"
            text = "Hết hàng"
        elif qty <= obj.LOW_STOCK_THRESHOLD:
            bg = "#fef3c7"
            color = "#b45309"
            text = f"Sắp hết ({qty})"
        else:
            bg = "#dcfce7"
            color = "#166534"
            text = f"Còn {qty}"
        return format_html(
            '<span style="display:inline-block;padding:4px 10px;border-radius:999px;'
            'background:{};color:{};font-weight:700;">{}</span>',
            bg,
            color,
            text,
        )

    @admin.display(description="Giao dịch kho")
    def stock_history_link(self, obj):
        url = reverse("admin:gis_store_giaodichkho_changelist") + f"?san_pham__id__exact={obj.pk}"
        return format_html('<a href="{}">Xem sổ kho</a>', url)

    class Media:
        js = ("assets/js/image_preview.js",)


@admin.register(HinhAnhSanPham)
class HinhAnhSanPhamAdmin(admin.ModelAdmin):
    list_display = ("id", "thumb", "san_pham", "chu_thich", "thu_tu")
    list_display_links = ("id", "san_pham")
    list_filter = ("san_pham__nhom_san_pham", "san_pham__thuong_hieu")
    search_fields = ("san_pham__ten", "chu_thich")
    list_select_related = ("san_pham", "san_pham__nhom_san_pham", "san_pham__thuong_hieu")
    ordering = ("san_pham__ten", "thu_tu", "id")
    autocomplete_fields = ("san_pham",)
    list_per_page = 25

    @admin.display(description="Ảnh")
    def thumb(self, obj):
        return _img(obj.hinh_anh, size=44)

    class Media:
        js = ("assets/js/image_preview.js",)


@admin.register(GiaoDichKho)
class GiaoDichKhoAdmin(admin.ModelAdmin):
    list_display = ("id", "created_at", "san_pham", "cua_hang", "nhan_vien", "signature_thumb", "loai", "so_luong", "ton_truoc", "ton_sau", "don_hang", "created_by")
    list_display_links = ("id", "san_pham")
    list_filter = ("loai", "cua_hang", "san_pham__nhom_san_pham", "san_pham__thuong_hieu", "nhan_vien__cua_hang")
    search_fields = ("san_pham__ten", "ghi_chu", "don_hang__id", "created_by__username", "nhan_vien__ho_ten", "cua_hang__ten")
    list_select_related = ("san_pham", "cua_hang", "don_hang", "created_by", "nhan_vien", "nhan_vien__cua_hang")
    ordering = ("-created_at", "-id")
    autocomplete_fields = ("san_pham", "cua_hang", "don_hang", "created_by", "nhan_vien")
    readonly_fields = (
        "ton_truoc",
        "ton_sau",
        "created_at",
        "signed_at",
        "signed_by",
        "signed_ip",
        "signed_user_agent",
        "otp_recipient_email",
        "otp_expires_at",
        "otp_verified_at",
        "otp_verified_by",
        "otp_verified_ip",
        "otp_verified_user_agent",
    )
    list_per_page = 25
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "san_pham",
                    "cua_hang",
                    "nhan_vien",
                    "loai",
                    "so_luong",
                    "don_hang",
                    "ghi_chu",
                    "chu_ky",
                )
            },
        ),
        (
            "Log ký & OTP",
            {
                "fields": (
                    "signed_at",
                    "signed_by",
                    "signed_ip",
                    "signed_user_agent",
                    "otp_recipient_email",
                    "otp_expires_at",
                    "otp_verified_at",
                    "otp_verified_by",
                    "otp_verified_ip",
                    "otp_verified_user_agent",
                    "ton_truoc",
                    "ton_sau",
                    "created_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    @admin.display(description="Chữ ký")
    def signature_thumb(self, obj):
        return _img(obj.chu_ky, size=44)


@admin.register(TonKhoCuaHang)
class TonKhoCuaHangAdmin(admin.ModelAdmin):
    list_display = ("id", "cua_hang", "san_pham", "ton_kho", "updated_at")
    list_filter = ("cua_hang__chuoi", "cua_hang", "san_pham__nhom_san_pham", "san_pham__thuong_hieu")
    search_fields = ("cua_hang__ten", "cua_hang__chuoi__ten", "san_pham__ten")
    list_select_related = ("cua_hang", "cua_hang__chuoi", "san_pham")
    ordering = ("cua_hang__ten", "san_pham__ten")


@admin.register(TonKhoAudit)
class TonKhoAuditAdmin(admin.ModelAdmin):
    list_display = ("id", "created_at", "hanh_dong", "loai", "san_pham", "cua_hang", "so_luong", "ton_truoc", "ton_sau", "created_by", "ly_do_short")
    list_filter = ("hanh_dong", "loai", "cua_hang")
    search_fields = ("san_pham__ten", "cua_hang__ten", "created_by__username", "ly_do")
    list_select_related = ("san_pham", "cua_hang", "created_by")
    ordering = ("-created_at", "-id")
    readonly_fields = (
        "giao_dich",
        "san_pham",
        "cua_hang",
        "loai",
        "so_luong",
        "ton_truoc",
        "ton_sau",
        "hanh_dong",
        "ly_do",
        "created_by",
        "created_at",
    )

    @admin.display(description="Lý do")
    def ly_do_short(self, obj):
        return (obj.ly_do[:80] + "...") if obj.ly_do and len(obj.ly_do) > 80 else (obj.ly_do or "-")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ChuoiCuaHang)
class ChuoiCuaHangAdmin(admin.ModelAdmin):
    list_display = ("id", "logo_thumb", "ten", "mo_ta_short")
    list_display_links = ("id", "ten")
    search_fields = ("ten", "mo_ta")
    ordering = ("ten",)
    list_per_page = 25

    @admin.display(description="Logo")
    def logo_thumb(self, obj):
        return _img(obj.logo, size=44)

    @admin.display(description="Mô tả")
    def mo_ta_short(self, obj):
        return (obj.mo_ta[:60] + "...") if obj.mo_ta and len(obj.mo_ta) > 60 else (obj.mo_ta or "-")

    class Media:
        js = ("assets/js/image_preview.js",)


@admin.register(CuaHang)
class CuaHangAdmin(admin.ModelAdmin):
    form = CuaHangAdminForm
    list_display = (
        "id",
        "ten",
        "chuoi",
        "quan_huyen",
        "gio_hoat_dong",
        "hoat_dong_24h",
        "dia_chi_short",
        "vi_do",
        "kinh_do",
    )
    list_display_links = ("id", "ten")
    list_filter = ("chuoi", "quan_huyen", "hoat_dong_24h")
    search_fields = ("ten", "dia_chi", "quan_huyen", "chuoi__ten")
    list_select_related = ("chuoi",)
    ordering = ("chuoi__ten", "quan_huyen", "ten")
    list_per_page = 25

    @admin.display(description="Địa chỉ")
    def dia_chi_short(self, obj):
        return (obj.dia_chi[:60] + "...") if obj.dia_chi and len(obj.dia_chi) > 60 else (obj.dia_chi or "-")

    @admin.display(description="Giờ hoạt động")
    def gio_hoat_dong(self, obj):
        if obj.hoat_dong_24h:
            return "24/7"
        if obj.mo_cua and obj.dong_cua:
            return f"{obj.mo_cua.strftime('%H:%M')} - {obj.dong_cua.strftime('%H:%M')}"
        if obj.mo_cua:
            return f"Mở: {obj.mo_cua.strftime('%H:%M')}"
        if obj.dong_cua:
            return f"Đóng: {obj.dong_cua.strftime('%H:%M')}"
        return "-"

    class Media:
        css = {
            "all": ("store/css/admin_multiselect.css",),
        }
        js = (
            "store/js/admin_multiselect_autocomplete_vn.js",
            "store/js/admin_coord_from_main_map.js",
        )


@admin.register(NhanVien)
class NhanVienAdmin(admin.ModelAdmin):
    form = NhanVienAdminForm
    list_display = ("id", "avatar_thumb", "ho_ten", "chuc_vu", "co_quyen_nhap_kho", "cua_hang", "so_dien_thoai", "email")
    list_display_links = ("id", "ho_ten")
    list_filter = ("cua_hang__chuoi", "cua_hang", "chuc_vu", "co_quyen_nhap_kho")
    search_fields = ("ho_ten", "chuc_vu", "so_dien_thoai", "email", "cua_hang__ten", "cua_hang__chuoi__ten")
    list_select_related = ("cua_hang", "cua_hang__chuoi")
    ordering = ("ho_ten",)
    list_per_page = 25
    autocomplete_fields = ("cua_hang",)

    @admin.display(description="Avatar")
    def avatar_thumb(self, obj):
        return _img(obj.avatar, size=40, media_fallback="avatar/default.jpg")

    class Media:
        js = ("assets/js/image_preview.js",)


@admin.register(KhuyenMai)
class KhuyenMaiAdmin(admin.ModelAdmin):
    form = KhuyenMaiAdminForm
    list_display = ("id", "ten", "ma_code", "loai_giam", "gia_tri_giam", "gia_tri_don_hang_toi_thieu", "dang_ap_dung")
    list_display_links = ("id", "ten")
    search_fields = ("ten", "ma_code", "mo_ta")
    list_filter = ("dang_ap_dung", "loai_giam")
    ordering = ("-id",)
    list_per_page = 25
    filter_horizontal = ("thuong_hieu", "cua_hang")

    @admin.display(description="Mô tả")
    def mo_ta_short(self, obj):
        return (obj.mo_ta[:70] + "...") if obj.mo_ta and len(obj.mo_ta) > 70 else (obj.mo_ta or "-")


@admin.register(HoSoKhachHang)
class HoSoKhachHangAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "so_dien_thoai", "dia_chi")
    search_fields = ("user__username", "user__email", "so_dien_thoai", "dia_chi")
    list_select_related = ("user",)


@admin.register(DiaChiKhachHang)
class DiaChiKhachHangAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "ho_ten_nguoi_nhan",
        "so_dien_thoai",
        "dia_chi_day_du_short",
        "loai_dia_chi",
        "mac_dinh",
    )
    list_filter = ("loai_dia_chi", "mac_dinh", "tinh_thanh")
    search_fields = (
        "user__username",
        "user__email",
        "ho_ten_nguoi_nhan",
        "so_dien_thoai",
        "dia_chi_cu_the",
        "phuong_xa",
        "quan_huyen",
        "tinh_thanh",
    )
    list_select_related = ("user",)
    ordering = ("user__username", "-mac_dinh", "-id")

    @admin.display(description="??a ch?")
    def dia_chi_day_du_short(self, obj):
        text = obj.dia_chi_day_du
        return (text[:80] + "...") if len(text) > 80 else text


@admin.register(DanhGiaCuaHang)
class DanhGiaCuaHangAdmin(admin.ModelAdmin):
    list_display = ("id", "cua_hang", "user", "so_sao", "created_at")
    list_display_links = ("id",)
    list_filter = ("so_sao", "cua_hang__chuoi", "created_at")
    search_fields = ("cua_hang__ten", "user__username", "binh_luan")
    list_select_related = ("cua_hang", "user", "cua_hang__chuoi")
    ordering = ("-created_at", "-id")
    list_per_page = 25


@admin.register(TepDanhGiaCuaHang)
class TepDanhGiaCuaHangAdmin(admin.ModelAdmin):
    list_display = ("id", "danh_gia", "loai", "created_at")
    list_display_links = ("id",)
    list_filter = ("loai", "created_at")
    search_fields = ("danh_gia__cua_hang__ten", "danh_gia__user__username")
    list_select_related = ("danh_gia", "danh_gia__cua_hang", "danh_gia__user")
    ordering = ("-created_at", "-id")
    list_per_page = 25


@admin.register(DonHang)
class DonHangAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "khach_hang",
        "ho_ten_nguoi_nhan",
        "trang_thai",
        "payment_status_badge",
        "payment_method_badge",
        "voucher_badge",
        "fulfillment_store",
        "receipt_badge",
        "delivery_coords",
        "tong_so_luong",
        "giam_gia",
        "tong_tien",
        "created_at",
    )
    list_filter = ("trang_thai", "trang_thai_thanh_toan", "created_at")
    search_fields = ("khach_hang__username", "khach_hang__email", "ho_ten_nguoi_nhan", "so_dien_thoai", "dia_chi_giao_hang", "ma_voucher_ap_dung", "phuong_thuc_thanh_toan", "trang_thai_thanh_toan", "ma_giao_dich_thanh_toan", "cua_hang_xu_ly__ten")
    list_select_related = ("khach_hang", "khuyen_mai", "cua_hang_xu_ly")

    @admin.display(description="Trạng thái thanh toán")
    def payment_status_badge(self, obj):
        palette = {
            "unpaid": ("#fff7ed", "#9a3412"),
            "paid": ("#ecfdf5", "#166534"),
            "awaiting_confirmation": ("#eff6ff", "#1d4ed8"),
            "refunded": ("#fef2f2", "#b91c1c"),
        }
        bg, fg = palette.get(obj.trang_thai_thanh_toan, ("#f8fafc", "#334155"))
        return format_html(
            '<span style="display:inline-block;padding:4px 10px;border-radius:999px;'
            'background:{};color:{};font-weight:700;">{}</span>',
            bg,
            fg,
            obj.get_trang_thai_thanh_toan_display(),
        )

    @admin.display(description="Thanh toán")
    def payment_method_badge(self, obj):
        palette = {
            "cod": ("#fff7ed", "#9a3412"),
            "bank_transfer": ("#ecfeff", "#155e75"),
            "momo": ("#fdf2f8", "#be185d"),
            "ewallet": ("#f5f3ff", "#6d28d9"),
        }
        bg, fg = palette.get(obj.phuong_thuc_thanh_toan, ("#f8fafc", "#334155"))
        return format_html(
            '<span style="display:inline-block;padding:4px 10px;border-radius:999px;'
            'background:{};color:{};font-weight:700;">{}</span>',
            bg,
            fg,
            obj.get_phuong_thuc_thanh_toan_display(),
        )

    @admin.display(description="Voucher")
    def voucher_badge(self, obj):
        if not obj.ma_voucher_ap_dung:
            return "-"
        return format_html(
            '<span style="display:inline-block;padding:4px 10px;border-radius:999px;'
            'background:#ecfeff;color:#155e75;font-weight:700;">{} ({})</span>',
            obj.ma_voucher_ap_dung,
            obj.giam_gia,
        )

    @admin.display(description="Cửa hàng xử lý")
    def fulfillment_store(self, obj):
        return obj.cua_hang_xu_ly.ten if obj.cua_hang_xu_ly_id else "-"

    @admin.display(description="Biên lai")
    def receipt_badge(self, obj):
        if not obj.anh_bien_lai:
            return "-"
        return format_html(
            '<a href="{}" target="_blank" rel="noopener" '
            'style="display:inline-block;padding:4px 10px;border-radius:999px;background:#ecfeff;color:#155e75;font-weight:700;">Xem biên lai</a>',
            obj.anh_bien_lai.url,
        )

    @admin.display(description="Tọa độ giao hàng")
    def delivery_coords(self, obj):
        if obj.vi_do_giao_hang is None or obj.kinh_do_giao_hang is None:
            return "-"
        url = (
            f"{reverse('store:map_page')}?"
            f"center_lat={obj.vi_do_giao_hang:.6f}&center_lon={obj.kinh_do_giao_hang:.6f}"
        )
        return format_html(
            '<a href="{}" target="_blank" rel="noopener">{}, {}</a>',
            url,
            f"{obj.vi_do_giao_hang:.6f}",
            f"{obj.kinh_do_giao_hang:.6f}",
        )


@admin.register(ChiTietDonHang)
class ChiTietDonHangAdmin(admin.ModelAdmin):
    list_display = ("id", "don_hang", "san_pham", "so_luong", "don_gia")
    search_fields = ("don_hang__khach_hang__username", "san_pham__ten")
    list_select_related = ("don_hang", "san_pham")

try:
    admin.site.unregister(User)
except NotRegistered:
    pass

admin.site.register(User, UserAdminVi)
