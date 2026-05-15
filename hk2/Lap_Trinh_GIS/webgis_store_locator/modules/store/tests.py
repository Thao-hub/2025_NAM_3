from datetime import datetime, time
from decimal import Decimal
from unittest.mock import patch
import pandas as pd
from django.contrib.auth.models import User
from django.core.management import call_command
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core import mail
from django.test import TestCase
from django.test.utils import override_settings
from django.utils import timezone

from modules.store.management.commands.restock_all_products import restock_products
from modules.store.controllers import (
    ROLE_ADMIN,
    ROLE_CUSTOMER_SUPPORT,
    ROLE_ORDER_MANAGER,
    ROLE_STOCK_MANAGER,
    ROLE_USER,
    _resolve_checkout_voucher,
    _save_about_gallery,
    _save_about_gallery_slots,
    _save_product_gallery,
    _ensure_role_groups,
)
from modules.spatial.controllers import _store_dict
from modules.store.models import ChiTietDonHang, ChuoiCuaHang, CuaHang, DanhGiaCuaHang, DonHang, GiaoDichKho, GopYKhachHang, HinhAnhSanPham, KhuyenMai, NhanVien, Notification, SanPham, TepDanhGiaCuaHang, ThuongHieu, TonKhoCuaHang, TrangGioiThieu, TrangGioiThieuHinhAnh, TrashRecord, XacNhanThanhToan


def _gif_file(name="signature.gif"):
    return SimpleUploadedFile(
        name,
        b"GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!"
        b"\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00"
        b"\x00\x02\x02D\x01\x00;",
        content_type="image/gif",
    )


def _video_file(name="clip.mp4"):
    return SimpleUploadedFile(
        name,
        b"\x00\x00\x00\x18ftypmp42\x00\x00\x00\x00mp42isom",
        content_type="video/mp4",
    )


class SmokeTests(TestCase):
    def test_home_page_ok(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_map_page_ok(self):
        response = self.client.get("/map/")
        self.assertEqual(response.status_code, 200)

    def test_ping_api_ok(self):
        response = self.client.get("/tools/ping/")
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"ok": True, "message": "pong", "pong": True})


class ProductGallerySyncTests(TestCase):
    def test_reordering_gallery_images_updates_saved_order(self):
        product = SanPham.objects.create(
            ten="San pham gallery",
            gia_ban=10000,
            hinh_anh=_gif_file("main.gif"),
        )
        image_1 = HinhAnhSanPham.objects.create(
            san_pham=product,
            hinh_anh=_gif_file("gallery-1.gif"),
            thu_tu=1,
            chu_thich="Ảnh phụ 1",
        )
        image_2 = HinhAnhSanPham.objects.create(
            san_pham=product,
            hinh_anh=_gif_file("gallery-2.gif"),
            thu_tu=2,
            chu_thich="Ảnh phụ 2",
        )

        class _DummyFiles:
            def get(self, key):
                return None

            def getlist(self, key):
                return []

        _save_product_gallery(
            product,
            _DummyFiles(),
            {
                f"image_order_{image_1.pk}": "2",
                f"image_order_{image_2.pk}": "1",
            },
        )

        ordered_ids = list(product.hinh_anh_phu.order_by("thu_tu", "id").values_list("pk", flat=True))
        self.assertEqual(ordered_ids[:2], [image_2.pk, image_1.pk])

    def test_multi_upload_uses_first_image_as_main_and_rest_as_gallery(self):
        product = SanPham.objects.create(ten="San pham multi upload", gia_ban=12000)

        class _DummyFiles:
            def get(self, key):
                return None

            def getlist(self, key):
                if key == "product_images":
                    return [
                        _gif_file("main-upload.gif"),
                        _gif_file("gallery-upload-1.gif"),
                        _gif_file("gallery-upload-2.gif"),
                    ]
                return []

        _save_product_gallery(product, _DummyFiles(), {})

        product.refresh_from_db()
        self.assertTrue(bool(product.hinh_anh))
        self.assertEqual(product.hinh_anh_phu.count(), 2)


class StorePayloadTests(TestCase):
    def setUp(self):
        self.chain = ChuoiCuaHang.objects.create(ten="CIRCLEK")

    def test_store_payload_includes_business_fields(self):
        store = CuaHang.objects.create(
            chuoi=self.chain,
            ten="CK Test",
            dia_chi="1 Test",
            quan_huyen="Quan 1",
            vi_do=10.77,
            kinh_do=106.70,
            mo_cua=time(7, 0),
            dong_cua=time(22, 0),
            hoat_dong_24h=False,
        )
        payload = _store_dict(store)
        self.assertEqual(payload["open_time"], "07:00")
        self.assertEqual(payload["close_time"], "22:00")
        self.assertEqual(payload["is_24h"], False)
        self.assertIn("is_open_now", payload)
        self.assertIn("business_hours", payload)
        self.assertEqual(payload["coord_source"], "db")

    def test_store_payload_24h(self):
        store = CuaHang.objects.create(
            chuoi=self.chain,
            ten="CK 24h",
            dia_chi="2 Test",
            quan_huyen="Quan 1",
            vi_do=10.78,
            kinh_do=106.71,
            hoat_dong_24h=True,
        )
        payload = _store_dict(store)
        self.assertEqual(payload["is_24h"], True)
        self.assertEqual(payload["business_hours"], "24/7")
        self.assertEqual(payload["is_open_now"], True)


class StoreReviewApiTests(TestCase):
    def setUp(self):
        self.chain = ChuoiCuaHang.objects.create(ten="CIRCLEK")
        self.store = CuaHang.objects.create(
            chuoi=self.chain,
            ten="CK Review",
            dia_chi="1 Review Street",
            quan_huyen="Quan 1",
            vi_do=10.77,
            kinh_do=106.70,
            hoat_dong_24h=True,
        )
        self.user = User.objects.create_user(username="review_user", password="Abc12345!")

    def test_store_reviews_api_returns_summary(self):
        review = DanhGiaCuaHang.objects.create(
            cua_hang=self.store,
            user=self.user,
            so_sao=5,
            binh_luan="Rat tot",
        )
        TepDanhGiaCuaHang.objects.create(
            danh_gia=review,
            tep=_gif_file("review.gif"),
            loai="image",
        )

        response = self.client.get(f"/stores/{self.store.pk}/reviews/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["ok"])
        self.assertEqual(data["summary"]["total_reviews"], 1)
        self.assertEqual(data["summary"]["total_media"], 1)
        self.assertEqual(data["reviews"][0]["stars"], 5)

    def test_authenticated_user_can_create_review_with_media(self):
        self.client.login(username="review_user", password="Abc12345!")

        response = self.client.post(
            f"/stores/{self.store.pk}/reviews/create/",
            data={
                "stars": "4",
                "comment": "On ap, sach se",
                "media": [_gif_file("photo.gif"), _video_file("clip.mp4")],
            },
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["ok"])
        self.assertEqual(DanhGiaCuaHang.objects.filter(cua_hang=self.store, user=self.user).count(), 1)
        self.assertEqual(TepDanhGiaCuaHang.objects.filter(danh_gia__cua_hang=self.store).count(), 2)
        self.assertEqual(data["summary"]["total_reviews"], 1)
        notice = Notification.objects.order_by("-created_at").first()
        self.assertIsNotNone(notice)
        self.assertIn("Đánh giá mới", notice.title)
        self.assertIn(self.store.ten, notice.title)
        self.assertIn(self.user.username, notice.message)
        self.assertIn("focus_review=", notice.path)

    def test_create_review_requires_regular_user_login(self):
        response = self.client.post(
            f"/stores/{self.store.pk}/reviews/create/",
            data={"stars": "5", "comment": "Tot"},
        )
        self.assertEqual(response.status_code, 401)


class StoreReviewAdminCustomTests(TestCase):
    def setUp(self):
        groups = _ensure_role_groups()
        self.support_user = User.objects.create_user(
            username="support_reviews",
            password="Abc12345!",
            is_staff=True,
        )
        self.support_user.groups.add(groups[ROLE_CUSTOMER_SUPPORT])
        self.customer = User.objects.create_user(
            username="customer_reviews",
            password="Abc12345!",
        )
        self.chain = ChuoiCuaHang.objects.create(ten="REVIEW CHAIN")
        self.store = CuaHang.objects.create(
            chuoi=self.chain,
            ten="Store Review Admin",
            dia_chi="1 Review Admin",
            quan_huyen="Quan 1",
            vi_do=10.77,
            kinh_do=106.70,
            hoat_dong_24h=True,
        )
        self.review = DanhGiaCuaHang.objects.create(
            cua_hang=self.store,
            user=self.customer,
            so_sao=5,
            binh_luan="Nhan vien than thien va cua hang sach se.",
        )
        self.media = TepDanhGiaCuaHang.objects.create(
            danh_gia=self.review,
            tep=_gif_file("review-admin.gif"),
            loai="image",
        )

    def test_admin_review_module_list_renders_with_filters_and_detail(self):
        self.client.force_login(self.support_user)

        response = self.client.get("/admin/danh-gia-cua-hang/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Store Review Admin")
        self.assertContains(response, "5 sao")
        self.assertContains(response, "Nhan vien than thien va cua hang sach se.")
        self.assertContains(response, self.media.tep.url)
        facet_params = {facet["param"] for facet in response.context["facet_filters"]}
        self.assertTrue({"store", "stars", "user", "created_at_range"}.issubset(facet_params))

    def test_admin_review_module_supports_filtering(self):
        other_customer = User.objects.create_user(username="other_reviews", password="Abc12345!")
        DanhGiaCuaHang.objects.create(
            cua_hang=self.store,
            user=other_customer,
            so_sao=2,
            binh_luan="Tam on",
        )
        self.client.force_login(self.support_user)
        review_local_date = timezone.localtime(self.review.created_at).date().isoformat()

        response = self.client.get(
            f"/admin/danh-gia-cua-hang/?stars=5&user={self.customer.username}&store={self.store.ten}&created_at_range_from={review_local_date}&created_at_range_to={review_local_date}"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["rows"]), 1)
        self.assertContains(response, "5 sao")
        self.assertNotContains(response, "2 sao")

    def test_admin_review_update_page_shows_attached_media(self):
        self.client.force_login(self.support_user)

        response = self.client.get(f"/admin/danh-gia-cua-hang/{self.review.pk}/edit/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ảnh / video đã gửi")
        self.assertContains(response, self.media.tep.url)


class SmartSearchTests(TestCase):
    def setUp(self):
        self.chain = ChuoiCuaHang.objects.create(ten="CIRCLEK")
        CuaHang.objects.create(
            chuoi=self.chain,
            ten="Circle K Test",
            dia_chi="236 Le Van Sy, Tan Binh, TP.HCM",
            quan_huyen="Tan Binh",
            vi_do=10.7934,
            kinh_do=106.6789,
            hoat_dong_24h=True,
        )

    @patch("modules.spatial.controllers._call_photon_search_safe")
    @patch("modules.spatial.controllers._call_nominatim_search_safe")
    def test_smart_search_geocode_address_mode(self, mock_nominatim, mock_photon):
        mock_photon.return_value = ([], None)
        mock_nominatim.return_value = (
            [
                {
                    "display_name": "236 Le Van Sy, Tan Binh, Thanh pho Ho Chi Minh, Viet Nam",
                    "lat": "10.7934",
                    "lon": "106.6789",
                }
            ],
            None,
        )

        response = self.client.post(
            "/tools/smart-search/",
            data='{"ten":"CIRCLEK","dia_chi":"236 Le Van Sy, Tan Binh, Thanh pho Ho Chi Minh, Viet Nam","max_km":1}',
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["mode"], "geocode_address")
        self.assertTrue(data["ok"])
        self.assertEqual(data["count"], 1)


class AdminOrderManagementTests(TestCase):
    def setUp(self):
        groups = _ensure_role_groups()
        self.admin = User.objects.create_user(
            username="admin_orders",
            password="Abc12345!",
            is_staff=True,
        )
        self.admin.groups.add(groups[ROLE_ADMIN])

        self.customer = User.objects.create_user(
            username="customer_orders",
            password="Abc12345!",
        )
        self.customer.groups.add(groups[ROLE_USER])

        self.product = SanPham.objects.create(
            ten="San pham test",
            gia_ban=25000,
        )
        self.order = DonHang.objects.create(
            khach_hang=self.customer,
            ho_ten_nguoi_nhan="Khach Test",
            so_dien_thoai="0123456789",
            dia_chi_giao_hang="Dia chi test",
            trang_thai="pending",
            tong_so_luong=1,
            tong_tien=25000,
        )

    def test_admin_order_list_can_filter_by_status(self):
        self.client.force_login(self.admin)

        response = self.client.get("/admin/don-hang/", {"status": "pending"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["status_filter"], "pending")
        rows = response.context["rows"]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["object"].pk, self.order.pk)
        self.assertEqual(rows[0]["status_actions"][0]["value"], "confirmed")

    def test_admin_order_detail_opens_project_map_instead_of_google_maps(self):
        self.order.vi_do_giao_hang = 10.781234
        self.order.kinh_do_giao_hang = 106.701234
        self.order.dia_chi_giao_hang = "123 Duong Test, Tan Binh"
        self.order.save(update_fields=["vi_do_giao_hang", "kinh_do_giao_hang", "dia_chi_giao_hang"])
        self.client.force_login(self.admin)

        response = self.client.get("/admin/chi-tiet-don-hang/", {"order": self.order.pk})

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "/map/?center_lat=10.781234&amp;center_lon=106.701234&amp;q=123%20Duong%20Test%2C%20Tan%20Binh",
        )
        self.assertContains(response, "Mở bản đồ trong hệ thống")
        self.assertNotContains(response, "google.com/maps")

    def test_admin_dashboard_can_export_revenue_csv(self):
        self.order.trang_thai_thanh_toan = "paid"
        self.order.tong_tien = 25000
        self.order.save(update_fields=["trang_thai_thanh_toan", "tong_tien"])
        self.client.force_login(self.admin)

        response = self.client.get("/admin/export/revenue/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv; charset=utf-8")
        self.assertIn("dashboard-doanh-thu-", response["Content-Disposition"])
        content = response.content.decode("utf-8")
        self.assertIn("Ngay,So don moi,Doanh thu da thanh toan", content)
        self.assertIn(",1,25000", content)

    def test_admin_can_confirm_ship_and_deliver_order(self):
        self.client.force_login(self.admin)

        response = self.client.post(
            f"/admin/orders/{self.order.pk}/confirmed/",
            {"return_query": "status=pending&page=1"},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.order.refresh_from_db()
        self.assertEqual(self.order.trang_thai, "confirmed")

        response = self.client.post(
            f"/admin/orders/{self.order.pk}/shipping/",
            {"return_query": "status=confirmed&page=1"},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.order.refresh_from_db()
        self.assertEqual(self.order.trang_thai, "shipping")

        response = self.client.post(
            f"/admin/orders/{self.order.pk}/delivered/",
            {"return_query": "status=shipping&page=1"},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.order.refresh_from_db()
        self.assertEqual(self.order.trang_thai, "delivered")

    def test_admin_cannot_cancel_delivered_order(self):
        self.client.force_login(self.admin)
        self.order.trang_thai = "delivered"
        self.order.save(update_fields=["trang_thai"])

        response = self.client.post(
            f"/admin/orders/{self.order.pk}/cancelled/",
            {"return_query": "status=delivered&page=1"},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.order.refresh_from_db()
        self.assertEqual(self.order.trang_thai, "delivered")

    def test_done_filter_includes_delivered_orders(self):
        self.client.force_login(self.admin)
        self.order.trang_thai = "delivered"
        self.order.save(update_fields=["trang_thai"])

        response = self.client.get("/admin/don-hang/", {"status": "done"})

        self.assertEqual(response.status_code, 200)
        rows = response.context["rows"]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["object"].pk, self.order.pk)

    def test_admin_can_update_payment_status(self):
        self.client.force_login(self.admin)
        self.order.trang_thai_thanh_toan = "awaiting_confirmation"
        self.order.save(update_fields=["trang_thai_thanh_toan"])

        response = self.client.post(
            f"/admin/orders/{self.order.pk}/payment/paid/",
            {"return_query": "status=pending&page=1"},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.order.refresh_from_db()
        self.assertEqual(self.order.trang_thai_thanh_toan, "paid")


class CustomerPurchaseFlowTests(TestCase):
    def setUp(self):
        groups = _ensure_role_groups()
        self.admin = User.objects.create_user(
            username="admin_flow",
            password="Abc12345!",
            is_staff=True,
        )
        self.admin.groups.add(groups[ROLE_ADMIN])

        self.customer = User.objects.create_user(
            username="customer_flow",
            password="Abc12345!",
        )
        self.customer.groups.add(groups[ROLE_USER])

        self.product = SanPham.objects.create(
            ten="San pham mua ngay",
            gia_ban=30000,
        )
        self.chain = ChuoiCuaHang.objects.create(ten="CHAIN FLOW")
        self.store = CuaHang.objects.create(
            chuoi=self.chain,
            ten="Cua hang flow",
            dia_chi="1 Test",
            quan_huyen="Quan 1",
            vi_do=10.77,
            kinh_do=106.70,
            hoat_dong_24h=True,
        )
        self.employee = NhanVien.objects.create(cua_hang=self.store, ho_ten="Nhan Vien Flow")
        GiaoDichKho.objects.create(
            san_pham=self.product,
            nhan_vien=self.employee,
            chu_ky=_gif_file("flow.gif"),
            loai="import",
            so_luong=20,
            ghi_chu="Nhập kho phục vụ test",
        )

    def test_buy_now_redirects_guest_to_login_then_checkout(self):
        response = self.client.post(
            f"/cart/add/{self.product.pk}/",
            {"next": "/checkout/"},
        )

        self.assertRedirects(response, "/user/login/?next=/checkout/")

        response = self.client.post(
            "/user/login/?next=/checkout/",
            {"username": "customer_flow", "password": "Abc12345!", "next": "/checkout/"},
        )

        self.assertRedirects(response, "/checkout/")

    def test_add_to_cart_redirects_guest_to_login_then_cart(self):
        response = self.client.post(
            f"/cart/add/{self.product.pk}/",
            {"next": "/cart/"},
        )

        self.assertRedirects(response, "/user/login/?next=/cart/")

        response = self.client.post(
            "/user/login/?next=/cart/",
            {"username": "customer_flow", "password": "Abc12345!", "next": "/cart/"},
        )

        self.assertRedirects(response, "/cart/")

    def test_admin_is_redirected_to_customer_login_when_buying(self):
        self.client.force_login(self.admin)

        response = self.client.post(
            f"/cart/add/{self.product.pk}/",
            {"next": "/checkout/"},
        )

        self.assertRedirects(response, "/user/login/?next=/checkout/")

    def test_regular_user_cannot_access_admin_dashboard(self):
        self.client.force_login(self.customer)

        response = self.client.get("/admin/")

        self.assertRedirects(
            response,
            "/admin/login/",
            fetch_redirect_response=False,
        )

    def test_admin_dashboard_renders_revenue_export_and_chart_widgets(self):
        self.client.force_login(self.admin)

        response = self.client.get("/admin/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Xuất doanh thu")
        self.assertContains(response, "Biểu đồ doanh thu")
        self.assertContains(response, "Kênh thanh toán")

    def test_admin_cannot_access_user_dashboard(self):
        self.client.force_login(self.admin)

        response = self.client.get("/user/")

        self.assertRedirects(response, "/admin/")


class RolePermissionTests(TestCase):
    def setUp(self):
        groups = _ensure_role_groups()
        self.system_admin = User.objects.create_user(
            username="sys_admin_role",
            password="Abc12345!",
            is_staff=True,
        )
        self.system_admin.groups.add(groups[ROLE_ADMIN])

        self.stock_manager = User.objects.create_user(
            username="stock_manager_role",
            password="Abc12345!",
            is_staff=True,
        )
        self.stock_manager.groups.add(groups[ROLE_STOCK_MANAGER])

        self.order_manager = User.objects.create_user(
            username="order_manager_role",
            password="Abc12345!",
            is_staff=True,
        )
        self.order_manager.groups.add(groups[ROLE_ORDER_MANAGER])

        self.support_user = User.objects.create_user(
            username="support_role",
            password="Abc12345!",
            is_staff=True,
        )
        self.support_user.groups.add(groups[ROLE_CUSTOMER_SUPPORT])

        self.customer = User.objects.create_user(
            username="customer_role",
            password="Abc12345!",
        )
        self.customer.groups.add(groups[ROLE_USER])
        self.order_customer = User.objects.create_user(
            username="customer_role_orders",
            password="Abc12345!",
        )
        self.order_customer.groups.add(groups[ROLE_USER])

        self.product = SanPham.objects.create(ten="Role Test Product", gia_ban=30000)
        self.chain = ChuoiCuaHang.objects.create(ten="ROLE CHAIN")
        self.store = CuaHang.objects.create(
            chuoi=self.chain,
            ten="Role Store",
            dia_chi="1 Role Street",
            quan_huyen="Quan 1",
            vi_do=10.77,
            kinh_do=106.70,
            hoat_dong_24h=True,
        )
        self.employee = NhanVien.objects.create(cua_hang=self.store, ho_ten="Role Employee")
        GiaoDichKho.objects.create(
            san_pham=self.product,
            nhan_vien=self.employee,
            chu_ky=_gif_file("role-stock.gif"),
            loai="import",
            so_luong=20,
            ghi_chu="Nhap kho role test",
        )
        self.order = DonHang.objects.create(
            khach_hang=self.order_customer,
            ho_ten_nguoi_nhan="Khach Role",
            so_dien_thoai="0123456789",
            dia_chi_giao_hang="Dia chi role",
            trang_thai="pending",
            tong_so_luong=1,
            tong_tien=30000,
        )

    def test_stock_manager_can_open_stock_module_but_not_settings(self):
        self.client.force_login(self.stock_manager)

        stock_response = self.client.get("/admin/giao-dich-kho/")
        self.assertEqual(stock_response.status_code, 200)

        inventory_response = self.client.get("/admin/inventory/")
        self.assertEqual(inventory_response.status_code, 200)

        employee_response = self.client.get("/admin/nhan-vien/")
        self.assertEqual(employee_response.status_code, 200)

        settings_response = self.client.get("/admin/settings/", follow=True)
        self.assertEqual(settings_response.status_code, 200)
        self.assertRedirects(settings_response, "/admin/")

    def test_internal_roles_can_open_admin_about_page(self):
        self.client.force_login(self.order_manager)

        response = self.client.get("/admin/about/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "SmartGIS")
        self.assertContains(response, "Lưu bài giới thiệu")

    def test_internal_roles_can_update_admin_about_content(self):
        self.client.force_login(self.system_admin)

        response = self.client.post(
            "/admin/about/",
            {
                "tieu_de": "Bai gioi thieu moi",
                "mo_ta_ngan": "Mo ta ngan cho admin",
                "noi_dung": "Noi dung chi tiet\nDong thu hai",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        page = TrangGioiThieu.objects.get(pk=1)
        self.assertEqual(page.tieu_de, "Bai gioi thieu moi")
        self.assertEqual(page.mo_ta_ngan, "Mo ta ngan cho admin")
        self.assertEqual(page.noi_dung, "Noi dung chi tiet\nDong thu hai")
        self.assertContains(response, "Bai gioi thieu moi")

    def test_admin_about_can_upload_multiple_gallery_images(self):
        page = TrangGioiThieu.objects.create(
            pk=1,
            tieu_de="Trang co gallery",
            mo_ta_ngan="Mo ta co anh",
            noi_dung="Doan 1\n\nDoan 2",
        )

        saved_count = _save_about_gallery(
            page,
            [_gif_file("about-1.gif"), _gif_file("about-2.gif")],
            ["Mo ta anh 1", "Mo ta anh 2"],
            ["Tieu de anh 1", "Tieu de anh 2"],
        )

        self.assertEqual(saved_count, 2)
        self.assertEqual(TrangGioiThieuHinhAnh.objects.count(), 2)
        self.assertEqual(
            list(TrangGioiThieuHinhAnh.objects.order_by("thu_tu").values_list("chu_thich", flat=True)),
            ["Mo ta anh 1", "Mo ta anh 2"],
        )
        self.assertEqual(
            list(TrangGioiThieuHinhAnh.objects.order_by("thu_tu").values_list("tieu_de", flat=True)),
            ["Tieu de anh 1", "Tieu de anh 2"],
        )
        self.client.force_login(self.system_admin)
        self.assertContains(self.client.get("/admin/about/"), "Them anh moi")
        self.assertContains(self.client.get("/admin/about/"), "Mo ta anh 1")
        self.assertContains(self.client.get("/admin/about/"), "Tieu de anh 1")

    def test_public_intro_page_uses_latest_admin_content(self):
        page = TrangGioiThieu.objects.create(
            pk=1,
            tieu_de="Gioi thieu moi",
            mo_ta_ngan="Mo ta public",
            noi_dung="Noi dung doan 1\n\nNoi dung doan 2",
        )
        TrangGioiThieuHinhAnh.objects.create(
            trang=page,
            tieu_de="Tieu de anh public",
            hinh_anh=_gif_file("public-gallery.gif"),
            chu_thich="Mo ta anh public",
            thu_tu=1,
        )

        response = self.client.get("/info/gioi-thieu-circle-k/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Gioi thieu moi")
        self.assertContains(response, "Mo ta public")
        self.assertContains(response, "Noi dung doan 1")
        self.assertContains(response, "public-gallery")
        self.assertContains(response, "Tieu de anh public")
        self.assertContains(response, "Mo ta anh public")
        self.assertContains(response, "data-about-slider")

    def test_public_intro_page_falls_back_to_legacy_content_when_admin_page_is_default(self):
        TrangGioiThieu.objects.create(
            pk=1,
            tieu_de="Giới thiệu hệ thống",
            mo_ta_ngan="Trang này dùng để admin quản lý bài giới thiệu, cập nhật nội dung và hình ảnh minh họa.",
            noi_dung="",
        )

        response = self.client.get("/info/gioi-thieu-circle-k/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Giới thiệu Circle K")
        self.assertNotContains(response, "Giới thiệu hệ thống")

    def test_admin_about_can_update_existing_gallery_caption(self):
        page = TrangGioiThieu.objects.create(
            pk=1,
            tieu_de="Trang co caption",
            mo_ta_ngan="Mo ta",
            noi_dung="Noi dung",
        )
        image = TrangGioiThieuHinhAnh.objects.create(
            trang=page,
            tieu_de="Tieu de cu",
            hinh_anh=_gif_file("caption-update.gif"),
            chu_thich="Cu",
            thu_tu=1,
        )
        self.client.force_login(self.system_admin)

        response = self.client.post(
            "/admin/about/",
            {
                "tieu_de": "Trang co caption",
                "mo_ta_ngan": "Mo ta",
                "noi_dung": "Noi dung",
                f"gallery_title_{image.pk}": "Tieu de moi",
                f"gallery_caption_{image.pk}": "Moi cho anh",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        image.refresh_from_db()
        self.assertEqual(image.tieu_de, "Tieu de moi")
        self.assertEqual(image.chu_thich, "Moi cho anh")
        self.assertContains(response, "Tieu de moi")
        self.assertContains(response, "Moi cho anh")

    def test_admin_about_can_delete_old_gallery_group(self):
        page = TrangGioiThieu.objects.create(
            pk=1,
            tieu_de="Trang co bai cu",
            mo_ta_ngan="Mo ta",
            noi_dung="Noi dung",
        )
        _save_about_gallery_slots(
            page,
            [
                {
                    "slot": 1,
                    "title": "Bai cu 1",
                    "caption": "Mo ta bai cu 1",
                    "images": [_gif_file("old-1.gif"), _gif_file("old-2.gif"), _gif_file("old-3.gif")],
                }
            ],
        )
        group_key = TrangGioiThieuHinhAnh.objects.values_list("nhom", flat=True).first()
        self.client.force_login(self.system_admin)

        response = self.client.post(
            "/admin/about/",
            {
                "tieu_de": "Trang co bai cu",
                "mo_ta_ngan": "Mo ta",
                "noi_dung": "Noi dung",
                "delete_group_keys": [group_key],
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(TrangGioiThieuHinhAnh.objects.count(), 0)
        self.assertContains(response, "xoa")

    def test_admin_about_does_not_delete_old_group_when_new_slot_is_invalid(self):
        page = TrangGioiThieu.objects.create(
            pk=1,
            tieu_de="Trang giu bai cu",
            mo_ta_ngan="Mo ta",
            noi_dung="Noi dung",
        )
        _save_about_gallery_slots(
            page,
            [
                {
                    "slot": 1,
                    "title": "Bai cu can giu",
                    "caption": "Mo ta bai cu",
                    "images": [_gif_file("keep-1.gif"), _gif_file("keep-2.gif"), _gif_file("keep-3.gif")],
                }
            ],
        )
        group_key = TrangGioiThieuHinhAnh.objects.values_list("nhom", flat=True).first()
        old_titles = list(TrangGioiThieuHinhAnh.objects.order_by("thu_tu").values_list("tieu_de", flat=True))
        self.client.force_login(self.system_admin)

        response = self.client.post(
            "/admin/about/",
            {
                "tieu_de": "Trang giu bai cu",
                "mo_ta_ngan": "Mo ta",
                "noi_dung": "Noi dung",
                "delete_group_keys": [group_key],
                "gallery_slot_title_1": "Slot loi",
                "gallery_slot_caption_1": "Mo ta slot loi",
                "gallery_slot_images_1": [
                    _gif_file("invalid-1.gif"),
                    _gif_file("invalid-2.gif"),
                ],
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("B\u1ea3n 1 c\u1ea7n \u00edt nh\u1ea5t 3 \u1ea3nh khi t\u1ea3i l\u00ean.", response.context["form"].non_field_errors())
        self.assertEqual(TrangGioiThieuHinhAnh.objects.count(), 3)
        self.assertEqual(
            list(TrangGioiThieuHinhAnh.objects.order_by("thu_tu").values_list("tieu_de", flat=True)),
            old_titles,
        )
        self.assertEqual(TrangGioiThieuHinhAnh.objects.values_list("nhom", flat=True).distinct().count(), 1)

    def test_admin_about_can_create_gallery_item_from_slot_inputs(self):
        TrangGioiThieu.objects.create(
            pk=1,
            tieu_de="Trang slot",
            mo_ta_ngan="Mo ta",
            noi_dung="Noi dung",
        )
        self.client.force_login(self.system_admin)

        response = self.client.post(
            "/admin/about/",
            {
                "tieu_de": "Trang slot",
                "mo_ta_ngan": "Mo ta",
                "noi_dung": "Noi dung",
                "gallery_slot_title_1": "Tieu de slot 1",
                "gallery_slot_caption_1": "Mo ta slot 1",
                "gallery_slot_images_1": [
                    _gif_file("slot-1.gif"),
                    _gif_file("slot-2.gif"),
                    _gif_file("slot-3.gif"),
                ],
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(TrangGioiThieuHinhAnh.objects.count(), 3)
        self.assertEqual(
            list(TrangGioiThieuHinhAnh.objects.order_by("thu_tu").values_list("tieu_de", flat=True)),
            ["Tieu de slot 1", "Tieu de slot 1", "Tieu de slot 1"],
        )
        self.assertEqual(
            list(TrangGioiThieuHinhAnh.objects.order_by("thu_tu").values_list("chu_thich", flat=True)),
            ["Mo ta slot 1", "Mo ta slot 1", "Mo ta slot 1"],
        )
        self.assertEqual(TrangGioiThieuHinhAnh.objects.values_list("nhom", flat=True).distinct().count(), 1)
        self.assertContains(response, "Tieu de slot 1")
        self.assertContains(response, "Mo ta slot 1")

    def test_admin_about_rejects_slot_with_fewer_than_three_images(self):
        TrangGioiThieu.objects.create(
            pk=1,
            tieu_de="Trang slot loi",
            mo_ta_ngan="Mo ta",
            noi_dung="Noi dung",
        )
        self.client.force_login(self.system_admin)

        response = self.client.post(
            "/admin/about/",
            {
                "tieu_de": "Trang slot loi",
                "mo_ta_ngan": "Mo ta",
                "noi_dung": "Noi dung",
                "gallery_slot_title_1": "Tieu de slot loi",
                "gallery_slot_caption_1": "Mo ta slot loi",
                "gallery_slot_images_1": [
                    _gif_file("slot-a.gif"),
                    _gif_file("slot-b.gif"),
                ],
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(TrangGioiThieuHinhAnh.objects.count(), 0)
        self.assertIn("B\u1ea3n 1 c\u1ea7n \u00edt nh\u1ea5t 3 \u1ea3nh khi t\u1ea3i l\u00ean.", response.context["form"].non_field_errors())

    def test_order_manager_can_update_order_status(self):
        self.client.force_login(self.order_manager)

        response = self.client.post(f"/admin/orders/{self.order.pk}/confirmed/", {"return_query": ""}, follow=True)

        self.assertEqual(response.status_code, 200)
        self.order.refresh_from_db()
        self.assertEqual(self.order.trang_thai, "confirmed")

    def test_support_cannot_access_stock_module(self):
        self.client.force_login(self.support_user)

        response = self.client.get("/admin/giao-dich-kho/", follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, "/admin/")

        inventory_response = self.client.get("/admin/inventory/", follow=True)
        self.assertEqual(inventory_response.status_code, 200)
        self.assertRedirects(inventory_response, "/admin/")

    def test_support_cannot_access_supplier_master_data(self):
        self.client.force_login(self.support_user)

        response = self.client.get("/admin/nha-cung-cap/", follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, "/admin/")

    def test_support_can_change_order_status_but_not_payment_status(self):
        self.client.force_login(self.support_user)

        status_response = self.client.post(f"/admin/orders/{self.order.pk}/confirmed/", {"return_query": ""}, follow=True)
        self.assertEqual(status_response.status_code, 200)
        self.order.refresh_from_db()
        self.assertEqual(self.order.trang_thai, "confirmed")

        self.order.trang_thai_thanh_toan = "awaiting_confirmation"
        self.order.save(update_fields=["trang_thai_thanh_toan"])

        payment_response = self.client.post(f"/admin/orders/{self.order.pk}/payment/paid/", {"return_query": ""}, follow=True)
        self.assertEqual(payment_response.status_code, 200)
        self.assertRedirects(payment_response, "/admin/")
        self.order.refresh_from_db()
        self.assertEqual(self.order.trang_thai_thanh_toan, "awaiting_confirmation")

    def test_order_manager_can_update_payment_status(self):
        self.client.force_login(self.order_manager)
        self.order.trang_thai_thanh_toan = "awaiting_confirmation"
        self.order.save(update_fields=["trang_thai_thanh_toan"])

        response = self.client.post(f"/admin/orders/{self.order.pk}/payment/paid/", {"return_query": ""}, follow=True)

        self.assertEqual(response.status_code, 200)
        self.order.refresh_from_db()
        self.assertEqual(self.order.trang_thai_thanh_toan, "paid")

    def test_order_manager_can_approve_transfer_receipt(self):
        self.client.force_login(self.order_manager)
        self.order.phuong_thuc_thanh_toan = "bank_transfer"
        self.order.trang_thai_thanh_toan = "awaiting_confirmation"
        self.order.anh_bien_lai = _gif_file("approve-receipt.gif")
        self.order.save(update_fields=["phuong_thuc_thanh_toan", "trang_thai_thanh_toan", "anh_bien_lai"])

        response = self.client.post(
            f"/admin/orders/{self.order.pk}/receipt/approve/",
            {"return_query": ""},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.order.refresh_from_db()
        self.assertEqual(self.order.trang_thai_thanh_toan, "paid")
        self.assertTrue(
            XacNhanThanhToan.objects.filter(
                don_hang=self.order,
                hanh_dong="approved",
                performed_by=self.order_manager,
            ).exists()
        )

    def test_order_manager_can_reject_transfer_receipt_and_save_note(self):
        self.client.force_login(self.order_manager)
        self.order.phuong_thuc_thanh_toan = "bank_transfer"
        self.order.trang_thai_thanh_toan = "awaiting_confirmation"
        self.order.trang_thai = "pending"
        self.order.anh_bien_lai = _gif_file("reject-receipt.gif")
        self.order.save(update_fields=["phuong_thuc_thanh_toan", "trang_thai_thanh_toan", "trang_thai", "anh_bien_lai"])

        response = self.client.post(
            f"/admin/orders/{self.order.pk}/receipt/reject/",
            {"return_query": "", "rejection_note": "Sai so tien chuyen khoan"},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.order.refresh_from_db()
        self.assertEqual(self.order.trang_thai_thanh_toan, "unpaid")
        self.assertEqual(self.order.trang_thai, "pending")
        log = XacNhanThanhToan.objects.filter(don_hang=self.order, hanh_dong="rejected").latest("id")
        self.assertEqual(log.ghi_chu, "Sai so tien chuyen khoan")

    def test_order_detail_shows_payment_confirmation_history(self):
        self.order.phuong_thuc_thanh_toan = "bank_transfer"
        self.order.trang_thai_thanh_toan = "awaiting_confirmation"
        self.order.anh_bien_lai = _gif_file("history-receipt.gif")
        self.order.save(update_fields=["phuong_thuc_thanh_toan", "trang_thai_thanh_toan", "anh_bien_lai"])
        XacNhanThanhToan.objects.create(
            don_hang=self.order,
            hanh_dong="submitted",
            ghi_chu="Khach da gui bien lai",
            performed_by=self.order_customer,
        )
        XacNhanThanhToan.objects.create(
            don_hang=self.order,
            hanh_dong="rejected",
            ghi_chu="Anh mo khong ro",
            performed_by=self.system_admin,
        )
        self.client.force_login(self.order_customer)

        response = self.client.get(f"/orders/{self.order.pk}/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Lịch sử xác nhận thanh toán")
        self.assertContains(response, "Khach da gui bien lai")
        self.assertContains(response, "Anh mo khong ro")

    def test_system_admin_cancelling_unpaid_order_restores_stock(self):
        self.client.force_login(self.system_admin)
        product = SanPham.objects.create(ten="Cancel Stock Product", gia_ban=22000)
        GiaoDichKho.objects.create(
            san_pham=product,
            nhan_vien=self.employee,
            chu_ky=_gif_file("cancel-stock.gif"),
            loai="import",
            so_luong=5,
            ghi_chu="Nhap kho cancel test",
        )
        order = DonHang.objects.create(
            khach_hang=self.order_customer,
            ho_ten_nguoi_nhan="Khach Cancel",
            so_dien_thoai="0123456789",
            dia_chi_giao_hang="Dia chi cancel",
            trang_thai="pending",
            trang_thai_thanh_toan="unpaid",
            tong_so_luong=2,
            tong_tien=44000,
            cua_hang_xu_ly=self.store,
        )
        GiaoDichKho.objects.create(
            san_pham=product,
            cua_hang=self.store,
            loai="export",
            so_luong=2,
            don_hang=order,
            ghi_chu="Xuat kho cho don cancel",
        )

        response = self.client.post(
            f"/admin/orders/{order.pk}/cancelled/",
            {"return_query": "status=pending&page=1"},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        order.refresh_from_db()
        product.refresh_from_db()
        self.assertEqual(order.trang_thai, "cancelled")
        self.assertEqual(product.ton_kho, 5)
        self.assertFalse(GiaoDichKho.objects.filter(don_hang=order, loai="export").exists())

    def test_customer_still_cannot_access_admin(self):
        self.client.force_login(self.customer)

        response = self.client.get("/admin/giao-dich-kho/")

        self.assertRedirects(response, "/admin/login/", fetch_redirect_response=False)

    def test_checkout_creates_order_and_item(self):
        self.client.force_login(self.customer)
        session = self.client.session
        session["cart"] = {str(self.product.pk): 2}
        session.save()

        response = self.client.post(
            "/checkout/",
            {
                "receiver_name": "Nguyen Van A",
                "phone": "0900000000",
                "address": "123 Duong Test",
                "payment_method": "bank_transfer",
                "transfer_code": "MB-0001",
                "transfer_receipt": _gif_file("receipt.gif"),
                "note": "Giao gio hanh chinh",
            },
        )

        self.assertRedirects(response, "/orders/")
        order = DonHang.objects.get(khach_hang=self.customer)
        self.assertEqual(order.tong_so_luong, 2)
        self.assertEqual(order.tong_tien, 60000)
        self.assertEqual(order.phuong_thuc_thanh_toan, "bank_transfer")
        self.assertEqual(order.trang_thai_thanh_toan, "awaiting_confirmation")
        self.assertEqual(order.cua_hang_xu_ly, self.store)
        self.assertEqual(order.ma_giao_dich_thanh_toan, "MB-0001")
        self.assertTrue(bool(order.anh_bien_lai))
        self.assertTrue(ChiTietDonHang.objects.filter(don_hang=order, san_pham=self.product, so_luong=2).exists())
        self.product.refresh_from_db()
        self.assertEqual(self.product.ton_kho, 18)
        movement = GiaoDichKho.objects.get(san_pham=self.product, loai="export", so_luong=2, don_hang=order)
        self.assertEqual(movement.cua_hang, self.store)
        store_stock = TonKhoCuaHang.objects.get(cua_hang=self.store, san_pham=self.product)
        self.assertEqual(store_stock.ton_kho, 18)

    def test_checkout_locks_products_before_creating_order(self):
        self.client.force_login(self.customer)
        session = self.client.session
        session["cart"] = {str(self.product.pk): 1}
        session.save()

        with patch(
            "modules.store.controllers.SanPham.objects.select_for_update",
            wraps=SanPham.objects.select_for_update,
        ) as mocked_select_for_update:
            response = self.client.post(
                "/checkout/",
                {
                    "receiver_name": "Nguyen Van A",
                    "phone": "0900000000",
                    "address": "123 Duong Test",
                    "note": "Khoa ton kho truoc khi xuat",
                },
            )

        self.assertRedirects(response, "/orders/")
        self.assertTrue(mocked_select_for_update.called)

    def test_checkout_applies_voucher_and_saves_delivery_coordinates(self):
        voucher = KhuyenMai.objects.create(
            ten="Giam 10 phan tram",
            ma_code="GIAM10",
            loai_giam="percent",
            gia_tri_giam=10,
            gia_tri_don_hang_toi_thieu=50000,
            dang_ap_dung=True,
        )
        self.client.force_login(self.customer)
        session = self.client.session
        session["cart"] = {str(self.product.pk): 2}
        session.save()

        response = self.client.post(
            "/checkout/",
            {
                "receiver_name": "Nguyen Van A",
                "phone": "0900000000",
                "address": "123 Duong Test",
                "note": "Giao tan noi",
                "voucher_code": "GIAM10",
                "payment_method": "ewallet",
                "delivery_lat": "10.781234",
                "delivery_lng": "106.701234",
            },
        )

        self.assertRedirects(response, "/orders/")
        order = DonHang.objects.get(khach_hang=self.customer)
        self.assertEqual(order.khuyen_mai, voucher)
        self.assertEqual(order.ma_voucher_ap_dung, "GIAM10")
        self.assertEqual(order.tong_tien_truoc_giam, Decimal("60000"))
        self.assertEqual(order.giam_gia, Decimal("6000"))
        self.assertEqual(order.tong_tien, Decimal("54000"))
        self.assertEqual(order.phuong_thuc_thanh_toan, "ewallet")
        self.assertEqual(order.trang_thai_thanh_toan, "unpaid")
        self.assertAlmostEqual(order.vi_do_giao_hang, 10.781234)
        self.assertAlmostEqual(order.kinh_do_giao_hang, 106.701234)

    def test_checkout_rejects_out_of_range_delivery_coordinates(self):
        self.client.force_login(self.customer)
        session = self.client.session
        session["cart"] = {str(self.product.pk): 1}
        session.save()

        response = self.client.post(
            "/checkout/",
            {
                "receiver_name": "Nguyen Van A",
                "phone": "0900000000",
                "address": "123 Duong Test",
                "payment_method": "cod",
                "delivery_lat": "91",
                "delivery_lng": "106.701234",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(DonHang.objects.filter(khach_hang=self.customer).exists())
        messages = [message.message for message in response.context["messages"]]
        self.assertTrue(any("Vĩ độ giao hàng phải nằm trong khoảng từ -90 đến 90." in message for message in messages))

    def test_store_model_rejects_out_of_range_coordinates(self):
        store = CuaHang(
            chuoi=self.chain,
            ten="Cua hang sai toa do",
            dia_chi="2 Test",
            quan_huyen="Quan 3",
            vi_do=95,
            kinh_do=181,
        )

        with self.assertRaises(ValidationError) as exc:
            store.full_clean()

        self.assertIn("vi_do", exc.exception.message_dict)
        self.assertIn("kinh_do", exc.exception.message_dict)

    def test_checkout_accepts_momo_payment_method(self):
        self.client.force_login(self.customer)
        session = self.client.session
        session["cart"] = {str(self.product.pk): 1}
        session.save()

        response = self.client.post(
            "/checkout/",
            {
                "receiver_name": "Nguyen Van A",
                "phone": "0900000000",
                "address": "123 Duong Test",
                "payment_method": "momo",
                "note": "Thanh toan bang MoMo",
            },
        )

        order = DonHang.objects.filter(khach_hang=self.customer).latest("pk")
        self.assertRedirects(response, f"/payments/momo/{order.pk}/")
        self.assertEqual(order.phuong_thuc_thanh_toan, "momo")
        self.assertEqual(order.trang_thai_thanh_toan, "unpaid")
        self.product.refresh_from_db()
        self.assertEqual(self.product.ton_kho, 19)

    def test_momo_demo_success_marks_order_paid(self):
        self.client.force_login(self.customer)
        order = DonHang.objects.create(
            khach_hang=self.customer,
            ho_ten_nguoi_nhan="Khach MoMo",
            so_dien_thoai="0900000000",
            dia_chi_giao_hang="123 Demo",
            tong_so_luong=1,
            tong_tien=30000,
            tong_tien_truoc_giam=30000,
            phuong_thuc_thanh_toan="momo",
            trang_thai_thanh_toan="unpaid",
        )

        response = self.client.post(f"/payments/momo/{order.pk}/", {"action": "success"}, follow=True)

        self.assertEqual(response.status_code, 200)
        order.refresh_from_db()
        self.assertEqual(order.trang_thai_thanh_toan, "paid")

    def test_momo_demo_fail_keeps_order_unpaid(self):
        self.product.refresh_from_db()
        initial_stock = self.product.ton_kho
        self.client.force_login(self.customer)
        order = DonHang.objects.create(
            khach_hang=self.customer,
            ho_ten_nguoi_nhan="Khach MoMo Fail",
            so_dien_thoai="0900000000",
            dia_chi_giao_hang="123 Demo",
            tong_so_luong=1,
            tong_tien=30000,
            tong_tien_truoc_giam=30000,
            phuong_thuc_thanh_toan="momo",
            trang_thai_thanh_toan="unpaid",
            cua_hang_xu_ly=self.store,
        )
        GiaoDichKho.objects.create(
            san_pham=self.product,
            cua_hang=self.store,
            loai="export",
            so_luong=1,
            don_hang=order,
            ghi_chu="Xuat cho momo fail",
        )

        response = self.client.post(f"/payments/momo/{order.pk}/", {"action": "fail"}, follow=True)

        self.assertEqual(response.status_code, 200)
        order.refresh_from_db()
        self.assertEqual(order.trang_thai_thanh_toan, "unpaid")
        self.assertEqual(order.trang_thai, "cancelled")
        self.product.refresh_from_db()
        self.assertEqual(self.product.ton_kho, initial_stock)
        self.assertFalse(GiaoDichKho.objects.filter(don_hang=order, loai="export").exists())


class StockMovementTests(TestCase):
    def setUp(self):
        self.chain = ChuoiCuaHang.objects.create(ten="CHAIN STOCK")
        self.store = CuaHang.objects.create(
            chuoi=self.chain,
            ten="Cua hang stock",
            dia_chi="1 Test",
            quan_huyen="Quan 1",
            vi_do=10.77,
            kinh_do=106.70,
            hoat_dong_24h=True,
        )
        self.employee = NhanVien.objects.create(cua_hang=self.store, ho_ten="Nhan Vien Stock")

    def test_stock_movement_updates_running_stock(self):
        product = SanPham.objects.create(ten="San pham kho", gia_ban=15000)

        GiaoDichKho.objects.create(
            san_pham=product,
            nhan_vien=self.employee,
            chu_ky=_gif_file("stock-1.gif"),
            loai="import",
            so_luong=10,
            ghi_chu="Nhập lô 1",
        )
        GiaoDichKho.objects.create(san_pham=product, cua_hang=self.store, loai="export", so_luong=3, ghi_chu="Xuất lẻ")

        product.refresh_from_db()
        self.assertEqual(product.ton_kho, 7)
        self.assertEqual(TonKhoCuaHang.objects.get(cua_hang=self.store, san_pham=product).ton_kho, 7)

        rows = list(GiaoDichKho.objects.filter(san_pham=product).order_by("created_at", "id"))
        self.assertEqual(rows[0].ton_truoc, 0)
        self.assertEqual(rows[0].ton_sau, 10)
        self.assertEqual(rows[1].ton_truoc, 10)
        self.assertEqual(rows[1].ton_sau, 7)

    def test_export_cannot_make_stock_negative(self):
        product = SanPham.objects.create(ten="San pham am kho", gia_ban=15000)
        GiaoDichKho.objects.create(
            san_pham=product,
            nhan_vien=self.employee,
            chu_ky=_gif_file("stock-2.gif"),
            loai="import",
            so_luong=2,
            ghi_chu="Nhập lô",
        )

        with self.assertRaises(ValidationError):
            GiaoDichKho.objects.create(san_pham=product, cua_hang=self.store, loai="export", so_luong=5, ghi_chu="Xuất quá tồn")

    def test_import_requires_employee_and_signature(self):
        product = SanPham.objects.create(ten="San pham ky nhap", gia_ban=10000)

        with self.assertRaises(ValidationError):
            GiaoDichKho.objects.create(san_pham=product, loai="import", so_luong=2, ghi_chu="Nhập thiếu chữ ký")

        chain = ChuoiCuaHang.objects.create(ten="CHAIN TEST")
        store = CuaHang.objects.create(
            chuoi=chain,
            ten="Cua hang test",
            dia_chi="1 Test",
            quan_huyen="Quan 1",
            vi_do=10.77,
            kinh_do=106.70,
            hoat_dong_24h=True,
        )
        employee = NhanVien.objects.create(cua_hang=store, ho_ten="Nhan Vien Kho")

        movement = GiaoDichKho.objects.create(
            san_pham=product,
            nhan_vien=employee,
            chu_ky=_gif_file(),
            loai="import",
            so_luong=2,
            ghi_chu="Nhập đủ chữ ký",
        )
        product.refresh_from_db()
        self.assertEqual(product.ton_kho, 2)

    @patch("modules.store.controllers.pd.read_excel")
    def test_excel_import_rolls_back_all_rows_when_any_row_is_invalid(self, mock_read_excel):
        groups = _ensure_role_groups()
        admin_user = User.objects.create_user(
            username="admin_excel_import",
            password="Abc12345!",
            is_staff=True,
        )
        admin_user.groups.add(groups[ROLE_ADMIN])
        product = SanPham.objects.create(ten="San pham excel", gia_ban=12000)
        mock_read_excel.return_value = pd.DataFrame(
            [
                {
                    "san_pham": product.pk,
                    "loai": "import",
                    "so_luong": 2,
                    "nhan_vien_id": self.employee.pk,
                    "cua_hang_id": self.store.pk,
                    "ghi_chu": "Dong hop le",
                },
                {
                    "san_pham": 999999,
                    "loai": "import",
                    "so_luong": 1,
                    "nhan_vien_id": self.employee.pk,
                    "cua_hang_id": self.store.pk,
                    "ghi_chu": "Dong loi",
                },
            ]
        )
        self.client.force_login(admin_user)

        response = self.client.post(
            "/admin/giao-dich-kho/excel/import/",
            {
                "file": SimpleUploadedFile(
                    "stock.xlsx",
                    b"fake-xlsx",
                    content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(GiaoDichKho.objects.count(), 0)
        product.refresh_from_db()
        self.assertEqual(product.ton_kho, 0)


class VoucherEligibilityRuleTests(TestCase):
    def test_froster_voucher_requires_froster_product_in_cart(self):
        froster_brand = ThuongHieu.objects.create(ten="Froster Brand")
        other_brand = ThuongHieu.objects.create(ten="Other Brand")
        froster_product = SanPham.objects.create(
            ten="Ly Froster Cau Vong",
            gia_ban=30000,
            thuong_hieu=froster_brand,
        )
        other_product = SanPham.objects.create(
            ten="Banh Bao Trung Muoi",
            gia_ban=30000,
            thuong_hieu=froster_brand,
        )
        tokbokki_product = SanPham.objects.create(
            ten="Tokbokki Xuc Xich Sot Cay",
            gia_ban=50000,
            thuong_hieu=other_brand,
        )
        voucher = KhuyenMai.objects.create(
            ten="Mua 2 Tang 1: Froster Cau Vong",
            ma_code="FROSTER33",
            loai_giam="percent",
            gia_tri_giam=33,
            gia_tri_don_hang_toi_thieu=0,
            dang_ap_dung=True,
        )
        voucher.thuong_hieu.add(froster_brand)

        with self.assertRaises(ValidationError):
            _resolve_checkout_voucher(
                "FROSTER33",
                [
                    {"product": other_product, "quantity": 1, "unit_price": Decimal("30000"), "line_total": Decimal("30000")},
                    {"product": tokbokki_product, "quantity": 1, "unit_price": Decimal("50000"), "line_total": Decimal("50000")},
                ],
                Decimal("80000"),
            )

        applied_voucher, discount_amount = _resolve_checkout_voucher(
            "FROSTER33",
            [
                {"product": froster_product, "quantity": 1, "unit_price": Decimal("30000"), "line_total": Decimal("30000")},
                {"product": tokbokki_product, "quantity": 1, "unit_price": Decimal("50000"), "line_total": Decimal("50000")},
            ],
            Decimal("80000"),
        )

        self.assertEqual(applied_voucher.pk, voucher.pk)
        self.assertEqual(discount_amount, Decimal("9900"))


class TrashBehaviorTests(TestCase):
    def setUp(self):
        groups = _ensure_role_groups()
        self.admin = User.objects.create_user(
            username="admin_trash",
            password="Abc12345!",
            is_staff=True,
        )
        self.admin.groups.add(groups[ROLE_ADMIN])
        self.product = SanPham.objects.create(ten="San pham thung rac", gia_ban=12000)
        self.chain = ChuoiCuaHang.objects.create(ten="CHAIN TRASH")
        self.store = CuaHang.objects.create(
            chuoi=self.chain,
            ten="Cua hang trash",
            dia_chi="1 Test",
            quan_huyen="Quan 1",
            vi_do=10.77,
            kinh_do=106.70,
            hoat_dong_24h=True,
        )
        self.employee = NhanVien.objects.create(cua_hang=self.store, ho_ten="Nhan Vien Trash")

    def test_failed_stock_movement_delete_does_not_create_trash_record(self):
        import_row = GiaoDichKho.objects.create(
            san_pham=self.product,
            nhan_vien=self.employee,
            loai="import",
            so_luong=3,
            ghi_chu="Kh?i t?o t?n",
            chu_ky=_gif_file("sig1.gif"),
        )
        GiaoDichKho.objects.create(
            san_pham=self.product,
            cua_hang=self.store,
            loai="export",
            so_luong=1,
            ghi_chu="Xu?t l?",
        )

        self.client.force_login(self.admin)
        response = self.client.post(f"/admin/giao-dich-kho/{import_row.pk}/delete/", follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(GiaoDichKho.objects.filter(pk=import_row.pk).exists())
        self.assertEqual(TrashRecord.objects.count(), 0)

    @override_settings(TRASH_RETENTION_DAYS=7)
    def test_deleted_record_stays_in_trash_for_configured_days(self):
        self.client.force_login(self.admin)

        response = self.client.post(f"/admin/san-pham/{self.product.pk}/delete/", follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(SanPham.objects.filter(pk=self.product.pk).exists())
        trash = TrashRecord.objects.get()
        retention = trash.expires_at - trash.deleted_at
        self.assertGreaterEqual(retention, timezone.timedelta(days=6, hours=23))
        self.assertLessEqual(retention, timezone.timedelta(days=7, minutes=1))

    def test_purge_trash_command_removes_only_expired_records(self):
        expired = TrashRecord.objects.create(
            model_label="gis_store.sanpham",
            object_id="1",
            data={"ten": "Expired"},
            expires_at=timezone.now() - timezone.timedelta(days=1),
        )
        active = TrashRecord.objects.create(
            model_label="gis_store.sanpham",
            object_id="2",
            data={"ten": "Active"},
            expires_at=timezone.now() + timezone.timedelta(days=5),
        )

        call_command("purge_trash")

        self.assertFalse(TrashRecord.objects.filter(pk=expired.pk).exists())
        self.assertTrue(TrashRecord.objects.filter(pk=active.pk).exists())


class RestockAllProductsCommandTests(TestCase):
    def setUp(self):
        self.chain = ChuoiCuaHang.objects.create(ten="CHAIN CMD")
        self.store_1 = CuaHang.objects.create(
            chuoi=self.chain,
            ten="Store 1",
            dia_chi="1 Test",
            quan_huyen="Quan 1",
            vi_do=10.77,
            kinh_do=106.70,
            hoat_dong_24h=True,
        )
        self.store_2 = CuaHang.objects.create(
            chuoi=self.chain,
            ten="Store 2",
            dia_chi="2 Test",
            quan_huyen="Quan 3",
            vi_do=10.78,
            kinh_do=106.71,
            hoat_dong_24h=True,
        )
        self.product_1 = SanPham.objects.create(ten="SP 1", gia_ban=10000)
        self.product_2 = SanPham.objects.create(ten="SP 2", gia_ban=15000)

    def test_restock_command_brings_every_store_product_pair_to_target(self):
        existing_employee = NhanVien.objects.create(
            cua_hang=self.store_1,
            ho_ten="Nhan vien co san",
        )
        GiaoDichKho.objects.create(
            san_pham=self.product_1,
            cua_hang=self.store_1,
            nhan_vien=existing_employee,
            chu_ky=_gif_file("existing-stock.gif"),
            loai="import",
            so_luong=5,
            ghi_chu="Ton ban dau",
        )

        call_command("restock_all_products", target_stock=12)

        for store in (self.store_1, self.store_2):
            for product in (self.product_1, self.product_2):
                row = TonKhoCuaHang.objects.get(cua_hang=store, san_pham=product)
                self.assertEqual(row.ton_kho, 12)

        self.product_1.refresh_from_db()
        self.product_2.refresh_from_db()
        self.assertEqual(self.product_1.ton_kho, 24)
        self.assertEqual(self.product_2.ton_kho, 24)
        self.assertEqual(
            GiaoDichKho.objects.filter(
                loai="import",
                ghi_chu="Nhập bù cho các cửa hàng đang thiếu hàng",
            ).count(),
            4,
        )
        self.assertEqual(NhanVien.objects.filter(cua_hang=self.store_2).count(), 1)
        self.assertTrue(self.store_1.san_pham.filter(pk=self.product_1.pk).exists())
        self.assertTrue(self.store_2.san_pham.filter(pk=self.product_2.pk).exists())

    def test_restock_command_is_idempotent_for_existing_target_stock(self):
        call_command("restock_all_products", target_stock=8)
        first_count = GiaoDichKho.objects.count()

        call_command("restock_all_products", target_stock=8)

        self.assertEqual(GiaoDichKho.objects.count(), first_count)

    def test_restock_command_can_target_single_store(self):
        call_command("restock_all_products", target_stock=9, store_ids=[self.store_1.pk])

        self.assertEqual(TonKhoCuaHang.objects.filter(cua_hang=self.store_1).count(), 2)
        self.assertEqual(TonKhoCuaHang.objects.filter(cua_hang=self.store_2).count(), 0)

        for product in (self.product_1, self.product_2):
            row = TonKhoCuaHang.objects.get(cua_hang=self.store_1, san_pham=product)
            self.assertEqual(row.ton_kho, 9)

        self.product_1.refresh_from_db()
        self.product_2.refresh_from_db()
        self.assertEqual(self.product_1.ton_kho, 9)
        self.assertEqual(self.product_2.ton_kho, 9)

    def test_restock_command_can_target_multiple_stores(self):
        self.store_3 = CuaHang.objects.create(
            chuoi=self.chain,
            ten="Store 3",
            dia_chi="3 Test",
            quan_huyen="Quan 5",
            vi_do=10.79,
            kinh_do=106.72,
            hoat_dong_24h=True,
        )

        call_command(
            "restock_all_products",
            target_stock=6,
            store_ids_bulk=[self.store_1.pk, self.store_3.pk],
        )

        for store in (self.store_1, self.store_3):
            for product in (self.product_1, self.product_2):
                row = TonKhoCuaHang.objects.get(cua_hang=store, san_pham=product)
                self.assertEqual(row.ton_kho, 6)

        self.assertEqual(TonKhoCuaHang.objects.filter(cua_hang=self.store_2).count(), 0)

        self.product_1.refresh_from_db()
        self.product_2.refresh_from_db()
        self.assertEqual(self.product_1.ton_kho, 12)
        self.assertEqual(self.product_2.ton_kho, 12)

    def test_restock_command_reconciles_store_stock_before_importing(self):
        employee = NhanVien.objects.create(
            cua_hang=self.store_1,
            ho_ten="Nhan vien doi chieu",
        )
        GiaoDichKho.objects.create(
            san_pham=self.product_1,
            cua_hang=self.store_1,
            nhan_vien=employee,
            chu_ky=_gif_file("reconcile-1.gif"),
            loai="import",
            so_luong=3,
            ghi_chu="Ton thuc te la 3",
        )
        TonKhoCuaHang.objects.filter(
            cua_hang=self.store_1,
            san_pham=self.product_1,
        ).update(ton_kho=99)

        summary = restock_products(
            target_stock=10,
            trigger_threshold=5,
            note="Nhap bu sau doi chieu",
            store_ids=[self.store_1.pk],
        )

        self.assertEqual(summary["created_movements"], 2)
        self.assertEqual(summary["reconciled_stock_rows"], 2)
        self.assertEqual(
            TonKhoCuaHang.objects.get(cua_hang=self.store_1, san_pham=self.product_1).ton_kho,
            10,
        )
        self.product_1.refresh_from_db()
        self.product_2.refresh_from_db()
        self.assertEqual(self.product_1.ton_kho, 10)
        self.assertEqual(self.product_2.ton_kho, 10)
        self.assertTrue(
            GiaoDichKho.objects.filter(
                cua_hang=self.store_1,
                san_pham=self.product_1,
                ghi_chu="Nhap bu sau doi chieu",
                loai="import",
                so_luong=7,
            ).exists()
        )


class InventoryBulkRestockAdminTests(TestCase):
    def setUp(self):
        groups = _ensure_role_groups()
        self.admin = User.objects.create_user(
            username="admin_bulk_restock",
            password="Abc12345!",
            is_staff=True,
        )
        self.admin.groups.add(groups[ROLE_STOCK_MANAGER])

        self.chain = ChuoiCuaHang.objects.create(ten="CHAIN BULK UI")
        self.store_1 = CuaHang.objects.create(
            chuoi=self.chain,
            ten="Store Bulk 1",
            dia_chi="1 Test",
            quan_huyen="Quan 1",
            vi_do=10.77,
            kinh_do=106.70,
            hoat_dong_24h=True,
        )
        self.store_2 = CuaHang.objects.create(
            chuoi=self.chain,
            ten="Store Bulk 2",
            dia_chi="2 Test",
            quan_huyen="Quan 3",
            vi_do=10.78,
            kinh_do=106.71,
            hoat_dong_24h=True,
        )
        self.product = SanPham.objects.create(ten="SP Bulk", gia_ban=10000)

    def test_inventory_restock_page_renders_for_stock_manager(self):
        self.client.force_login(self.admin)

        response = self.client.get("/admin/inventory/restock/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Nhập kho theo cửa hàng")
        self.assertContains(response, self.store_1.ten)
        self.assertContains(response, self.store_2.ten)

    def test_inventory_restock_page_can_restock_selected_stores_only(self):
        self.client.force_login(self.admin)

        response = self.client.post(
            "/admin/inventory/restock/",
            {
                "target_stock": "7",
                "note": "Nhap kho tu admin web",
                "store_ids": [str(self.store_1.pk)],
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(TonKhoCuaHang.objects.filter(cua_hang=self.store_1, san_pham=self.product).count(), 1)
        self.assertEqual(TonKhoCuaHang.objects.get(cua_hang=self.store_1, san_pham=self.product).ton_kho, 7)
        self.assertEqual(TonKhoCuaHang.objects.filter(cua_hang=self.store_2, san_pham=self.product).count(), 0)

        self.product.refresh_from_db()
        self.assertEqual(self.product.ton_kho, 7)
        self.assertTrue(
            GiaoDichKho.objects.filter(
                cua_hang=self.store_1,
                san_pham=self.product,
                ghi_chu="Nhap kho tu admin web",
                loai="import",
            ).exists()
        )


class InventoryAdminUiTests(TestCase):
    def setUp(self):
        groups = _ensure_role_groups()
        self.admin = User.objects.create_user(
            username="admin_inventory_ui",
            password="Abc12345!",
            is_staff=True,
        )
        self.admin.groups.add(groups[ROLE_ADMIN])
        self.chain = ChuoiCuaHang.objects.create(ten="CHAIN INV UI")
        self.store = CuaHang.objects.create(
            chuoi=self.chain,
            ten="Cua hang inv ui",
            dia_chi="1 Test",
            quan_huyen="Quan 1",
            vi_do=10.77,
            kinh_do=106.70,
            hoat_dong_24h=True,
        )
        self.employee = NhanVien.objects.create(cua_hang=self.store, ho_ten="Nhan Vien In Phieu")
        self.product = SanPham.objects.create(ten="San pham in phieu", gia_ban=25000)
        self.movement = GiaoDichKho.objects.create(
            san_pham=self.product,
            nhan_vien=self.employee,
            chu_ky=_gif_file("print.gif"),
            loai="import",
            so_luong=5,
            ghi_chu="Nhap kho de in phieu",
            created_by=self.admin,
        )

    def test_inventory_list_shows_signature_preview_and_print_action(self):
        self.client.force_login(self.admin)

        response = self.client.get("/admin/giao-dich-kho/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.movement.chu_ky.url)
        self.assertContains(response, f"/admin/inventory/{self.movement.pk}/print/")

    def test_inventory_print_page_renders_import_slip(self):
        self.client.force_login(self.admin)

        response = self.client.get(f"/admin/inventory/{self.movement.pk}/print/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f"PNK-{self.movement.pk}")
        self.assertContains(response, self.product.ten)
        self.assertContains(response, self.employee.ho_ten)

    def test_inventory_pdf_download_supports_unicode_content(self):
        self.client.force_login(self.admin)
        self.product.ten = "Sữa gạo đặc biệt"
        self.product.save(update_fields=["ten"])
        self.employee.ho_ten = "Nguyễn Văn Kho"
        self.employee.save(update_fields=["ho_ten"])
        self.movement.ghi_chu = "Nhập kho lô đầu tiên cho quầy mới"
        self.movement.save(update_fields=["ghi_chu"])

        response = self.client.get(f"/admin/inventory/{self.movement.pk}/pdf/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertIn(f'phieu-nhap-kho-{self.movement.pk}.pdf', response["Content-Disposition"])
        self.assertTrue(response.content.startswith(b"%PDF"))

    def test_inventory_hub_shows_system_total_and_per_store_average(self):
        second_store = CuaHang.objects.create(
            chuoi=self.chain,
            ten="Cua hang inv ui 2",
            dia_chi="2 Test",
            quan_huyen="Quan 3",
            vi_do=10.78,
            kinh_do=106.71,
            hoat_dong_24h=True,
        )
        second_employee = NhanVien.objects.create(cua_hang=second_store, ho_ten="Nhan Vien In Phieu 2")
        GiaoDichKho.objects.create(
            san_pham=self.product,
            nhan_vien=second_employee,
            chu_ky=_gif_file("print-2.gif"),
            loai="import",
            so_luong=45,
            ghi_chu="Nhap them cho cua hang 2",
            created_by=self.admin,
        )
        self.client.force_login(self.admin)

        response = self.client.get("/admin/inventory/")

        self.assertEqual(response.status_code, 200)
        product = next(item for item in response.context["export_suggestions"] if item.pk == self.product.pk)
        self.assertEqual(product.ton_kho, 50)
        self.assertEqual(product.avg_store_stock_display, 25)
        self.assertEqual(product.stores_with_stock_count, 2)
        self.assertContains(response, "Tổng tồn toàn hệ thống")
        self.assertContains(response, "TB / cửa hàng còn hàng")

    def test_inventory_report_filters_by_local_day_boundaries(self):
        self.client.force_login(self.admin)
        timezone.activate("Asia/Ho_Chi_Minh")
        try:
            boundary_dt = timezone.make_aware(datetime(2026, 4, 28, 0, 30))
            GiaoDichKho.objects.filter(pk=self.movement.pk).update(created_at=boundary_dt)

            response = self.client.get(
                "/admin/inventory/report/",
                {"start": "2026-04-28", "end": "2026-04-28", "store_id": str(self.store.pk)},
            )

            self.assertEqual(response.status_code, 200)
            rows = list(response.context["daily_rows"])
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["day"].isoformat(), "2026-04-28")
            self.assertEqual(rows[0]["import_total"], 5)
        finally:
            timezone.deactivate()

    def test_inventory_hub_flags_branch_shortage_even_when_system_stock_is_high(self):
        second_store = CuaHang.objects.create(
            chuoi=self.chain,
            ten="Cua hang inv ui shortage",
            dia_chi="3 Test",
            quan_huyen="Quan 5",
            vi_do=10.79,
            kinh_do=106.72,
            hoat_dong_24h=True,
        )
        second_employee = NhanVien.objects.create(cua_hang=second_store, ho_ten="Nhan Vien Thieu Hang")
        shortage_product = SanPham.objects.create(ten="San pham thieu theo cua hang", gia_ban=32000)
        GiaoDichKho.objects.create(
            san_pham=shortage_product,
            nhan_vien=self.employee,
            chu_ky=_gif_file("shortage-1.gif"),
            loai="import",
            so_luong=40,
            ghi_chu="Ton cao tai cua hang 1",
            created_by=self.admin,
        )
        GiaoDichKho.objects.create(
            san_pham=shortage_product,
            nhan_vien=second_employee,
            chu_ky=_gif_file("shortage-2.gif"),
            loai="import",
            so_luong=2,
            ghi_chu="Ton thap tai cua hang 2",
            created_by=self.admin,
        )
        self.client.force_login(self.admin)

        response = self.client.get("/admin/inventory/")

        self.assertEqual(response.status_code, 200)
        suggestion = next(
            item
            for item in response.context["import_suggestions"]
            if item.san_pham_id == shortage_product.pk and item.cua_hang_id == second_store.pk
        )
        self.assertEqual(suggestion.product_total_stock, 42)
        self.assertEqual(suggestion.current_stock, 2)
        self.assertEqual(suggestion.recommended_restock, 23)
        self.assertEqual(suggestion.store_display, second_store.ten)
        self.assertEqual(suggestion.product.ten, shortage_product.ten)
        self.assertEqual(response.context["inventory_stats"]["low_stock_count"], 2)
        self.assertEqual(response.context["inventory_stats"]["out_of_stock_count"], 0)
        self.assertContains(response, second_store.ten)
        self.assertContains(response, shortage_product.ten)

    def test_dashboard_uses_same_branch_shortage_logic_as_inventory_hub(self):
        second_store = CuaHang.objects.create(
            chuoi=self.chain,
            ten="Cua hang dashboard shortage",
            dia_chi="4 Test",
            quan_huyen="Quan 6",
            vi_do=10.80,
            kinh_do=106.73,
            hoat_dong_24h=True,
        )
        second_employee = NhanVien.objects.create(cua_hang=second_store, ho_ten="Nhan Vien Dashboard")
        shortage_product = SanPham.objects.create(ten="San pham thong ke dong bo", gia_ban=33000)
        GiaoDichKho.objects.create(
            san_pham=shortage_product,
            nhan_vien=self.employee,
            chu_ky=_gif_file("dashboard-shortage-1.gif"),
            loai="import",
            so_luong=40,
            ghi_chu="Ton cao tai cua hang 1",
            created_by=self.admin,
        )
        GiaoDichKho.objects.create(
            san_pham=shortage_product,
            nhan_vien=second_employee,
            chu_ky=_gif_file("dashboard-shortage-2.gif"),
            loai="import",
            so_luong=2,
            ghi_chu="Ton thap tai cua hang 2",
            created_by=self.admin,
        )
        self.client.force_login(self.admin)

        dashboard_response = self.client.get("/admin/")
        inventory_response = self.client.get("/admin/inventory/")

        self.assertEqual(dashboard_response.status_code, 200)
        self.assertEqual(inventory_response.status_code, 200)
        self.assertEqual(dashboard_response.context["dashboard_stats"]["low_stock_count"], 2)
        self.assertEqual(dashboard_response.context["dashboard_stats"]["out_stock_count"], 0)
        self.assertEqual(
            dashboard_response.context["dashboard_stats"]["low_stock_count"],
            inventory_response.context["inventory_stats"]["low_stock_count"],
        )
        self.assertEqual(
            dashboard_response.context["dashboard_stats"]["out_stock_count"],
            inventory_response.context["inventory_stats"]["out_of_stock_count"],
        )


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    DEFAULT_FROM_EMAIL="noreply@example.com",
    FEEDBACK_NOTIFICATION_EMAIL="support@example.com",
)
class FeedbackFlowTests(TestCase):
    def test_feedback_page_ok(self):
        response = self.client.get("/feedback/")
        self.assertEqual(response.status_code, 200)

    def test_feedback_submission_saves_and_sends_mail(self):
        response = self.client.post(
            "/feedback/",
            {
                "ho_ten": "Nguyen Van A",
                "email": "nguyenvana@example.com",
                "so_dien_thoai": "0900000000",
                "chu_de": "Góp ý về dịch vụ",
                "noi_dung": "Nhân viên hỗ trợ rất nhiệt tình.",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(GopYKhachHang.objects.count(), 1)
        feedback = GopYKhachHang.objects.first()
        self.assertEqual(feedback.ho_ten, "Nguyen Van A")
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[0].to, ["nguyenvana@example.com"])
        self.assertEqual(mail.outbox[1].to, ["support@example.com"])

    def test_feedback_submission_validates_required_fields(self):
        response = self.client.post(
            "/feedback/",
            {
                "ho_ten": "",
                "email": "sai-dinh-dang",
                "chu_de": "",
                "noi_dung": "",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Vui lòng nhập họ tên.")
        self.assertContains(response, "Email không đúng định dạng.")
        self.assertContains(response, "Vui lòng nhập chủ đề.")
        self.assertContains(response, "Vui lòng nhập nội dung góp ý.")
        self.assertEqual(GopYKhachHang.objects.count(), 0)
