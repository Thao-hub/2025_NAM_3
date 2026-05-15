from dataclasses import fields

from django.shortcuts import render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST

from modules.store.management.commands.restock_all_products import restock_products


def store_list_page(request):
    pref = _admin_pref_context(request)
    qs = CuaHang.objects.select_related("chuoi").order_by("ten")
    paginator = Paginator(qs, 12)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(
        request,
        "store/store_list.html",
        {
            "stores": page_obj.object_list,
            "page_obj": page_obj,
            "paginator": paginator,
            "cart_total_quantity": _cart_items(request)[1],
            **pref,
        },
    )


def store_detail_page(request, pk):
    pref = _admin_pref_context(request)
    store = get_object_or_404(CuaHang.objects.select_related("chuoi"), pk=pk)
    store_staff = list(NhanVien.objects.filter(cua_hang=store).order_by("ho_ten"))

    stock_rows = list(
        TonKhoCuaHang.objects.filter(cua_hang=store, ton_kho__gt=0)
        .select_related("san_pham__thuong_hieu", "san_pham__nhom_san_pham")
        .prefetch_related("san_pham__hinh_anh_phu")
        .order_by("-ton_kho", "san_pham__ten")
    )
    products = []
    if stock_rows:
        for row in stock_rows[:12]:
            product = row.san_pham
            product.display_price = _format_currency(product.gia_ban)
            product.store_stock = row.ton_kho
            product.card_gallery = _build_product_card_gallery(product)
            products.append(product)
    else:
        fallback_products = list(
            store.san_pham.select_related("thuong_hieu", "nhom_san_pham")
            .prefetch_related("hinh_anh_phu")
            .order_by("ten")[:12]
        )
        for product in fallback_products:
            product.display_price = _format_currency(product.gia_ban)
            product.store_stock = product.ton_kho
            product.card_gallery = _build_product_card_gallery(product)
            products.append(product)

    reviews = list(
        store.danh_gia.select_related("user")
        .prefetch_related("tep_dinh_kem")
        .order_by("-created_at")[:6]
    )
    total_stars = 0
    review_media_count = 0
    for review in reviews:
        total_stars += review.so_sao or 0
        review.media_items = _build_review_media_context(review)
        review.preview_media = review.media_items[:3]
        review.display_created = timezone.localtime(review.created_at).strftime("%d/%m/%Y %H:%M")
        review_media_count += len(review.media_items)
    review_count = store.danh_gia.count()
    average_rating = round((sum(item.so_sao or 0 for item in store.danh_gia.all()) / review_count), 1) if review_count else 0

    promotions = list(
        KhuyenMai.objects.filter(dang_ap_dung=True)
        .filter(Q(cua_hang=store) | Q(thuong_hieu__in=[p.thuong_hieu_id for p in products if p.thuong_hieu_id]))
        .distinct()
        .order_by("-ngay_bat_dau", "ten")[:6]
    )
    for promo in promotions:
        promo.display_discount = _format_currency(promo.gia_tri_giam)
        promo.display_min_order = _format_currency(promo.gia_tri_don_hang_toi_thieu)
        promo.display_cap = _format_currency(promo.giam_toi_da) if promo.giam_toi_da else ""

    processing_orders = DonHang.objects.filter(cua_hang_xu_ly=store).count()
    employee_count = len(store_staff)
    primary_staff = store_staff[0] if store_staff else None

    store_logo_url = ""
    try:
        if store.chuoi.logo:
            store_logo_url = store.chuoi.logo.url
    except Exception:
        store_logo_url = ""

    _, cart_total_quantity, _ = _cart_items(request)
    return render(
        request,
        "store/store_detail.html",
        {
            "store": store,
            "store_products": products,
            "store_reviews": reviews,
            "store_promotions": promotions,
            "store_logo_url": store_logo_url,
            "average_rating": average_rating,
            "review_count": review_count,
            "processing_orders": processing_orders,
            "employee_count": employee_count,
            "review_media_count": review_media_count,
            "store_staff": store_staff[:6],
            "primary_staff": primary_staff,
            "cart_total_quantity": cart_total_quantity,
            "user_notifications": _user_header_notifications(request.user) if request.user.is_authenticated else [],
            **pref,
        },
    )


@never_cache
def map_page(request):
    return render(
        request,
        "store/map.html",
        {
            "cart_total_quantity": _cart_items(request)[1],
            **_admin_pref_context(request),
        },
    )


@never_cache
def geocode_address_api(request):
    query = (request.GET.get("q") or "").strip()
    raw_limit = (request.GET.get("limit") or "").strip()
    try:
        limit = int(raw_limit or 5)
    except (TypeError, ValueError):
        limit = 5
    limit = max(1, min(limit, 8))

    if not query:
        return JsonResponse({"ok": True, "results": []})

    url = "https://nominatim.openstreetmap.org/search?" + urlencode(
        {
            "format": "jsonv2",
            "limit": limit,
            "addressdetails": 1,
            "countrycodes": "vn",
            "accept-language": "vi",
            "q": query,
        }
    )
    req = Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "webgis-store-locator/1.0",
        },
    )

    try:
        with urlopen(req, timeout=8) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except Exception:
        return JsonResponse(
            {"ok": False, "error": "Không lấy được gợi ý địa chỉ lúc này.", "results": []},
            status=502,
        )

    results = []
    for item in payload if isinstance(payload, list) else []:
        try:
            lat = float(item.get("lat"))
            lon = float(item.get("lon"))
        except (TypeError, ValueError):
            continue
        results.append(
            {
                "lat": lat,
                "lon": lon,
                "display_name": item.get("display_name") or "",
                "address": item.get("address") or {},
            }
        )

    return JsonResponse({"ok": True, "results": results})


def _fetch_json_from_url(url):
    req = Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "webgis-store-locator/1.0",
        },
    )
    with urlopen(req, timeout=8) as response:
        return json.loads(response.read().decode("utf-8"))


@never_cache
def region_provinces_api(request):
    try:
        payload = _fetch_json_from_url("https://provinces.open-api.vn/api/v1/?depth=1")
    except Exception:
        return JsonResponse({"ok": False, "items": [], "error": "Không tải được danh sách tỉnh/thành."}, status=502)
    return JsonResponse({"ok": True, "items": payload if isinstance(payload, list) else []})


@never_cache
def region_districts_api(request, province_code):
    try:
        payload = _fetch_json_from_url(f"https://provinces.open-api.vn/api/v1/p/{province_code}?depth=2")
    except Exception:
        return JsonResponse({"ok": False, "items": [], "error": "Không tải được danh sách quận/huyện."}, status=502)
    return JsonResponse({"ok": True, "items": payload.get("districts") if isinstance(payload, dict) else []})


@never_cache
def region_wards_api(request, district_code):
    try:
        payload = _fetch_json_from_url(f"https://provinces.open-api.vn/api/v1/d/{district_code}?depth=2")
    except Exception:
        return JsonResponse({"ok": False, "items": [], "error": "Không tải được danh sách khu vực."}, status=502)
    return JsonResponse({"ok": True, "items": payload.get("wards") if isinstance(payload, dict) else []})


@never_cache
def store_reviews_api(request, pk):
    store = get_object_or_404(CuaHang.objects.select_related("chuoi"), pk=pk)
    return JsonResponse(
        {
            "ok": True,
            "message": "OK",
            **_store_review_payload(store, request.user),
        }
    )


@require_POST
@never_cache
def store_reviews_create(request, pk):
    if not _is_regular_user(request.user):
        return JsonResponse(
            {"ok": False, "error": "Vui lòng đăng nhập tài khoản người dùng để đánh giá cửa hàng."},
            status=401,
        )

    store = get_object_or_404(CuaHang.objects.select_related("chuoi"), pk=pk)
    try:
        stars = int(request.POST.get("stars") or 0)
    except (TypeError, ValueError):
        stars = 0
    comment = (request.POST.get("comment") or "").strip()
    media_files = request.FILES.getlist("media")

    if stars < 1 or stars > 5:
        return JsonResponse({"ok": False, "error": "Số sao phải nằm trong khoảng từ 1 đến 5."}, status=400)
    if not comment and not media_files:
        return JsonResponse({"ok": False, "error": "Vui lòng nhập bình luận hoặc tải lên ít nhất một ảnh/video."}, status=400)

    invalid_files = [uploaded.name for uploaded in media_files if not _review_media_kind(uploaded)]
    if invalid_files:
        return JsonResponse(
            {"ok": False, "error": f"Chỉ hỗ trợ ảnh hoặc video. File không hợp lệ: {', '.join(invalid_files[:3])}"},
            status=400,
        )

    with transaction.atomic():
        review = DanhGiaCuaHang.objects.create(
            cua_hang=store,
            user=request.user,
            so_sao=stars,
            binh_luan=comment,
        )
        for uploaded in media_files:
            TepDanhGiaCuaHang.objects.create(
                danh_gia=review,
                tep=uploaded,
                loai=_review_media_kind(uploaded),
            )
        reviewer_name = _user_display_name(request.user)
        media_count = len(media_files)
        media_text = f", kèm {media_count} tệp ảnh/video" if media_count else ""
        comment_preview = comment[:120] if comment else "Không có bình luận văn bản."
        _create_admin_notification(
            f"Đánh giá mới cho cửa hàng {store.ten}",
            (
                f"{reviewer_name} vừa gửi đánh giá {stars} sao cho {store.ten}{media_text}. "
                f"Nội dung: {comment_preview}"
            ),
            level="info",
            path=f"{reverse('store:admin_list', kwargs={'model_slug': 'danh-gia-cua-hang'})}?focus_review={review.pk}",
            method="POST",
            status_code=201,
        )

    return JsonResponse(
        {
            "ok": True,
            "message": "Đã gửi đánh giá cửa hàng.",
            **_store_review_payload(store, request.user),
        }
    )


INFO_PAGES = {
    "gioi-thieu-circle-k": {
        "title": "Giới thiệu Circle K",
        "kicker": "Về Chúng Tôi",
        "summary": "Từ cửa hàng đầu tiên tại Texas (1951), Circle K phát triển thành thương hiệu cửa hàng tiện lợi toàn cầu và đang mở rộng mạnh tại Việt Nam.",
        "sections": [
            {
                "heading": "Circle K Toàn Cầu",
                "content": "Circle K hiện diện tại nhiều quốc gia như Mỹ, Canada, Mexico, châu Âu, Nhật Bản, Đài Loan và nhiều thị trường khác, phục vụ hàng triệu khách hàng mỗi ngày.",
            },
            {
                "heading": "Lịch sử phát triển",
                "content": "Trong hơn 70 năm, thương hiệu không ngừng mở rộng hệ thống, chuẩn hóa vận hành và nâng cấp trải nghiệm mua sắm tiện lợi 24/7 cho cộng đồng đô thị.",
            },
            {
                "heading": "Circle K Việt Nam",
                "content": "Circle K Việt Nam hoạt động từ năm 2008 và phát triển nhanh tại TP.HCM cùng nhiều tỉnh thành lớn, tập trung vào nhu cầu mua sắm linh hoạt của người trẻ và dân văn phòng.",
            },
            {
                "heading": "Điểm khác biệt",
                "content": "Hệ thống mở cửa 24/7, danh mục sản phẩm đa dạng, vị trí thuận tiện và dịch vụ thân thiện giúp khách hàng mua nhanh, dùng ngay, tiết kiệm thời gian.",
            },
            {
                "heading": "Tầm nhìn",
                "content": "Trở thành chuỗi cửa hàng tiện lợi được ưu tiên lựa chọn hàng đầu tại Việt Nam bằng mô hình vận hành hiệu quả, tiêu chuẩn dịch vụ ổn định và đổi mới liên tục.",
            },
            {
                "heading": "Sứ mệnh tại Việt Nam",
                "content": "Cung cấp sản phẩm và dịch vụ đáng tin cậy với tốc độ nhanh, góp phần nâng cao chất lượng sống của khách hàng trong từng khu phố và điểm dân cư.",
            },
        ],
    },
    "tin-tuc-su-kien": {
        "title": "Tin tức và Sự kiện",
        "kicker": "Cập Nhật",
        "summary": "Tổng hợp thông tin nổi bật về chương trình khuyến mãi, hoạt động cộng đồng và sự kiện mới trong hệ thống Circle K và GS25.",
        "sections": [
            {
                "heading": "Khuyến mãi theo mùa",
                "content": "Ưu đãi theo tuần, combo giờ vàng và các chương trình đồng giá cho nhóm sản phẩm thiết yếu.",
            },
            {
                "heading": "Sự kiện tại cửa hàng",
                "content": "Mini game, trải nghiệm sản phẩm mới, hoạt động tri ân khách hàng tại các điểm bán trọng điểm.",
            },
            {
                "heading": "Hoạt động cộng đồng",
                "content": "Chiến dịch xanh, hỗ trợ sinh viên và các chương trình đồng hành cùng khu dân cư địa phương.",
            },
        ],
    },
    "tuyen-dung": {
        "title": "Tuyển dụng",
        "kicker": "Cơ Hội Nghề Nghiệp",
        "summary": "Làm việc tại Circle K là cơ hội phát triển trong môi trường năng động, tôn trọng con người và có lộ trình nghề nghiệp rõ ràng.",
        "sections": [
            {
                "heading": "Môi trường làm việc",
                "content": "Đội ngũ trẻ, tinh thần hợp tác cao, quy trình chuyên nghiệp và văn hóa hỗ trợ lẫn nhau giúp nhân sự mới nhanh hòa nhập và phát huy năng lực.",
            },
            {
                "heading": "4 Giá trị EVP",
                "content": "Phúc lợi cạnh tranh, phát triển sự nghiệp, văn hóa tích cực và ghi nhận thành tích là nền tảng giữ chân và tạo động lực cho nhân viên.",
            },
            {
                "heading": "Phúc lợi nổi bật",
                "content": "Hỗ trợ theo ca, đào tạo định kỳ, phụ cấp theo vị trí, chế độ thưởng hiệu suất và chính sách gắn bó dành cho nhân sự ổn định lâu dài.",
            },
            {
                "heading": "Lộ trình phát triển",
                "content": "Từ nhân viên cửa hàng có thể thăng tiến lên ca trưởng, quản lý cửa hàng, giám sát khu vực hoặc chuyển sang các bộ phận vận hành và văn phòng.",
            },
            {
                "heading": "Vị trí tuyển dụng",
                "content": "Nhân viên bán hàng, ca trưởng, quản lý cửa hàng, hỗ trợ vận hành, marketing, chuỗi cung ứng và các vị trí chuyên môn khác theo từng giai đoạn.",
            },
            {
                "heading": "Cách ứng tuyển",
                "content": "Ứng viên có thể nộp hồ sơ trực tuyến, gửi email tuyển dụng hoặc đăng ký trực tiếp tại cửa hàng gần nhất để được hướng dẫn phỏng vấn.",
            },
        ],
    },
    "chinh-sach-bao-mat": {
        "title": "Chính sách bảo mật",
        "kicker": "Bảo Mật Dữ Liệu",
        "summary": "Cam kết bảo vệ thông tin cá nhân của khách hàng khi truy cập website, đăng ký nhận tin và sử dụng dịch vụ trực tuyến.",
        "sections": [
            {
                "heading": "Phạm vi thu thập",
                "content": "Chỉ thu thập thông tin cần thiết để xử lý yêu cầu, chăm sóc khách hàng và nâng cao chất lượng dịch vụ.",
            },
            {
                "heading": "Mục đích sử dụng",
                "content": "Dùng cho xác nhận liên hệ, gửi thông báo dịch vụ, cải thiện trải nghiệm và tuân thủ quy định pháp luật.",
            },
            {
                "heading": "Bảo vệ thông tin",
                "content": "Áp dụng biện pháp kỹ thuật và quy trình nội bộ để ngăn truy cập trái phép, rò rỉ hoặc lạm dụng dữ liệu.",
            },
        ],
    },
    "chinh-sach-thanh-toan": {
        "title": "Chính sách thanh toán",
        "kicker": "Thanh Toán",
        "summary": "Quy định về phương thức thanh toán, xác nhận giao dịch và xử lý các vấn đề phát sinh liên quan đến thanh toán.",
        "sections": [
            {
                "heading": "Phương thức hỗ trợ",
                "content": "Tiền mặt, thẻ ngân hàng, ví điện tử và các hình thức thanh toán số được chấp nhận theo từng cửa hàng.",
            },
            {
                "heading": "Xác nhận giao dịch",
                "content": "Mọi giao dịch được ghi nhận trên hệ thống và thể hiện bằng hóa đơn hoặc biên nhận điện tử tương ứng.",
            },
            {
                "heading": "Xử lý sai lệch",
                "content": "Trường hợp thanh toán lỗi hoặc trừ tiền bất thường sẽ được tiếp nhận, kiểm tra và phản hồi theo quy trình hỗ trợ.",
            },
        ],
    },
    "dieu-khoan-su-dung": {
        "title": "Điều khoản sử dụng",
        "kicker": "Điều Khoản",
        "summary": "Các điều kiện áp dụng khi truy cập website và sử dụng nội dung, công cụ tra cứu cửa hàng và dịch vụ liên quan.",
        "sections": [
            {
                "heading": "Quyền và trách nhiệm",
                "content": "Người dùng có trách nhiệm cung cấp thông tin đúng mục đích, không sử dụng website vào hành vi gây hại.",
            },
            {
                "heading": "Nội dung và bản quyền",
                "content": "Mọi nội dung hiển thị thuộc quyền quản lý của hệ thống, nghiêm cấm sao chép trái phép khi chưa được chấp thuận.",
            },
            {
                "heading": "Cập nhật điều khoản",
                "content": "Điều khoản có thể được cập nhật theo nhu cầu vận hành và quy định pháp lý, phiên bản mới có hiệu lực khi công bố.",
            },
        ],
    },
}


PAGE_MEDIA = {
    "gioi-thieu-circle-k": {
        "hero_image": "https://images.unsplash.com/photo-1542838132-92c53300491e?auto=format&fit=crop&w=1400&q=80",
        "section_images": [
            "https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=900&q=80",
            "https://images.unsplash.com/photo-1441986300917-64674bd600d8?auto=format&fit=crop&w=900&q=80",
            "https://images.unsplash.com/photo-1556740738-b6a63e27c4df?auto=format&fit=crop&w=900&q=80",
        ],
    },
    "tin-tuc-su-kien": {
        "hero_image": "https://images.unsplash.com/photo-1492684223066-81342ee5ff30?auto=format&fit=crop&w=1400&q=80",
        "section_images": [
            "https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=900&q=80",
            "https://images.unsplash.com/photo-1511578314322-379afb476865?auto=format&fit=crop&w=900&q=80",
            "https://images.unsplash.com/photo-1529390079861-591de354faf5?auto=format&fit=crop&w=900&q=80",
        ],
    },
    "tuyen-dung": {
        "hero_image": "https://images.unsplash.com/photo-1521737604893-d14cc237f11d?auto=format&fit=crop&w=1400&q=80",
        "section_images": [
            "https://images.unsplash.com/photo-1552664730-d307ca884978?auto=format&fit=crop&w=900&q=80",
            "https://images.unsplash.com/photo-1522071820081-009f0129c71c?auto=format&fit=crop&w=900&q=80",
            "https://images.unsplash.com/photo-1557804506-669a67965ba0?auto=format&fit=crop&w=900&q=80",
        ],
    },
    "chinh-sach-bao-mat": {
        "hero_image": "https://images.unsplash.com/photo-1563013544-824ae1b704d3?auto=format&fit=crop&w=1400&q=80",
        "section_images": [
            "https://images.unsplash.com/photo-1510511459019-5dda7724fd87?auto=format&fit=crop&w=900&q=80",
            "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?auto=format&fit=crop&w=900&q=80",
            "https://images.unsplash.com/photo-1633265486064-086b219458ec?auto=format&fit=crop&w=900&q=80",
        ],
    },
    "chinh-sach-thanh-toan": {
        "hero_image": "https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?auto=format&fit=crop&w=1400&q=80",
        "section_images": [
            "https://images.unsplash.com/photo-1559526324-593bc073d938?auto=format&fit=crop&w=900&q=80",
            "https://images.unsplash.com/photo-1563013544-824ae1b704d3?auto=format&fit=crop&w=900&q=80",
            "https://images.unsplash.com/photo-1579621970795-87facc2f976d?auto=format&fit=crop&w=900&q=80",
        ],
    },
    "dieu-khoan-su-dung": {
        "hero_image": "https://images.unsplash.com/photo-1450101499163-c8848c66ca85?auto=format&fit=crop&w=1400&q=80",
        "section_images": [
            "https://images.unsplash.com/photo-1589578527966-fdac0f44566c?auto=format&fit=crop&w=900&q=80",
            "https://images.unsplash.com/photo-1521791136064-7986c2920216?auto=format&fit=crop&w=900&q=80",
            "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?auto=format&fit=crop&w=900&q=80",
        ],
    },
}


NEWS_EVENTS = {
    "featured": {
        "title": "Circle K Việt Nam bổ nhiệm tân Tổng Giám đốc, đặt mục tiêu mở rộng lên 1.000 cửa hàng",
        "excerpt": "Circle K Việt Nam công bố lãnh đạo mới cho giai đoạn tăng trưởng tiếp theo, tập trung mở rộng mạng lưới, chuẩn hóa vận hành và nâng cao trải nghiệm khách hàng.",
        "image": "https://images.unsplash.com/photo-1556740738-b6a63e27c4df?auto=format&fit=crop&w=1400&q=80",
        "category": "Tin doanh nghiệp",
    },
    "items": [
        {
            "title": "Circle K x What It IsNt: đồng phục mới 2025",
            "excerpt": "Bộ đồng phục mới lấy cảm hứng từ văn hóa đường phố, tăng nhận diện thương hiệu và sự linh hoạt khi vận hành tại cửa hàng.",
            "image": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?auto=format&fit=crop&w=1000&q=80",
            "category": "Văn hóa",
        },
        {
            "title": "Thư viện Ước Mơ đến với học sinh Ba Vì",
            "excerpt": "Hoạt động cộng đồng hỗ trợ sách và không gian đọc cho học sinh, tiếp tục hành trình phát triển bền vững tại địa phương.",
            "image": "https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?auto=format&fit=crop&w=1000&q=80",
            "category": "Cộng đồng",
        },
        {
            "title": "Circle K hợp tác cùng đối tác bất động sản đô thị",
            "excerpt": "Mô hình cửa hàng tiện lợi trong khu dân cư và tòa nhà văn phòng giúp khách hàng tiếp cận dịch vụ nhanh hơn.",
            "image": "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=1000&q=80",
            "category": "Hợp tác",
        },
        {
            "title": "Nước sạch đến trường: chương trình vì cộng đồng",
            "excerpt": "Dự án tài trợ máy lọc nước và nâng cao điều kiện sinh hoạt học đường tại các khu vực còn hạn chế nguồn nước sạch.",
            "image": "https://images.unsplash.com/photo-1473445361085-b9a07f55608b?auto=format&fit=crop&w=1000&q=80",
            "category": "CSR",
        },
        {
            "title": "Ưu đãi tháng mới cho nhóm sản phẩm ăn nhanh",
            "excerpt": "Loạt combo hotdog, gà rán, cà phê và đồ uống mát với mức giá tối ưu cho khách hàng trẻ và dân văn phòng.",
            "image": "https://images.unsplash.com/photo-1525059696034-4967a8e1dca2?auto=format&fit=crop&w=1000&q=80",
            "category": "Ưu đãi",
        },
        {
            "title": "Mở rộng khung giờ chăm sóc khách hàng",
            "excerpt": "Kênh tiếp nhận phản hồi được tăng cường theo nhiều nền tảng để xử lý yêu cầu nhanh và nhất quán hơn.",
            "image": "https://images.unsplash.com/photo-1552581234-26160f608093?auto=format&fit=crop&w=1000&q=80",
            "category": "Dịch vụ",
        },
    ],
}


NEWS_DETAILS = {
    "bo-nhiem-tan-tong-giam-doc-1000-cua-hang": {
        "lead": "Circle K Việt Nam chính thức bổ nhiệm ông TC Cheng vào vị trí Tổng Giám đốc mới từ ngày 30 tháng 10 năm 2025, đánh dấu bước chuyển quan trọng trong giai đoạn tăng trưởng tiếp theo.",
        "paragraphs": [
            "Trong vai trò mới, ông TC sẽ điều hành toàn bộ hoạt động của Circle K Việt Nam với trọng tâm là mở rộng mạng lưới, nâng chuẩn vận hành và nâng cao trải nghiệm khách hàng trên toàn quốc.",
            "Với hơn 35 năm kinh nghiệm quản trị bán lẻ tại nhiều thị trường lớn, ông TC từng đảm nhiệm các vai trò lãnh đạo chiến lược trong các mô hình cửa hàng tiện lợi, siêu thị và thương mại điện tử.",
            "Mục tiêu giai đoạn mới là mở rộng lên 1.000 cửa hàng, đồng thời đẩy mạnh chuyển đổi số, chuẩn hóa vận hành chuỗi và tăng cường năng lực đội ngũ.",
            "Circle K cam kết tiếp tục mang đến dịch vụ tiện lợi chất lượng cao, lấy khách hàng làm trung tâm và duy trì vai trò tiên phong trong ngành bán lẻ tiện lợi.",
        ],
        "images": [
            "https://images.unsplash.com/photo-1556740738-b6a63e27c4df?auto=format&fit=crop&w=1400&q=80",
            "https://images.unsplash.com/photo-1600880292203-757bb62b4baf?auto=format&fit=crop&w=1400&q=80",
        ],
    },
    "dong-phuc-moi-2025": {
        "lead": "Bộ nhận diện đồng phục mới giúp đội ngũ cửa hàng thể hiện tinh thần trẻ trung, hiện đại và nhất quán thương hiệu.",
        "paragraphs": [
            "Thiết kế tập trung vào độ thoải mái khi làm việc theo ca, đồng thời nâng cao trải nghiệm thị giác tại điểm bán.",
            "Đây là một phần trong chương trình nâng cấp toàn diện hình ảnh vận hành tại các cửa hàng trọng điểm.",
        ],
        "images": [
            "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?auto=format&fit=crop&w=1400&q=80",
        ],
    },
    "thu-vien-uoc-mo-ba-vi": {
        "lead": "Dự án cộng đồng tiếp tục được mở rộng với mục tiêu tạo thêm không gian học tập thân thiện cho học sinh.",
        "paragraphs": [
            "Chương trình hỗ trợ sách, kệ đọc và các hoạt động khuyến đọc cho học sinh tại khu vực ngoại thành.",
            "Hoạt động nằm trong chuỗi dự án phát triển bền vững và gắn kết cộng đồng địa phương.",
        ],
        "images": [
            "https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?auto=format&fit=crop&w=1400&q=80",
        ],
    },
}


def _news_entries():
    featured = dict(NEWS_EVENTS["featured"])
    featured["slug"] = "bo-nhiem-tan-tong-giam-doc-1000-cua-hang"
    featured["date"] = "28/02/2026"

    items = [
        {
            **NEWS_EVENTS["items"][0],
            "slug": "dong-phuc-moi-2025",
            "date": "24/02/2026",
        },
        {
            **NEWS_EVENTS["items"][1],
            "slug": "thu-vien-uoc-mo-ba-vi",
            "date": "25/02/2026",
        },
        {
            **NEWS_EVENTS["items"][2],
            "slug": "hop-tac-bat-dong-san-do-thi",
            "date": "26/02/2026",
        },
        {
            **NEWS_EVENTS["items"][3],
            "slug": "nuoc-sach-den-truong",
            "date": "27/02/2026",
        },
        {
            **NEWS_EVENTS["items"][4],
            "slug": "uu-dai-thang-moi",
            "date": "28/02/2026",
        },
        {
            **NEWS_EVENTS["items"][5],
            "slug": "mo-rong-khung-gio-cham-soc",
            "date": "01/03/2026",
        },
    ]
    return featured, items


def _about_page_gallery_groups(page):
    groups = []
    grouped_items = {}

    for item in page.hinh_anh_phu.all().order_by("thu_tu", "id"):
        if not getattr(item.hinh_anh, "url", ""):
            continue
        group_key = item.nhom or f"single-{item.pk}"
        group = grouped_items.get(group_key)
        if group is None:
            group = {
                "group_key": group_key,
                "title": item.tieu_de or "",
                "caption": item.chu_thich or "",
                "images": [],
            }
            grouped_items[group_key] = group
            groups.append(group)
        group["images"].append({"url": item.hinh_anh.url, "alt": item.tieu_de or item.chu_thich or page.tieu_de})
        if not group["title"] and item.tieu_de:
            group["title"] = item.tieu_de
        if not group["caption"] and item.chu_thich:
            group["caption"] = item.chu_thich
    return groups


def _about_page_gallery_admin_groups(page):
    groups = []
    grouped_items = {}

    for item in page.hinh_anh_phu.all().order_by("thu_tu", "id"):
        if not getattr(item.hinh_anh, "url", ""):
            continue
        group_key = item.nhom or f"single-{item.pk}"
        group = grouped_items.get(group_key)
        if group is None:
            group = {
                "group_key": group_key,
                "title": item.tieu_de or "",
                "caption": item.chu_thich or "",
                "images": [],
                "item_ids": [],
            }
            grouped_items[group_key] = group
            groups.append(group)
        group["images"].append({"url": item.hinh_anh.url, "alt": item.tieu_de or item.chu_thich or page.tieu_de})
        group["item_ids"].append(item.pk)
        if not group["title"] and item.tieu_de:
            group["title"] = item.tieu_de
        if not group["caption"] and item.chu_thich:
            group["caption"] = item.chu_thich
    return groups


def _about_page_gallery_items(page):
    items = []
    for group in _about_page_gallery_groups(page):
        first_image = group["images"][0] if group["images"] else None
        if not first_image:
            continue
        items.append(
            {
                "url": first_image["url"],
                "title": group["title"],
                "caption": group["caption"],
            }
        )
    return items


def _about_page_gallery_urls(page):
    return [item["url"] for item in _about_page_gallery_items(page)]


def _extract_gallery_upload_captions(raw_text):
    if not raw_text:
        return []
    return [line.strip() for line in raw_text.splitlines()]


def _update_about_gallery_details(page, post_data):
    updated = 0
    for item in page.hinh_anh_phu.all().order_by("thu_tu", "id"):
        title_key = f"gallery_title_{item.pk}"
        caption_key = f"gallery_caption_{item.pk}"
        if title_key not in post_data and caption_key not in post_data:
            continue
        title = (post_data.get(title_key) or "").strip()
        caption = (post_data.get(caption_key) or "").strip()
        changed_fields = []
        if title != (item.tieu_de or ""):
            item.tieu_de = title
            changed_fields.append("tieu_de")
        if caption != (item.chu_thich or ""):
            item.chu_thich = caption
            changed_fields.append("chu_thich")
        if changed_fields:
            item.save(update_fields=changed_fields)
            updated += 1
    return updated


def _update_about_gallery_group_details(page, post_data):
    updated = 0
    groups = _about_page_gallery_admin_groups(page)
    for group in groups:
        title_key = f"group_title::{group['group_key']}"
        caption_key = f"group_caption::{group['group_key']}"
        if title_key not in post_data and caption_key not in post_data:
            continue
        title = (post_data.get(title_key) or "").strip()
        caption = (post_data.get(caption_key) or "").strip()
        items = page.hinh_anh_phu.filter(pk__in=group["item_ids"])
        changed = False
        for item in items:
            fields = []
            if title != (item.tieu_de or ""):
                item.tieu_de = title
                fields.append("tieu_de")
            if caption != (item.chu_thich or ""):
                item.chu_thich = caption
                fields.append("chu_thich")
            if fields:
                item.save(update_fields=fields)
                changed = True
        if changed:
            updated += 1
    return updated


def _delete_about_gallery_groups(page, post_data):
    raw_keys = post_data.getlist("delete_group_keys")
    group_keys = [key.strip() for key in raw_keys if (key or "").strip()]
    if not group_keys:
        return 0
    deleted = 0
    for group_key in group_keys:
        queryset = page.hinh_anh_phu.filter(nhom=group_key)
        if group_key.startswith("single-"):
            try:
                pk = int(group_key.split("-", 1)[1])
            except (TypeError, ValueError):
                pk = None
            if pk:
                queryset = page.hinh_anh_phu.filter(pk=pk)
        deleted += queryset.count()
        queryset.delete()
    return deleted


def _about_page_sections(page):
    body = (page.noi_dung or "").strip()
    if body:
        return [{"heading": "Nội dung giới thiệu", "content": body, "image": ""}]
    if page.mo_ta_ngan:
        return [{"heading": "Nội dung giới thiệu", "content": page.mo_ta_ngan.strip(), "image": ""}]
    return []


def _save_about_gallery(page, gallery_images, captions=None, titles=None):
    if not gallery_images:
        return 0

    captions = captions or []
    titles = titles or []
    next_order = page.hinh_anh_phu.aggregate(max_order=dj_models.Max("thu_tu")).get("max_order") or 0
    group_key = f"legacy-{uuid.uuid4().hex[:12]}"
    for offset, image in enumerate(gallery_images, start=1):
        TrangGioiThieuHinhAnh.objects.create(
            trang=page,
            nhom=group_key,
            tieu_de=titles[offset - 1] if offset - 1 < len(titles) else "",
            hinh_anh=image,
            chu_thich=captions[offset - 1] if offset - 1 < len(captions) else "",
            thu_tu=next_order + offset,
        )
    return len(gallery_images)


def _collect_about_gallery_slot_payloads(files, post_data, slot_count=4, min_images_per_slot=3):
    payloads = []
    errors = []
    for slot in range(1, slot_count + 1):
        images = files.getlist(f"gallery_slot_images_{slot}")
        title = (post_data.get(f"gallery_slot_title_{slot}") or "").strip()
        caption = (post_data.get(f"gallery_slot_caption_{slot}") or "").strip()
        if not images:
            continue
        if len(images) < min_images_per_slot:
            errors.append(f"Bản {slot} cần ít nhất {min_images_per_slot} ảnh khi tải lên.")
            continue
        payloads.append(
            {
                "slot": slot,
                "title": title,
                "caption": caption,
                "images": images,
            }
        )
    return payloads, errors


def _save_about_gallery_slots(page, slot_payloads):
    created = 0
    next_order = page.hinh_anh_phu.aggregate(max_order=dj_models.Max("thu_tu")).get("max_order") or 0
    for payload in slot_payloads:
        group_key = f"slot-{payload['slot']}-{uuid.uuid4().hex[:10]}"
        for image in payload["images"]:
            TrangGioiThieuHinhAnh.objects.create(
                trang=page,
                nhom=group_key,
                tieu_de=payload["title"],
                hinh_anh=image,
                chu_thich=payload["caption"],
                thu_tu=next_order + created + 1,
            )
            created += 1
    return created


def _about_page_defaults():
    return {
        "tieu_de": "Giới thiệu hệ thống",
        "mo_ta_ngan": "Trang này dùng để admin quản lý bài giới thiệu, cập nhật nội dung và hình ảnh minh họa.",
    }


def _about_page_has_custom_content(page):
    if not page:
        return False
    defaults = _about_page_defaults()
    if (page.noi_dung or "").strip():
        return True
    if any(getattr(page, field_name) for field_name in ("anh_bia", "anh_noi_dung_1", "anh_noi_dung_2", "anh_noi_dung_3")):
        return True
    if page.hinh_anh_phu.exists():
        return True
    if (page.tieu_de or "").strip() != defaults["tieu_de"]:
        return True
    if (page.mo_ta_ngan or "").strip() != defaults["mo_ta_ngan"]:
        return True
    return False


def _build_about_public_page_context(pref):
    page = TrangGioiThieu.objects.prefetch_related("hinh_anh_phu").filter(pk=1).first()
    if page and _about_page_has_custom_content(page):
        return {
            "title": page.tieu_de or "Giới thiệu hệ thống",
            "kicker": "Giới thiệu",
            "summary": page.mo_ta_ngan or "Thông tin giới thiệu đang được cập nhật.",
            "sections": _about_page_sections(page),
            "hero_image": page.anh_bia.url
            if page.anh_bia
            else "https://images.unsplash.com/photo-1521791136064-7986c2920216?auto=format&fit=crop&w=1400&q=80",
            "page_slug": "gioi-thieu-circle-k",
            "gallery_images": _about_page_gallery_groups(page),
            "using_admin_content": True,
            **pref,
        }

    legacy_page = INFO_PAGES.get("gioi-thieu-circle-k", {})
    media = PAGE_MEDIA.get("gioi-thieu-circle-k", {})
    section_images = media.get("section_images", [])
    sections = []
    for idx, section in enumerate(legacy_page.get("sections", [])):
        section_data = dict(section)
        if section_images:
            section_data["image"] = section_images[idx % len(section_images)]
        sections.append(section_data)

    context = dict(legacy_page)
    context["page_slug"] = "gioi-thieu-circle-k"
    context["sections"] = sections
    context["gallery_images"] = []
    context["hero_image"] = media.get(
        "hero_image",
        "https://images.unsplash.com/photo-1521791136064-7986c2920216?auto=format&fit=crop&w=1400&q=80",
    )
    context["using_admin_content"] = False
    context.update(pref)
    return context


def news_detail(request, slug):
    pref = _admin_pref_context(request)
    featured_news, news_items = _news_entries()
    all_news = [featured_news] + news_items
    article = next((n for n in all_news if n.get("slug") == slug), None)

    if not article:
        return render(
            request,
            "store/news_detail.html",
            status=404,
            context={
                "title": "Không tìm thấy bài viết",
                "article": None,
                "related_news": all_news[:6],
                "is_not_found": True,
                **pref,
            },
        )

    details = NEWS_DETAILS.get(slug, {})
    article_data = dict(article)
    article_data["lead"] = details.get("lead", article.get("excerpt", ""))
    article_data["paragraphs"] = details.get(
        "paragraphs",
        [
            article.get("excerpt", ""),
            "Nội dung bài viết đang được cập nhật chi tiết để phản ánh đầy đủ các hoạt động mới nhất.",
        ],
    )
    article_data["images"] = details.get("images", [article.get("image")])

    related_news = [n for n in all_news if n.get("slug") != slug][:8]
    return render(
        request,
        "store/news_detail.html",
        context={
            "title": article_data["title"],
            "article": article_data,
            "related_news": related_news,
            "page_slug": "tin-tuc-su-kien",
            **pref,
        },
    )


# CMS Section
import csv
import json
import math
import os
import re
import random
import uuid
import unicodedata
from urllib.parse import parse_qs, urlencode, urlparse
from urllib.request import Request, urlopen
from datetime import datetime, time, timedelta
from decimal import Decimal, ROUND_HALF_UP

from django.apps import apps
from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, SetPasswordForm, UserCreationForm
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import Group
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth.views import LoginView
from django.conf import settings
from django.core.mail import send_mail, get_connection
from django.core.paginator import Paginator
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.files.images import get_image_dimensions
from django.core.serializers.json import DjangoJSONEncoder
from django import forms
from django.db import models as dj_models, transaction
from django.db.models import Count, Q, Sum
from django.db.models.functions import Coalesce
from django.forms import modelform_factory
from django.forms.models import model_to_dict
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.encoding import force_bytes, force_str
from django.utils import timezone
from django.utils.dateparse import parse_date, parse_datetime
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.decorators.http import require_POST

from .models import (
    ChiTietDonHang,
    DanhGiaCuaHang,
    DiaChiKhachHang,
    DonHang,
    GiaoDichKho,
    GopYKhachHang,
    HinhAnhSanPham,
    HoSoKhachHang,
    Notification,
    TepDanhGiaCuaHang,
    TrashRecord,
    ChuoiCuaHang,
    CuaHang,
    KhuyenMai,
    NhaCungCap,
    NhanVien,
    NhomSanPham,
    SanPham,
    TonKhoAudit,
    TonKhoCuaHang,
    TrangGioiThieu,
    TrangGioiThieuHinhAnh,
    ThuongHieu,
    XacNhanThanhToan,
)


MODEL_REGISTRY = {
    "thuong-hieu": ThuongHieu,
    "nha-cung-cap": NhaCungCap,
    "nhom-san-pham": NhomSanPham,
    "san-pham": SanPham,
    "giao-dich-kho": GiaoDichKho,
    "ton-kho-cua-hang": TonKhoCuaHang,
    "nhat-ky-ton-kho": TonKhoAudit,
    "chuoi-cua-hang": ChuoiCuaHang,
    "cua-hang": CuaHang,
    "nhan-vien": NhanVien,
    "khuyen-mai": KhuyenMai,
    "danh-gia-cua-hang": DanhGiaCuaHang,
    "gop-y-khach-hang": GopYKhachHang,
    "ho-so-khach-hang": HoSoKhachHang,
    "dia-chi-khach-hang": DiaChiKhachHang,
    "chi-tiet-don-hang": ChiTietDonHang,
    "don-hang": DonHang,
}

ORDER_MODULE_SLUG = "don-hang"
ORDER_ITEM_MODULE_SLUG = "chi-tiet-don-hang"
MENU_SECTION_ORDER = ["catalog", "operations", "sales", "customers"]
MENU_SECTION_LABELS = {
    "vi": {
        "catalog": "Danh mục",
        "operations": "Vận hành",
        "sales": "Bán hàng",
        "customers": "Khách hàng",
    },
    "en": {
        "catalog": "Catalog",
        "operations": "Operations",
        "sales": "Sales",
        "customers": "Customers",
    },
}
MENU_SECTION_MAP = {
    "thuong-hieu": "catalog",
    "nha-cung-cap": "catalog",
    "nhom-san-pham": "catalog",
    "san-pham": "catalog",
    "khuyen-mai": "catalog",
    "giao-dich-kho": "operations",
    "ton-kho-cua-hang": "operations",
    "nhat-ky-ton-kho": "operations",
    "chuoi-cua-hang": "operations",
    "cua-hang": "operations",
    "nhan-vien": "operations",
    "chi-tiet-don-hang": "sales",
    "don-hang": "sales",
    "danh-gia-cua-hang": "customers",
    "gop-y-khach-hang": "customers",
    "ho-so-khach-hang": "customers",
    "dia-chi-khach-hang": "customers",
}
MENU_ITEM_ORDER = {
    "san-pham": 10,
    "thuong-hieu": 20,
    "nha-cung-cap": 30,
    "nhom-san-pham": 40,
    "khuyen-mai": 50,
    "giao-dich-kho": 60,
    "ton-kho-cua-hang": 70,
    "nhat-ky-ton-kho": 75,
    "chuoi-cua-hang": 80,
    "cua-hang": 90,
    "nhan-vien": 100,
    "chi-tiet-don-hang": 110,
    "don-hang": 120,
    "danh-gia-cua-hang": 125,
    "gop-y-khach-hang": 130,
    "ho-so-khach-hang": 140,
    "dia-chi-khach-hang": 150,
}

User = get_user_model()
ROLE_SYSTEM_ADMIN = "SystemAdmin"
ROLE_STOCK_MANAGER = "StockManager"
ROLE_ORDER_MANAGER = "OrderManager"
ROLE_CUSTOMER_SUPPORT = "CustomerSupport"
ROLE_CUSTOMER = "Customer"
ROLE_ADMIN = ROLE_SYSTEM_ADMIN
ROLE_USER = ROLE_CUSTOMER
ROLE_CHOICES = (
    (ROLE_SYSTEM_ADMIN, "Quản trị hệ thống"),
    (ROLE_STOCK_MANAGER, "Quản lý kho"),
    (ROLE_ORDER_MANAGER, "Quản lý đơn hàng"),
    (ROLE_CUSTOMER_SUPPORT, "Nhân viên CSKH"),
    (ROLE_CUSTOMER, "Khách hàng"),
)
ROLE_LABELS = dict(ROLE_CHOICES)
INTERNAL_ROLES = {
    ROLE_SYSTEM_ADMIN,
    ROLE_STOCK_MANAGER,
    ROLE_ORDER_MANAGER,
    ROLE_CUSTOMER_SUPPORT,
}
LEGACY_ROLE_MAP = {
    "Admin": ROLE_SYSTEM_ADMIN,
    "User": ROLE_CUSTOMER,
}
MODULE_ROLE_ACTIONS = {
    "thuong-hieu": {
        "view": {ROLE_SYSTEM_ADMIN, ROLE_STOCK_MANAGER, ROLE_ORDER_MANAGER},
        "create": {ROLE_SYSTEM_ADMIN, ROLE_STOCK_MANAGER},
        "update": {ROLE_SYSTEM_ADMIN, ROLE_STOCK_MANAGER},
        "delete": {ROLE_SYSTEM_ADMIN},
    },
    "nha-cung-cap": {
        "view": {ROLE_SYSTEM_ADMIN, ROLE_STOCK_MANAGER},
        "create": {ROLE_SYSTEM_ADMIN, ROLE_STOCK_MANAGER},
        "update": {ROLE_SYSTEM_ADMIN, ROLE_STOCK_MANAGER},
        "delete": {ROLE_SYSTEM_ADMIN},
    },
    "nhom-san-pham": {
        "view": {ROLE_SYSTEM_ADMIN, ROLE_STOCK_MANAGER, ROLE_ORDER_MANAGER},
        "create": {ROLE_SYSTEM_ADMIN, ROLE_STOCK_MANAGER},
        "update": {ROLE_SYSTEM_ADMIN, ROLE_STOCK_MANAGER},
        "delete": {ROLE_SYSTEM_ADMIN},
    },
    "san-pham": {
        "view": {ROLE_SYSTEM_ADMIN, ROLE_STOCK_MANAGER, ROLE_ORDER_MANAGER, ROLE_CUSTOMER_SUPPORT},
        "create": {ROLE_SYSTEM_ADMIN, ROLE_STOCK_MANAGER},
        "update": {ROLE_SYSTEM_ADMIN, ROLE_STOCK_MANAGER},
        "delete": {ROLE_SYSTEM_ADMIN},
    },
    "giao-dich-kho": {
        "view": {ROLE_SYSTEM_ADMIN, ROLE_STOCK_MANAGER},
        "create": {ROLE_SYSTEM_ADMIN, ROLE_STOCK_MANAGER},
        "update": {ROLE_SYSTEM_ADMIN, ROLE_STOCK_MANAGER},
        "delete": {ROLE_SYSTEM_ADMIN},
        "print": {ROLE_SYSTEM_ADMIN, ROLE_STOCK_MANAGER},
    },
    "ton-kho-cua-hang": {
        "view": {ROLE_SYSTEM_ADMIN, ROLE_STOCK_MANAGER, ROLE_ORDER_MANAGER},
        "create": {ROLE_SYSTEM_ADMIN},
        "update": {ROLE_SYSTEM_ADMIN},
        "delete": {ROLE_SYSTEM_ADMIN},
    },
    "hinh-anh-san-pham": {
        "view": {ROLE_SYSTEM_ADMIN, ROLE_STOCK_MANAGER},
        "create": {ROLE_SYSTEM_ADMIN, ROLE_STOCK_MANAGER},
        "update": {ROLE_SYSTEM_ADMIN, ROLE_STOCK_MANAGER},
        "delete": {ROLE_SYSTEM_ADMIN},
    },
    "chuoi-cua-hang": {
        "view": {ROLE_SYSTEM_ADMIN, ROLE_STOCK_MANAGER},
        "create": {ROLE_SYSTEM_ADMIN, ROLE_STOCK_MANAGER},
        "update": {ROLE_SYSTEM_ADMIN, ROLE_STOCK_MANAGER},
        "delete": {ROLE_SYSTEM_ADMIN},
    },
    "cua-hang": {
        "view": {ROLE_SYSTEM_ADMIN, ROLE_STOCK_MANAGER, ROLE_ORDER_MANAGER},
        "create": {ROLE_SYSTEM_ADMIN, ROLE_STOCK_MANAGER},
        "update": {ROLE_SYSTEM_ADMIN, ROLE_STOCK_MANAGER},
        "delete": {ROLE_SYSTEM_ADMIN},
    },
    "nhan-vien": {
        "view": {ROLE_SYSTEM_ADMIN, ROLE_STOCK_MANAGER, ROLE_CUSTOMER_SUPPORT},
        "create": {ROLE_SYSTEM_ADMIN},
        "update": {ROLE_SYSTEM_ADMIN},
        "delete": {ROLE_SYSTEM_ADMIN},
    },
    "khuyen-mai": {
        "view": {ROLE_SYSTEM_ADMIN, ROLE_ORDER_MANAGER},
        "create": {ROLE_SYSTEM_ADMIN, ROLE_ORDER_MANAGER},
        "update": {ROLE_SYSTEM_ADMIN, ROLE_ORDER_MANAGER},
        "delete": {ROLE_SYSTEM_ADMIN},
    },
    "danh-gia-cua-hang": {
        "view": {ROLE_SYSTEM_ADMIN, ROLE_CUSTOMER_SUPPORT},
        "create": set(),
        "update": {ROLE_SYSTEM_ADMIN, ROLE_CUSTOMER_SUPPORT},
        "delete": {ROLE_SYSTEM_ADMIN},
    },
    "gop-y-khach-hang": {
        "view": {ROLE_SYSTEM_ADMIN, ROLE_CUSTOMER_SUPPORT},
        "create": {ROLE_SYSTEM_ADMIN, ROLE_CUSTOMER_SUPPORT},
        "update": {ROLE_SYSTEM_ADMIN, ROLE_CUSTOMER_SUPPORT},
        "delete": {ROLE_SYSTEM_ADMIN},
    },
    "ho-so-khach-hang": {
        "view": {ROLE_SYSTEM_ADMIN, ROLE_CUSTOMER_SUPPORT},
        "create": {ROLE_SYSTEM_ADMIN, ROLE_CUSTOMER_SUPPORT},
        "update": {ROLE_SYSTEM_ADMIN, ROLE_CUSTOMER_SUPPORT},
        "delete": {ROLE_SYSTEM_ADMIN},
    },
    "dia-chi-khach-hang": {
        "view": {ROLE_SYSTEM_ADMIN, ROLE_CUSTOMER_SUPPORT},
        "create": {ROLE_SYSTEM_ADMIN, ROLE_CUSTOMER_SUPPORT},
        "update": {ROLE_SYSTEM_ADMIN, ROLE_CUSTOMER_SUPPORT},
        "delete": {ROLE_SYSTEM_ADMIN},
    },
    "don-hang": {
        "view": {ROLE_SYSTEM_ADMIN, ROLE_ORDER_MANAGER, ROLE_CUSTOMER_SUPPORT},
        "create": {ROLE_SYSTEM_ADMIN},
        "update": {ROLE_SYSTEM_ADMIN, ROLE_ORDER_MANAGER, ROLE_CUSTOMER_SUPPORT},
        "delete": {ROLE_SYSTEM_ADMIN},
        "status": {ROLE_SYSTEM_ADMIN, ROLE_ORDER_MANAGER, ROLE_CUSTOMER_SUPPORT},
        "payment_status": {ROLE_SYSTEM_ADMIN, ROLE_ORDER_MANAGER},
    },
    "chi-tiet-don-hang": {
        "view": {ROLE_SYSTEM_ADMIN, ROLE_ORDER_MANAGER, ROLE_CUSTOMER_SUPPORT},
        "create": {ROLE_SYSTEM_ADMIN},
        "update": {ROLE_SYSTEM_ADMIN},
        "delete": {ROLE_SYSTEM_ADMIN},
    },
}
ADMIN_PAGE_ROLE_ACTIONS = {
    "dashboard": {"view": INTERNAL_ROLES},
    "about": {"view": INTERNAL_ROLES},
    "inventory_hub": {"view": {ROLE_SYSTEM_ADMIN, ROLE_STOCK_MANAGER}},
    "settings": {"view": {ROLE_SYSTEM_ADMIN}},
    "user_management": {"view": {ROLE_SYSTEM_ADMIN}},
    "trash": {"view": {ROLE_SYSTEM_ADMIN}, "restore": {ROLE_SYSTEM_ADMIN}, "delete": {ROLE_SYSTEM_ADMIN}},
    "notifications": {"view": INTERNAL_ROLES},
}


def _default_payment_status_for_method(method: str) -> str:
    if method == "bank_transfer":
        return "awaiting_confirmation"
    return "unpaid"


def _momo_demo_context(order):
    qr_svg = ""
    qr_payload = f"MOMO-DEMO|ORDER:{order.pk}|AMOUNT:{int(order.tong_tien or 0)}"
    try:
        from reportlab.graphics import renderSVG
        from reportlab.graphics.barcode.qr import QrCodeWidget
        from reportlab.graphics.shapes import Drawing

        qr_widget = QrCodeWidget(qr_payload)
        bounds = qr_widget.getBounds()
        qr_width = bounds[2] - bounds[0]
        qr_height = bounds[3] - bounds[1]
        qr_drawing = Drawing(180, 180, transform=[180 / qr_width, 0, 0, 180 / qr_height, 0, 0])
        qr_drawing.add(qr_widget)
        qr_svg = renderSVG.drawToString(qr_drawing)
        if isinstance(qr_svg, bytes):
            qr_svg = qr_svg.decode("utf-8")
    except Exception:
        qr_svg = ""
    return {
        "order": order,
        "order_amount_display": _format_currency(order.tong_tien),
        "momo_demo_code": f"MOMO-DEMO-{order.pk}",
        "momo_demo_qr_svg": qr_svg,
        "momo_demo_qr_payload": qr_payload,
    }

MODULE_LABELS = {
    "thuong-hieu": {"vi_singular": "Thương hiệu", "vi_plural": "Thương hiệu", "en_singular": "Brand", "en_plural": "Brands"},
    "nha-cung-cap": {"vi_singular": "Nhà cung cấp", "vi_plural": "Nhà cung cấp", "en_singular": "Supplier", "en_plural": "Suppliers"},
    "nhom-san-pham": {"vi_singular": "Nhóm sản phẩm", "vi_plural": "Nhóm sản phẩm", "en_singular": "Product Group", "en_plural": "Product Groups"},
    "san-pham": {"vi_singular": "Sản phẩm", "vi_plural": "Sản phẩm", "en_singular": "Product", "en_plural": "Products"},
    "giao-dich-kho": {"vi_singular": "Giao dịch kho", "vi_plural": "Giao dịch kho", "en_singular": "Stock Movement", "en_plural": "Stock Movements"},
    "ton-kho-cua-hang": {"vi_singular": "Tồn kho cửa hàng", "vi_plural": "Tồn kho cửa hàng", "en_singular": "Store Stock", "en_plural": "Store Stocks"},
    "nhat-ky-ton-kho": {"vi_singular": "Nhật ký tồn kho", "vi_plural": "Nhật ký tồn kho", "en_singular": "Stock Audit", "en_plural": "Stock Audit"},
    "hinh-anh-san-pham": {"vi_singular": "Hình ảnh sản phẩm", "vi_plural": "Hình ảnh sản phẩm", "en_singular": "Product Image", "en_plural": "Product Images"},
    "chuoi-cua-hang": {"vi_singular": "Chuỗi cửa hàng", "vi_plural": "Chuỗi cửa hàng", "en_singular": "Store Chain", "en_plural": "Store Chains"},
    "cua-hang": {"vi_singular": "Cửa hàng", "vi_plural": "Cửa hàng", "en_singular": "Store", "en_plural": "Stores"},
    "nhan-vien": {"vi_singular": "Nhân viên", "vi_plural": "Nhân viên", "en_singular": "Employee", "en_plural": "Employees"},
    "khuyen-mai": {"vi_singular": "Khuyến mãi", "vi_plural": "Khuyến mãi", "en_singular": "Promotion", "en_plural": "Promotions"},
    "danh-gia-cua-hang": {"vi_singular": "\u0110\u00e1nh gi\u00e1 c\u1eeda h\u00e0ng", "vi_plural": "\u0110\u00e1nh gi\u00e1 c\u1eeda h\u00e0ng", "en_singular": "Store Review", "en_plural": "Store Reviews"},
    "gop-y-khach-hang": {"vi_singular": "Góp ý khách hàng", "vi_plural": "Góp ý khách hàng", "en_singular": "Customer Feedback", "en_plural": "Customer Feedback"},
    "ho-so-khach-hang": {"vi_singular": "Hồ sơ khách hàng", "vi_plural": "Hồ sơ khách hàng", "en_singular": "Customer Profile", "en_plural": "Customer Profiles"},
    "dia-chi-khach-hang": {"vi_singular": "Địa chỉ khách hàng", "vi_plural": "Địa chỉ khách hàng", "en_singular": "Customer Address", "en_plural": "Customer Addresses"},
    "don-hang": {"vi_singular": "Đơn hàng", "vi_plural": "Đơn hàng", "en_singular": "Order", "en_plural": "Orders"},
    "chi-tiet-don-hang": {"vi_singular": "Chi tiết đơn hàng", "vi_plural": "Chi tiết đơn hàng", "en_singular": "Order Item", "en_plural": "Order Items"},
}

CMS_TRANSLATIONS = {
    "vi": {
        "system_settings": "Cài đặt hệ thống",
        "dashboard": "Tổng quan",
        "inventory_hub": "Kho",
        "navigation": "Điều hướng",
        "data": "Dữ liệu",
        "logout": "Đăng xuất",
        "add_new": "Thêm mới",
        "save_changes": "Lưu thay đổi",
        "back_to_list": "Quay lại danh sách",
        "search_placeholder": "Tìm theo nội dung...",
        "actions": "Thao tác",
        "previous": "Trước",
        "next": "Sau",
        "first": "Đầu",
        "last": "Cuối",
        "page": "Trang",
        "no_data": "Chưa có dữ liệu.",
        "language": "Ngôn ngữ",
        "theme": "Giao diện",
        "light_theme": "Nền sáng",
        "dark_theme": "Nền tối",
        "vietnamese": "Tiếng Việt",
        "english": "Tiếng Anh",
        "save_settings": "Lưu cài đặt",
        "settings_saved": "Đã lưu cài đặt hệ thống.",
        "logged_in_as": "Đăng nhập bởi",
        "internal_cms": "Hệ thống nội bộ",
        "custom_internal_management": "Hệ thống quản trị nội bộ tự tạo",
        "manage": "Quản lý",
        "confirm_delete": "Xác nhận xóa",
        "you_are_deleting": "Bạn đang xóa một bản ghi của",
        "confirm_delete_btn": "Xác nhận xóa",
        "cancel": "Hủy",
        "total_records": "Tổng bản ghi",
        "all_modules": "Tất cả module dữ liệu trong hệ thống",
        "total_modules": "Số module",
        "module_hint": "Bao gồm danh mục, cửa hàng, nhân viên, khuyến mãi...",
        "manage_module": "Quản lý",
        "edit": "Sửa",
        "delete": "Xóa",
        "create_prefix": "Thêm",
        "edit_prefix": "Sửa",
        "file_current": "Tệp hiện tại",
        "saved_successfully": "Lưu thành công.",
        "deleted_successfully": "Xóa thành công.",
        "no_access": "Tài khoản không có quyền truy cập trang quản trị.",
        "store_front": "Cửa hàng",
        "notifications": "Thông báo",
        "user_management": "Quản lý người dùng",
        "role": "Vai trò",
        "admin_role": "Admin",
        "user_role": "User",
        "account_status": "Trạng thái",
        "active": "Hoạt động",
        "inactive": "Ngưng",
        "create_user": "Tạo người dùng",
        "full_name": "Họ tên",
        "update_role": "Cập nhật quyền",
        "user_area": "Trang người dùng",
        "user_portal": "Khu vực người dùng",
        "welcome_user": "Xin chào",
        "user_intro": "Trang dành cho tài khoản người dùng đã đăng nhập.",
        "access_admin": "Vào trang quản trị",
        "user_login_title": "Đăng nhập tài khoản của bạn",
        "user_login_hint": "",
        "user_created": "Đã tạo tài khoản mới.",
        "user_updated": "Đã cập nhật quyền người dùng.",
        "register": "Đăng ký",
        "products_page": "Sản phẩm",
        "cart": "Giỏ hàng",
        "checkout": "Thanh toán",
        "my_orders": "Đơn hàng của tôi",
        "buy_now": "Mua ngay",
        "add_to_cart": "Thêm vào giỏ",
        "cart_empty": "Giỏ hàng đang trống.",
        "continue_shopping": "Tiếp tục mua sắm",
        "place_order": "Đặt hàng",
        "receiver_name": "Người nhận",
        "delivery_address": "Địa chỉ giao hàng",
        "quantity": "Số lượng",
        "order_success": "Đã tạo đơn hàng thành công.",
        "login_to_buy": "Bạn cần đăng nhập tài khoản khách hàng để mua sản phẩm.",
        "product_added": "Đã thêm sản phẩm vào giỏ hàng.",
        "cart_updated": "Đã cập nhật giỏ hàng.",
        "order_status": "Trạng thái đơn",
        "order_code": "Mã đơn",
        "order_time": "Thời gian đặt",
        "product_catalog_intro": "Khách có thể xem hàng tự do, nhưng cần tài khoản để thêm giỏ và đặt mua.",
        "customer_profile": "Hồ sơ khách hàng",
        "update_profile": "Cập nhật hồ sơ",
        "profile_saved": "Đã lưu hồ sơ khách hàng.",
        "all_statuses": "Tất cả trạng thái",
        "confirm_order": "Xác nhận đơn",
        "ship_order": "Bắt đầu giao",
        "deliver_order": "Đã giao",
        "complete_order": "Hoàn tất đơn",
        "cancel_order": "Hủy đơn",
        "order_status_updated": "Đã cập nhật trạng thái đơn hàng.",
        "trash": "Thùng rác",
        "restore": "Khôi phục",
        "delete_permanently": "Xóa hẳn",
        "deleted_at": "Thời gian xóa",
        "expires_at": "Tự xóa sau",
        "trash_empty": "Thùng rác đang trống.",
        "unit_price": "Đơn giá",
        "line_total": "Thành tiền",
        "total_amount": "Tổng tiền",
        "featured_products": "Sản phẩm nổi bật",
        "password_strength": "Độ mạnh mật khẩu",
        "password_weak": "Yếu",
        "password_medium": "Trung bình",
        "password_strong": "Mạnh",
        "password_hint": "Nên có ít nhất 8 ký tự, gồm chữ hoa, chữ thường, số và ký tự đặc biệt.",
        "password_too_weak": "Mật khẩu đang quá yếu. Hãy dùng ít nhất 8 ký tự, có chữ hoa, chữ thường, số và ký tự đặc biệt.",
        "change_password": "Đổi mật khẩu",
        "reset_password": "Đặt lại mật khẩu",
        "password_updated": "Đã cập nhật mật khẩu.",
        "current_password": "Mật khẩu hiện tại",
        "new_password": "Mật khẩu mới",
        "confirm_password": "Xác nhận mật khẩu",
        "notification_title": "Thông báo hệ thống",
        "notification_empty": "Chưa có thông báo.",
        "support_request": "Yêu cầu hỗ trợ",
        "retry_request": "Yêu cầu thử lại",
        "login_title": "Đăng nhập quản trị",
        "login_only_staff": "Chỉ tài khoản Admin mới được phép truy cập.",
        "username": "Tài khoản",
        "password": "Mật khẩu",
        "login": "Đăng nhập",
        "cancel": "Hủy",
        "coord_pick_hint": "Tọa độ chỉ được lấy từ bản đồ.",
        "pick_on_map": "Chọn trên bản đồ",
        "coord_saved_from_map": "Đã nhận tọa độ từ bản đồ. Hãy bấm Lưu thay đổi để chốt.",
        "coord_required_from_map": "Cần chốt tọa độ bằng cách click trên bản đồ trước khi lưu.",
        "inventory_overview": "Tổng quan kho",
        "stock_summary": "Tóm tắt tồn kho",
        "suggest_import": "Đề xuất nhập thêm",
        "suggest_export": "Đề xuất ưu tiên xuất",
        "view_all_products": "Xem toàn bộ sản phẩm",
        "view_stock_movements": "Xem giao dịch kho",
    },
    "en": {
        "system_settings": "System Settings",
        "dashboard": "Dashboard",
        "inventory_hub": "Inventory",
        "navigation": "Navigation",
        "data": "Data",
        "logout": "Log Out",
        "add_new": "Add New",
        "save_changes": "Save Changes",
        "back_to_list": "Back to List",
        "search_placeholder": "Search by content...",
        "actions": "Actions",
        "previous": "Previous",
        "next": "Next",
        "first": "First",
        "last": "Last",
        "page": "Page",
        "no_data": "No data yet.",
        "language": "Language",
        "theme": "Theme",
        "light_theme": "Light",
        "dark_theme": "Dark",
        "vietnamese": "Vietnamese",
        "english": "English",
        "save_settings": "Save Settings",
        "settings_saved": "System settings saved.",
        "logged_in_as": "Logged in as",
        "internal_cms": "Internal System",
        "custom_internal_management": "Custom internal management system",
        "manage": "Manage",
        "confirm_delete": "Confirm Deletion",
        "you_are_deleting": "You are deleting a record of",
        "confirm_delete_btn": "Confirm Delete",
        "cancel": "Cancel",
        "total_records": "Total Records",
        "all_modules": "All data modules in the system",
        "total_modules": "Total Modules",
        "module_hint": "Including categories, stores, employees, promotions...",
        "manage_module": "Manage",
        "edit": "Edit",
        "delete": "Delete",
        "create_prefix": "Create",
        "edit_prefix": "Edit",
        "file_current": "Current file",
        "store_front": "Storefront",
        "notifications": "Notifications",
        "user_management": "User Management",
        "role": "Role",
        "admin_role": "Admin",
        "user_role": "User",
        "account_status": "Status",
        "active": "Active",
        "inactive": "Inactive",
        "create_user": "Create User",
        "full_name": "Full Name",
        "update_role": "Update Role",
        "user_area": "User Area",
        "user_portal": "User Portal",
        "welcome_user": "Welcome",
        "user_intro": "This page is for authenticated user accounts.",
        "access_admin": "Open Admin",
        "user_login_title": "User Login",
        "user_login_hint": "Regular users enter the user area. Admin accounts are redirected to the admin panel.",
        "user_created": "New user created.",
        "user_updated": "User role updated.",
        "register": "Register",
        "products_page": "Products",
        "cart": "Cart",
        "checkout": "Checkout",
        "my_orders": "My Orders",
        "buy_now": "Buy Now",
        "add_to_cart": "Add to Cart",
        "cart_empty": "Your cart is empty.",
        "continue_shopping": "Continue Shopping",
        "place_order": "Place Order",
        "receiver_name": "Receiver",
        "delivery_address": "Delivery Address",
        "quantity": "Quantity",
        "order_success": "Order created successfully.",
        "login_to_buy": "Please sign in with a customer account before purchasing.",
        "product_added": "Product added to cart.",
        "cart_updated": "Cart updated.",
        "order_status": "Order Status",
        "order_code": "Order Code",
        "order_time": "Order Time",
        "product_catalog_intro": "Visitors can browse products freely, but must sign in to add to cart and checkout.",
        "customer_profile": "Customer Profile",
        "update_profile": "Update Profile",
        "profile_saved": "Customer profile saved.",
        "all_statuses": "All Statuses",
        "confirm_order": "Confirm Order",
        "ship_order": "Start Delivery",
        "deliver_order": "Delivered",
        "complete_order": "Complete Order",
        "cancel_order": "Cancel Order",
        "order_status_updated": "Order status updated.",
        "trash": "Trash",
        "restore": "Restore",
        "delete_permanently": "Delete permanently",
        "deleted_at": "Deleted at",
        "expires_at": "Expires at",
        "trash_empty": "Trash is empty.",
        "unit_price": "Unit Price",
        "line_total": "Line Total",
        "total_amount": "Total Amount",
        "featured_products": "Featured Products",
        "password_strength": "Password Strength",
        "password_weak": "Weak",
        "password_medium": "Medium",
        "password_strong": "Strong",
        "password_hint": "Use at least 8 characters with uppercase, lowercase, numbers, and special characters.",
        "password_too_weak": "Password is too weak. Use at least 8 characters with uppercase, lowercase, numbers, and special characters.",
        "change_password": "Change Password",
        "reset_password": "Reset Password",
        "password_updated": "Password updated.",
        "current_password": "Current Password",
        "new_password": "New Password",
        "confirm_password": "Confirm Password",
        "notification_title": "System Notifications",
        "notification_empty": "No notifications yet.",
        "support_request": "Support Request",
        "retry_request": "Retry Request",
        "coord_pick_hint": "Coordinates must be selected from the map.",
        "pick_on_map": "Pick on map",
        "coord_saved_from_map": "Coordinates received from map. Click Save Changes to confirm.",
        "coord_required_from_map": "Please pick coordinates on map before saving.",
        "inventory_overview": "Inventory Overview",
        "stock_summary": "Stock Summary",
        "suggest_import": "Suggested Restock",
        "suggest_export": "Suggested Sell-Through",
        "view_all_products": "View all products",
        "view_stock_movements": "View stock movements",
    },
}

CMS_TRANSLATIONS["vi"]["about"] = "Giới thiệu"
CMS_TRANSLATIONS["vi"]["about_admin"] = "Giới thiệu hệ thống"
CMS_TRANSLATIONS["en"]["about"] = "About"
CMS_TRANSLATIONS["en"]["about_admin"] = "Admin Introduction"

FIELD_LABELS = {
    "en": {
        "ten": "Name",
        "ghi_chu": "Notes",
        "mo_ta": "Description",
        "nhom_san_pham": "Category",
        "nha_cung_cap": "Supplier",
        "thuong_hieu": "Brand",
        "hinh_anh": "Product Image",
        "gia_ban": "Price",
        "ton_kho": "Stock",
        "logo": "Logo",
        "chuoi": "Store Chain",
        "dia_chi": "Address",
        "quan_huyen": "District",
        "vi_do": "Latitude (lat)",
        "kinh_do": "Longitude (lng)",
        "mo_cua": "Open Time",
        "dong_cua": "Close Time",
        "hoat_dong_24h": "Open 24h",
        "san_pham": "Products",
        "chu_thich": "Caption",
        "thu_tu": "Display Order",
        "cua_hang": "Store",
        "ho_ten": "Full Name",
        "chuc_vu": "Position",
        "so_dien_thoai": "Phone",
        "email": "Email",
        "avatar": "Avatar",
        "chu_de": "Subject",
        "noi_dung": "Feedback Content",
        "da_phan_hoi": "Responded",
        "user": "User",
        "tinh_thanh": "Province / City",
        "quan_huyen": "District",
        "phuong_xa": "Ward / Commune",
        "dia_chi_cu_the": "Street Address",
        "loai_dia_chi": "Address Type",
        "mac_dinh": "Default Address",
        "khach_hang": "Customer",
        "ho_ten_nguoi_nhan": "Receiver",
        "dia_chi_giao_hang": "Delivery Address",
        "ghi_chu": "Note",
        "trang_thai": "Status",
        "tong_so_luong": "Total Quantity",
        "tong_tien": "Total Amount",
        "giam_gia": "Discount",
        "khuyen_mai": "Voucher",
        "ma_voucher_ap_dung": "Voucher Code Applied",
        "vi_do_giao_hang": "Delivery Latitude",
        "kinh_do_giao_hang": "Delivery Longitude",
        "ma_code": "Voucher Code",
        "loai_giam": "Discount Type",
        "gia_tri_giam": "Discount Value",
        "gia_tri_don_hang_toi_thieu": "Minimum Order",
        "giam_toi_da": "Maximum Discount",
        "dang_ap_dung": "Active",
        "ngay_bat_dau": "Start At",
        "ngay_ket_thuc": "End At",
        "don_hang": "Order",
        "so_luong": "Quantity",
        "don_gia": "Unit Price",
        "created_at": "Created At",
    }
}


class MultipleImageInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleImageField(forms.FileField):
    widget = MultipleImageInput

    def clean(self, data, initial=None):
        single_clean = super().clean
        if isinstance(data, (list, tuple)):
            return [single_clean(item, initial) for item in data]
        if not data:
            return []
        return [single_clean(data, initial)]


class SanPhamAdminForm(forms.ModelForm):
    product_images = MultipleImageField(
        label="Ảnh sản phẩm",
        required=False,
        widget=MultipleImageInput(attrs={"multiple": True, "accept": "image/*"}),
        help_text="Chọn một hoặc nhiều ảnh. Ảnh đầu tiên sẽ làm ảnh chính, các ảnh còn lại tự thêm vào gallery.",
    )

    class Meta:
        model = SanPham
        exclude = ("hinh_anh", "ton_kho")


class GiaoDichKhoAdminForm(forms.ModelForm):
    class Meta:
        model = GiaoDichKho
        exclude = ("ton_truoc", "ton_sau", "created_by")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        store_field = self.fields.get("cua_hang")
        if store_field is not None:
            store_field.help_text = "Bắt buộc với phiếu xuất kho. Phiếu nhập sẽ tự lấy theo cửa hàng của nhân viên ký nếu để trống."
        nhan_vien_field = self.fields.get("nhan_vien")
        if nhan_vien_field is not None:
            nhan_vien_field.help_text = "Bắt buộc với phiếu nhập kho."
            selected_store = (self.data.get("cua_hang") or "").strip()
            if not selected_store and self.instance and self.instance.pk and self.instance.cua_hang_id:
                selected_store = str(self.instance.cua_hang_id)
            if selected_store.isdigit():
                nhan_vien_field.queryset = (
                    NhanVien.objects.filter(cua_hang_id=int(selected_store), co_quyen_nhap_kho=True)
                    .order_by("ho_ten")
                )
            else:
                nhan_vien_field.queryset = NhanVien.objects.none()
            nhan_vien_field.widget.attrs["data-employee-endpoint"] = "/admin/stores/0/employees/"
        chu_ky_field = self.fields.get("chu_ky")
        if chu_ky_field is not None:
            chu_ky_field.help_text = "Tải ảnh chữ ký của nhân viên khi nhập kho."


class TrangGioiThieuAdminForm(forms.ModelForm):
    gallery_images = MultipleImageField(
        label="Ảnh thư viện",
        required=False,
        widget=MultipleImageInput(attrs={"multiple": True, "accept": "image/*"}),
        help_text="Có thể chọn nhiều ảnh một lần để thêm vào thư viện ảnh của trang giới thiệu.",
    )
    gallery_captions = forms.CharField(
        label="Mô tả ảnh mới",
        required=False,
        widget=forms.Textarea(
            attrs={
                "rows": 4,
                "placeholder": "Mỗi dòng ứng với một ảnh mới theo đúng thứ tự đã chọn.",
            }
        ),
        help_text="Ví dụ chọn 3 ảnh thì nhập 3 dòng mô tả tương ứng cho 3 ảnh đó.",
    )

    class Meta:
        model = TrangGioiThieu
        fields = ("tieu_de", "mo_ta_ngan", "noi_dung", "anh_bia", "anh_noi_dung_1", "anh_noi_dung_2", "anh_noi_dung_3")
        widgets = {
            "mo_ta_ngan": forms.Textarea(attrs={"rows": 3, "placeholder": "Đoạn giới thiệu ngắn ở phần mở đầu."}),
            "noi_dung": forms.Textarea(attrs={"rows": 12, "placeholder": "Viết nội dung giới thiệu chi tiết cho quản lý tại đây..."}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["tieu_de"].help_text = "Tiêu đề chính của bài giới thiệu."
        self.fields["mo_ta_ngan"].help_text = "Đoạn mô tả ngắn để làm phần tóm tắt."
        self.fields["noi_dung"].help_text = "Có thể xuống dòng để chia đoạn nội dung cho bài viết."
        self.fields["anh_bia"].help_text = "Ảnh lớn xuất hiện ở phần đầu trang."
        self.fields["anh_noi_dung_1"].help_text = "Ảnh minh họa thứ nhất."
        self.fields["anh_noi_dung_2"].help_text = "Ảnh minh họa thứ hai."
        self.fields["anh_noi_dung_3"].help_text = "Ảnh minh họa thứ ba."


class KhuyenMaiAdminForm(forms.ModelForm):
    class Meta:
        model = KhuyenMai
        fields = "__all__"
        widgets = {
            "ma_code": forms.TextInput(
                attrs={
                    "placeholder": "Ví dụ: GIAM10 hoặc FREESHIP50",
                    "style": "text-transform:uppercase;",
                }
            ),
            "ten": forms.TextInput(attrs={"placeholder": "Ví dụ: Giảm 10% cho đơn online"}),
            "mo_ta": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Giải thích ngắn: áp dụng cho đơn online, giới hạn theo thương hiệu hoặc thời gian...",
                }
            ),
            "gia_tri_giam": forms.NumberInput(attrs={"placeholder": "Ví dụ: 10 hoặc 50000", "min": "0"}),
            "gia_tri_don_hang_toi_thieu": forms.NumberInput(attrs={"placeholder": "Ví dụ: 100000", "min": "0"}),
            "giam_toi_da": forms.NumberInput(attrs={"placeholder": "Để trống nếu không giới hạn", "min": "0"}),
            "ngay_bat_dau": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "ngay_ket_thuc": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["ma_code"].help_text = "Mã khách hàng nhập ở checkout. Nên dùng chữ in hoa, không dấu, không khoảng trắng."
        self.fields["loai_giam"].help_text = "Chọn 'Giảm theo phần trăm' nếu muốn nhập 10, 15, 20...; chọn 'Giảm số tiền' nếu muốn nhập trực tiếp số tiền."
        self.fields["gia_tri_giam"].help_text = "Nếu giảm theo phần trăm: nhập từ 1 đến 100. Nếu giảm số tiền: nhập số tiền giảm theo VND."
        self.fields["gia_tri_don_hang_toi_thieu"].help_text = "Chỉ cho phép áp dụng voucher khi đơn hàng đạt ít nhất số tiền này."
        self.fields["giam_toi_da"].help_text = "Chỉ dùng khi giảm theo phần trăm để giới hạn số tiền giảm tối đa."
        self.fields["dang_ap_dung"].help_text = "Bỏ chọn nếu muốn tạm khóa voucher mà không cần xóa."
        self.fields["ngay_bat_dau"].help_text = "Để trống nếu voucher có hiệu lực ngay."
        self.fields["ngay_ket_thuc"].help_text = "Để trống nếu voucher không có ngày hết hạn."
        self.fields["thuong_hieu"].help_text = "Nếu chọn thương hiệu, voucher chỉ áp dụng cho các sản phẩm thuộc thương hiệu đó."
        self.fields["cua_hang"].help_text = "Nếu chọn cửa hàng, voucher hiện được xem là ưu đãi mua tại cửa hàng và sẽ không áp dụng cho checkout online."

    def clean_ma_code(self):
        code = _normalize_voucher_code(self.cleaned_data.get("ma_code"))
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


def _is_admin_user(user):
    if not user.is_authenticated:
        return False
    if not user.is_active:
        return False
    return _ensure_user_role(user) in INTERNAL_ROLES


def _is_regular_user(user):
    return user.is_authenticated and not _is_admin_user(user)


def _require_regular_user(request):
    if _is_regular_user(request.user):
        return None
    if _is_admin_user(request.user):
        return redirect("store:admin_dashboard")
    return redirect("store:user_login")


def _require_customer_account(request):
    if _is_regular_user(request.user):
        return None
    next_url = request.POST.get("next") or request.get_full_path() or reverse("store:product_catalog")
    if _is_admin_user(request.user):
        logout(request)
    login_url = reverse("store:user_login")
    if next_url:
        login_url = f"{login_url}?next={next_url}"
    return redirect(login_url)


def _cart_session(request):
    return request.session.setdefault("cart", {})


def _cart_entry_key(product_id, store_id):
    return f"{int(product_id)}:{int(store_id)}"


def _parse_cart_entry_key(raw_key):
    key = str(raw_key or "").strip()
    if ":" not in key:
        if key.isdigit():
            return int(key), None
        return None, None
    product_id, store_id = key.split(":", 1)
    if not product_id.isdigit() or not store_id.isdigit():
        return None, None
    return int(product_id), int(store_id)


def _find_default_store_for_product(product_id):
    return (
        TonKhoCuaHang.objects.filter(san_pham_id=product_id, ton_kho__gt=0)
        .select_related("cua_hang")
        .order_by("-ton_kho", "cua_hang__ten", "pk")
        .first()
    )


def _remember_post_login_cart_action(request, product_id, next_url, store_id=None):
    request.session["post_login_cart_action"] = {
        "product_id": int(product_id),
        "store_id": int(store_id) if store_id else None,
        "next": next_url or reverse("store:cart"),
    }
    request.session.modified = True


def _resume_post_login_cart_action(request):
    payload = request.session.pop("post_login_cart_action", None)
    if not payload:
        return None

    product_id = payload.get("product_id")
    if product_id:
        cart = _cart_session(request)
        store_id = payload.get("store_id")
        if not store_id:
            stock_row = _find_default_store_for_product(product_id)
            store_id = stock_row.cua_hang_id if stock_row else None
        key = _cart_entry_key(product_id, store_id) if store_id else str(product_id)
        cart[key] = int(cart.get(key, 0)) + 1
        request.session.modified = True
    return payload.get("next") or reverse("store:cart")


def _format_currency(value):
    try:
        amount = int(Decimal(value))
    except Exception:
        amount = 0
    return f"{amount:,}".replace(",", ".") + " đ"


def _mojibake_score(value: str) -> int:
    if not isinstance(value, str) or not value:
        return 0
    markers = [
        "Ã", "Â", "Ä", "Å", "Æ", "Ç", "È", "É", "Ê", "Ë", "Ì", "Í", "Î", "Ï",
        "Ð", "Ñ", "Ò", "Ó", "Ô", "Õ", "Ö", "Ø", "Ù", "Ú", "Û", "Ü", "Ý", "Þ",
        "ß", "�", "á»", "áº", "Ä‘", "Æ°", "Tá»", "Nháº", "KhÃ", "Há»", "Cá»",
        "ThÃ", "Ä", "Â ",
    ]
    return sum(value.count(marker) for marker in markers)


def _fix_text(value):
    if not isinstance(value, str) or not value:
        return value
    best = value
    best_score = _mojibake_score(best)
    probe = best
    for _ in range(2):
        try:
            candidate = probe.encode("latin1").decode("utf-8")
        except Exception:
            break
        candidate_score = _mojibake_score(candidate)
        if candidate_score <= best_score and candidate != best:
            best = candidate
            best_score = candidate_score
            probe = candidate
            continue
        break
    return best


def _fix_text_dict(data):
    return {key: _fix_text(value) if isinstance(value, str) else value for key, value in data.items()}


def u(value: str) -> str:
    return _fix_text(value)


def _parse_coordinate(raw_value):
    text = (raw_value or "").strip()
    if not text:
        return None
    try:
        value = float(text)
    except (TypeError, ValueError):
        raise ValidationError("Tọa độ giao hàng không hợp lệ.")
    return value


def _parse_latitude(raw_value):
    value = _parse_coordinate(raw_value)
    if value is None:
        return None
    if value < -90 or value > 90:
        raise ValidationError("Vĩ độ giao hàng phải nằm trong khoảng từ -90 đến 90.")
    return value


def _parse_longitude(raw_value):
    value = _parse_coordinate(raw_value)
    if value is None:
        return None
    if value < -180 or value > 180:
        raise ValidationError("Kinh độ giao hàng phải nằm trong khoảng từ -180 đến 180.")
    return value


def _normalize_voucher_code(value):
    return re.sub(r"\s+", "", (value or "").upper())


def _line_total_for_item(item):
    line_total = item.get("line_total")
    if line_total is not None:
        return Decimal(line_total)
    return (item.get("unit_price") or Decimal("0")) * (item.get("quantity") or 0)


SHIPPING_BASE_DISTANCE_KM = Decimal("2")
SHIPPING_BASE_FEE = Decimal("15000")
SHIPPING_RATE_2_TO_10_KM = Decimal("5000")
SHIPPING_RATE_OVER_10_KM = Decimal("7000")


def _round_decimal(value):
    return Decimal(value or 0).quantize(Decimal("1"), rounding=ROUND_HALF_UP)


def _distance_km_between_points(lat1, lng1, lat2, lng2):
    if None in {lat1, lng1, lat2, lng2}:
        return None
    radius_km = 6371.0
    phi1 = math.radians(float(lat1))
    phi2 = math.radians(float(lat2))
    d_phi = math.radians(float(lat2) - float(lat1))
    d_lambda = math.radians(float(lng2) - float(lng1))
    a = (
        math.sin(d_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return Decimal(str(radius_km * c))


def _calculate_shipping_fee(distance_km):
    if distance_km is None:
        return Decimal("0")
    distance = max(Decimal(distance_km), Decimal("0"))
    fee = SHIPPING_BASE_FEE
    if distance <= SHIPPING_BASE_DISTANCE_KM:
        return _round_decimal(fee)
    middle_distance = min(distance, Decimal("10")) - SHIPPING_BASE_DISTANCE_KM
    if middle_distance > 0:
        fee += middle_distance * SHIPPING_RATE_2_TO_10_KM
    extra_distance = distance - Decimal("10")
    if extra_distance > 0:
        fee += extra_distance * SHIPPING_RATE_OVER_10_KM
    return _round_decimal(fee)


def _group_cart_items_by_store(items, delivery_lat=None, delivery_lng=None):
    groups = []
    group_map = {}
    for item in items:
        store = item.get("store")
        if store is None:
            continue
        group = group_map.get(store.pk)
        if group is None:
            distance_km = _distance_km_between_points(
                getattr(store, "vi_do", None),
                getattr(store, "kinh_do", None),
                delivery_lat,
                delivery_lng,
            )
            shipping_pending = distance_km is None
            shipping_fee = _calculate_shipping_fee(distance_km) if distance_km is not None else None
            group = {
                "store": store,
                "items": [],
                "subtotal": Decimal("0"),
                "total_quantity": 0,
                "distance_km": distance_km,
                "shipping_pending": shipping_pending,
                "shipping_fee": shipping_fee,
            }
            group_map[store.pk] = group
            groups.append(group)
        line_total = _line_total_for_item(item)
        group["items"].append(item)
        group["subtotal"] += line_total
        group["total_quantity"] += int(item.get("quantity") or 0)
    for group in groups:
        group["display_subtotal"] = _format_currency(group["subtotal"])
        group["display_shipping_fee"] = _format_currency(group["shipping_fee"]) if group["shipping_fee"] is not None else "Chưa tính"
        group["distance_label"] = (
            f"{group['distance_km']:.2f} km" if group["distance_km"] is not None else "Nhập tọa độ giao hàng"
        )
    return groups


def _allocate_discount_to_groups(groups, discount_amount):
    discount_total = Decimal(discount_amount or 0)
    if discount_total <= 0 or not groups:
        for group in groups:
            group["discount_amount"] = Decimal("0")
            shipping_fee = group["shipping_fee"] if group["shipping_fee"] is not None else Decimal("0")
            group["merchandise_total"] = group["subtotal"]
            group["final_amount"] = group["subtotal"] + shipping_fee
            group["display_discount_amount"] = _format_currency(0)
            if group.get("shipping_pending"):
                group["display_final_amount"] = f"{_format_currency(group['subtotal'])} + ship"
            else:
                group["display_final_amount"] = _format_currency(group["final_amount"])
        return groups

    subtotal_total = sum((group["subtotal"] for group in groups), Decimal("0"))
    remaining_discount = discount_total
    last_index = len(groups) - 1
    for index, group in enumerate(groups):
        if subtotal_total <= 0:
            discount_share = Decimal("0")
        elif index == last_index:
            discount_share = remaining_discount
        else:
            ratio = group["subtotal"] / subtotal_total
            discount_share = _round_decimal(discount_total * ratio)
            discount_share = min(discount_share, remaining_discount)
        remaining_discount -= discount_share
        group["discount_amount"] = discount_share
        merchandise_total = max(group["subtotal"] - discount_share, Decimal("0"))
        shipping_fee = group["shipping_fee"] if group["shipping_fee"] is not None else Decimal("0")
        group["merchandise_total"] = merchandise_total
        group["final_amount"] = merchandise_total + shipping_fee
        group["display_discount_amount"] = _format_currency(discount_share)
        if group.get("shipping_pending"):
            group["display_final_amount"] = f"{_format_currency(merchandise_total)} + ship"
        else:
            group["display_final_amount"] = _format_currency(group["final_amount"])
    return groups


VOUCHER_PRODUCT_RULES = {
    "COMBO5K": {"all_keywords": ["mi tron", "pepsi"]},
    "FROSTER33": {"any_keywords": ["froster"]},
    "YOUUS50": {"any_keywords": ["youus"]},
    "TOK10": {"any_keywords": ["tokbokki"]},
}


def _normalize_matching_text(value):
    value = unicodedata.normalize("NFKD", str(value or ""))
    value = "".join(char for char in value if not unicodedata.combining(char))
    value = re.sub(r"\s+", " ", value).strip().lower()
    return value


def _filter_voucher_eligible_items(voucher, items):
    eligible_items = list(items)

    allowed_brand_ids = list(voucher.thuong_hieu.values_list("pk", flat=True))
    if allowed_brand_ids:
        eligible_items = [
            item for item in eligible_items if item["product"].thuong_hieu_id in allowed_brand_ids
        ]

    rule = VOUCHER_PRODUCT_RULES.get(_normalize_voucher_code(voucher.ma_code))
    if not rule:
        return eligible_items

    normalized_items = [
        (item, _normalize_matching_text(getattr(item["product"], "ten", "")))
        for item in eligible_items
    ]

    any_keywords = [_normalize_matching_text(keyword) for keyword in rule.get("any_keywords", [])]
    if any_keywords:
        normalized_items = [
            (item, normalized_name)
            for item, normalized_name in normalized_items
            if any(keyword in normalized_name for keyword in any_keywords)
        ]

    all_keywords = [_normalize_matching_text(keyword) for keyword in rule.get("all_keywords", [])]
    if all_keywords:
        matched_keywords = {
            keyword
            for _, normalized_name in normalized_items
            for keyword in all_keywords
            if keyword in normalized_name
        }
        if not all(keyword in matched_keywords for keyword in all_keywords):
            return []
        normalized_items = [
            (item, normalized_name)
            for item, normalized_name in normalized_items
            if any(keyword in normalized_name for keyword in all_keywords)
        ]

    return [item for item, _ in normalized_items]


def _resolve_checkout_voucher(raw_code, items, subtotal_amount):
    code = _normalize_voucher_code(raw_code)
    if not code:
        return None, Decimal("0")

    voucher = (
        KhuyenMai.objects.prefetch_related("thuong_hieu", "cua_hang")
        .filter(ma_code__iexact=code)
        .order_by("-id")
        .first()
    )
    if voucher is None:
        raise ValidationError("Mã voucher không tồn tại.")
    if not voucher.dang_ap_dung:
        raise ValidationError("Voucher này hiện không còn áp dụng.")

    now = timezone.now()
    if voucher.ngay_bat_dau and voucher.ngay_bat_dau > now:
        raise ValidationError("Voucher này chưa đến thời gian sử dụng.")
    if voucher.ngay_ket_thuc and voucher.ngay_ket_thuc < now:
        raise ValidationError("Voucher này đã hết hạn.")
    if voucher.cua_hang.exists():
        raise ValidationError("Voucher này chỉ áp dụng cho mua tại cửa hàng.")

    subtotal_amount = Decimal(subtotal_amount or 0)
    minimum_order = Decimal(voucher.gia_tri_don_hang_toi_thieu or 0)
    if subtotal_amount < minimum_order:
        raise ValidationError(
            f"Đơn hàng cần tối thiểu {_format_currency(minimum_order)} để áp dụng voucher này."
        )

    eligible_items = _filter_voucher_eligible_items(voucher, items)
    eligible_total = sum((_line_total_for_item(item) for item in eligible_items), Decimal("0"))
    if eligible_total <= 0:
        raise ValidationError("Voucher này không áp dụng cho sản phẩm đang có trong giỏ hàng.")

    discount_value = Decimal(voucher.gia_tri_giam or 0)
    if discount_value <= 0:
        raise ValidationError("Voucher này chưa được cấu hình giá trị giảm hợp lệ.")

    if voucher.loai_giam == "percent":
        discount_amount = (eligible_total * discount_value) / Decimal("100")
        if voucher.giam_toi_da:
            discount_amount = min(discount_amount, Decimal(voucher.giam_toi_da))
    else:
        discount_amount = discount_value

    discount_amount = min(discount_amount, eligible_total, subtotal_amount)
    if discount_amount <= 0:
        raise ValidationError("Voucher này không tạo ra giá trị giảm hợp lệ.")

    return voucher, discount_amount


def _get_checkout_available_vouchers(items, subtotal_amount):
    vouchers = (
        KhuyenMai.objects.prefetch_related("thuong_hieu", "cua_hang")
        .exclude(ma_code__isnull=True)
        .exclude(ma_code__exact="")
        .filter(dang_ap_dung=True)
        .order_by("-id")[:20]
    )
    available = []
    for voucher in vouchers:
        code = _normalize_voucher_code(voucher.ma_code)
        if not code:
            continue
        try:
            _, discount_amount = _resolve_checkout_voucher(code, items, subtotal_amount)
        except ValidationError:
            continue
        available.append(
            {
                "code": code,
                "title": voucher.ten,
                "description": voucher.mo_ta,
                "discount_amount": discount_amount,
                "display_discount_amount": _format_currency(discount_amount),
                "minimum_order_amount": Decimal(voucher.gia_tri_don_hang_toi_thieu or 0),
                "display_minimum_order_amount": _format_currency(voucher.gia_tri_don_hang_toi_thieu or 0),
            }
        )
    return available


def _get_customer_profile(user):
    profile, _ = HoSoKhachHang.objects.get_or_create(user=user)
    return profile


def _review_media_kind(uploaded_file):
    content_type = (getattr(uploaded_file, "content_type", "") or "").lower()
    if content_type.startswith("image/"):
        return "image"
    if content_type.startswith("video/"):
        return "video"
    return ""


def _serialize_review_media(media_obj):
    url = ""
    try:
        if media_obj.tep and getattr(media_obj.tep, "url", ""):
            url = media_obj.tep.url
    except Exception:
        url = ""
    return {
        "id": media_obj.pk,
        "kind": media_obj.loai,
        "url": url,
        "name": media_obj.tep.name.rsplit("/", 1)[-1] if getattr(media_obj, "tep", None) else "",
    }


def _serialize_store_review(review, current_user=None):
    profile = getattr(review.user, "ho_so_khach_hang", None)
    avatar_url = ""
    try:
        if profile and profile.avatar and getattr(profile.avatar, "url", ""):
            avatar_url = profile.avatar.url
    except Exception:
        avatar_url = ""
    return {
        "id": review.pk,
        "stars": review.so_sao,
        "comment": review.binh_luan or "",
        "created_at": timezone.localtime(review.created_at).strftime("%d/%m/%Y %H:%M"),
        "author": _user_display_name(review.user),
        "avatar_url": avatar_url,
        "is_owner": bool(current_user and current_user.is_authenticated and current_user.pk == review.user_id),
        "media": [_serialize_review_media(item) for item in review.tep_dinh_kem.all()],
    }


def _store_review_payload(store, current_user=None):
    reviews_qs = (
        DanhGiaCuaHang.objects.filter(cua_hang=store)
        .select_related("user", "user__ho_so_khach_hang")
        .prefetch_related("tep_dinh_kem")
    )
    review_stats = DanhGiaCuaHang.objects.filter(cua_hang=store).aggregate(
        avg_stars=Coalesce(dj_models.Avg("so_sao"), 0.0),
        total_reviews=Coalesce(dj_models.Count("id", distinct=True), 0),
    )
    total_media = TepDanhGiaCuaHang.objects.filter(danh_gia__cua_hang=store).count()
    current_user_review = None
    if current_user and current_user.is_authenticated:
        current_user_review = reviews_qs.filter(user=current_user).first()

    return {
        "store": {
            "id": store.pk,
            "name": store.ten,
            "brand": store.chuoi.ten,
            "address": store.dia_chi,
            "district": store.quan_huyen,
        },
        "summary": {
            "average_stars": round(float(review_stats["avg_stars"] or 0), 1),
            "total_reviews": int(review_stats["total_reviews"] or 0),
            "total_media": int(total_media or 0),
        },
        "current_user_review": _serialize_store_review(current_user_review, current_user) if current_user_review else None,
        "reviews": [_serialize_store_review(item, current_user) for item in reviews_qs],
        "can_review": bool(current_user and _is_regular_user(current_user)),
        "requires_login": not bool(current_user and _is_regular_user(current_user)),
    }


def _refresh_authenticated_user(request):
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return user
    try:
        user.refresh_from_db()
    except Exception:
        return user
    return user


def _purge_expired_trash():
    TrashRecord.objects.filter(expires_at__lt=timezone.now()).delete()


def _serialize_for_trash(obj):
    data = {}
    for field in obj._meta.fields:
        if isinstance(field, dj_models.ForeignKey):
            data[field.name] = getattr(obj, field.attname)
            continue
        if field.get_internal_type() in {"ImageField", "FileField"}:
            value = getattr(obj, field.name)
            data[field.name] = str(value) if value else ""
            continue
        data[field.name] = field.value_from_object(obj)
    for field in obj._meta.many_to_many:
        data[field.name] = list(getattr(obj, field.name).values_list("pk", flat=True))
    data = json.loads(json.dumps(data, cls=DjangoJSONEncoder))
    data.pop("id", None)
    return data


def _move_to_trash(obj, data=None, *, object_id=None):
    payload = data if data is not None else _serialize_for_trash(obj)
    retention_days = getattr(settings, "TRASH_RETENTION_DAYS", 15)
    resolved_object_id = object_id
    if resolved_object_id in ("", None):
        resolved_object_id = getattr(obj, "pk", None)
    resolved_object_id = "" if resolved_object_id in ("", None) else str(resolved_object_id)
    TrashRecord.objects.create(
        model_label=obj._meta.label_lower,
        object_id=resolved_object_id,
        data=payload,
        expires_at=timezone.now() + timedelta(days=retention_days),
    )


def _model_slug_from_label(label: str) -> str:
    try:
        model = apps.get_model(label)
    except Exception:
        return label.split(".")[-1]
    for slug, registered in MODEL_REGISTRY.items():
        if registered is model:
            return slug
    return model._meta.model_name


def _trash_display_name(data: dict, model_label: str = "") -> str:
    model_key = (model_label or "").split(".")[-1].lower()

    if model_key == "giaodichkho":
        movement_type = (data.get("loai") or "").strip().lower()
        quantity = data.get("so_luong")
        product_id = data.get("san_pham")
        product_name = ""
        if product_id not in (None, ""):
            product_name = SanPham.objects.filter(pk=product_id).values_list("ten", flat=True).first() or f"SP #{product_id}"
        type_label = "Nhập kho" if movement_type == "import" else "Xuất kho" if movement_type == "export" else "Giao dịch kho"
        if product_name and quantity not in (None, ""):
            return f"{type_label} - {product_name} x {quantity}"
        if product_name:
            return f"{type_label} - {product_name}"
        if quantity not in (None, ""):
            return f"{type_label} x {quantity}"
        return type_label

    if model_key == "donhang":
        order_id = data.get("id") or data.get("object_id")
        receiver = data.get("ho_ten_nguoi_nhan")
        if order_id and receiver:
            return f"Đơn hàng #{order_id} - {receiver}"
        if order_id:
            return f"Đơn hàng #{order_id}"

    if model_key == "chitietdonhang":
        quantity = data.get("so_luong")
        product_id = data.get("san_pham")
        product_name = ""
        if product_id not in (None, ""):
            product_name = SanPham.objects.filter(pk=product_id).values_list("ten", flat=True).first() or f"SP #{product_id}"
        if product_name and quantity not in (None, ""):
            return f"{product_name} x {quantity}"

    for key in ("ten", "ho_ten", "ho_ten_nguoi_nhan", "username", "email"):
        value = data.get(key)
        if value:
            return str(value)
    return ""


def _address_type_label(address):
    return dict(DiaChiKhachHang.LOAI_DIA_CHI_CHOICES).get(address.loai_dia_chi, "Khác")


def _format_customer_address(address):
    if not address:
        return ""
    parts = [
        (address.dia_chi_cu_the or "").strip(),
        (address.phuong_xa or "").strip(),
        (address.quan_huyen or "").strip(),
        (address.tinh_thanh or "").strip(),
    ]
    return ", ".join(part for part in parts if part)


def _customer_addresses_qs(user):
    return DiaChiKhachHang.objects.filter(user=user).order_by("-mac_dinh", "-created_at", "-id")


def _get_default_customer_address(user):
    return _customer_addresses_qs(user).filter(mac_dinh=True).first() or _customer_addresses_qs(user).first()


def _sync_legacy_profile_address(user):
    profile = _get_customer_profile(user)
    default_address = _get_default_customer_address(user)
    full_address = _format_customer_address(default_address)
    if profile.dia_chi != full_address:
        profile.dia_chi = full_address
        profile.save(update_fields=["dia_chi"])


def _normalize_customer_address_defaults(user, target=None):
    addresses = list(_customer_addresses_qs(user))
    if not addresses:
        profile = _get_customer_profile(user)
        if profile.dia_chi:
            profile.dia_chi = ""
            profile.save(update_fields=["dia_chi"])
        return

    selected = None
    if target is not None:
        selected = next((item for item in addresses if item.pk == target.pk), None)
    if selected is None:
        selected = next((item for item in addresses if item.mac_dinh), None) or addresses[0]

    DiaChiKhachHang.objects.filter(user=user).exclude(pk=selected.pk).update(mac_dinh=False)
    if not selected.mac_dinh:
        selected.mac_dinh = True
        selected.save(update_fields=["mac_dinh"])

    _sync_legacy_profile_address(user)


def _send_feedback_emails(feedback):
    user_subject = "Circle K & GS25 đã nhận góp ý của bạn"
    user_message = (
        f"Xin chào {feedback.ho_ten},\n\n"
        "Chúng tôi đã nhận được góp ý của bạn và sẽ phản hồi sớm nhất có thể.\n\n"
        f"Chủ đề: {feedback.chu_de}\n"
        f"Nội dung: {feedback.noi_dung}\n\n"
        "Cảm ơn bạn đã đồng hành cùng Circle K & GS25."
    )
    admin_subject = f"Góp ý mới từ website: {feedback.chu_de}"
    admin_message = (
        "Hệ thống vừa ghi nhận một góp ý mới.\n\n"
        f"Họ tên: {feedback.ho_ten}\n"
        f"Email: {feedback.email}\n"
        f"Số điện thoại: {feedback.so_dien_thoai or '-'}\n"
        f"Chủ đề: {feedback.chu_de}\n"
        f"Nội dung:\n{feedback.noi_dung}\n"
    )

    send_mail(
        user_subject,
        user_message,
        settings.DEFAULT_FROM_EMAIL,
        [feedback.email],
        fail_silently=False,
    )
    send_mail(
        admin_subject,
        admin_message,
        settings.DEFAULT_FROM_EMAIL,
        [settings.FEEDBACK_NOTIFICATION_EMAIL],
        fail_silently=False,
    )


def _send_order_confirmation(order, items):
    customer_email = (order.khach_hang.email or "").strip()
    if not customer_email:
        return False
    created_at = timezone.localtime(order.created_at) if order.created_at else timezone.localtime(timezone.now())
    created_text = created_at.strftime("%d/%m/%Y %H:%M")
    item_lines = []
    for item in items:
        line_total = item.get("line_total")
        if line_total is None:
            line_total = (item.get("unit_price") or Decimal("0")) * (item.get("quantity") or 0)
        item_lines.append(
            f"- {item['product'].ten} x {item['quantity']} = {_format_currency(line_total)}"
        )
    items_text = "\n".join(item_lines) if item_lines else "-"
    subject = f"Xác nhận đơn hàng {order.pk} - Circle K & GS25"
    message = (
        f"Xin chào {order.ho_ten_nguoi_nhan},\n\n"
        "Cảm ơn bạn đã đặt hàng tại Circle K & GS25.\n"
        f"Mã đơn: {order.pk}\n"
        f"Thời gian đặt: {created_text}\n"
        f"Người nhận: {order.ho_ten_nguoi_nhan}\n"
        f"Số điện thoại: {order.so_dien_thoai}\n"
        f"Địa chỉ giao hàng: {order.dia_chi_giao_hang}\n"
        f"Ghi chú: {order.ghi_chu or '-'}\n\n"
        "Chi tiết đơn hàng:\n"
        f"{items_text}\n\n"
        f"Tổng số lượng: {order.tong_so_luong}\n"
        f"Tạm tính: {_format_currency(order.tong_tien_truoc_giam or order.tong_tien)}\n"
        f"Voucher: {order.ma_voucher_ap_dung or '-'}\n"
        f"Giảm giá: {_format_currency(order.giam_gia)}\n"
        f"Tổng tiền: {_format_currency(order.tong_tien)}\n\n"
        "Chúng tôi sẽ liên hệ với bạn để xác nhận và giao hàng sớm nhất.\n"
        "Trân trọng."
    )
    customer_conn = get_connection(
        host=settings.ORDER_EMAIL_HOST,
        port=settings.ORDER_EMAIL_PORT,
        username=settings.ORDER_EMAIL_HOST_USER,
        password=settings.ORDER_EMAIL_HOST_PASSWORD,
        use_tls=settings.ORDER_EMAIL_USE_TLS,
        use_ssl=settings.ORDER_EMAIL_USE_SSL,
        timeout=settings.EMAIL_TIMEOUT,
    )
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [customer_email],
        fail_silently=False,
        connection=customer_conn,
    )
    return True


def _cart_items(request):
    cart = _cart_session(request)
    parsed_entries = []
    product_ids = set()
    store_ids = set()
    for raw_key, quantity in cart.items():
        product_id, store_id = _parse_cart_entry_key(raw_key)
        if not product_id:
            continue
        parsed_entries.append((str(raw_key), product_id, store_id, quantity))
        product_ids.add(product_id)
        if store_id:
            store_ids.add(store_id)

    products = {p.pk: p for p in SanPham.objects.filter(pk__in=product_ids)}
    stores = {store.pk: store for store in CuaHang.objects.select_related("chuoi").filter(pk__in=store_ids)}
    stock_rows = (
        TonKhoCuaHang.objects.filter(san_pham_id__in=product_ids)
        .select_related("cua_hang", "cua_hang__chuoi")
        .order_by("cua_hang__ten", "san_pham_id")
    )
    stock_map = {}
    default_store_map = {}
    for row in stock_rows:
        stock_map[(row.san_pham_id, row.cua_hang_id)] = int(row.ton_kho or 0)
        stores[row.cua_hang_id] = row.cua_hang
        if row.ton_kho > 0 and row.san_pham_id not in default_store_map:
            default_store_map[row.san_pham_id] = row.cua_hang_id

    items = []
    total_quantity = 0
    total_amount = Decimal("0")
    normalized_cart = {}
    cart_changed = False
    for raw_key, product_id, store_id, quantity in parsed_entries:
        try:
            product = products[int(product_id)]
        except Exception:
            continue
        resolved_store_id = store_id or default_store_map.get(product.pk)
        if not resolved_store_id:
            cart_changed = True
            continue
        available_stock = stock_map.get((product.pk, resolved_store_id), 0)
        qty = min(max(int(quantity), 0), available_stock)
        if qty <= 0:
            cart_changed = True
            continue
        normalized_key = _cart_entry_key(product.pk, resolved_store_id)
        normalized_cart[normalized_key] = normalized_cart.get(normalized_key, 0) + qty
        if normalized_key != raw_key or qty != int(quantity):
            cart_changed = True
        unit_price = product.gia_ban or Decimal("0")
        line_total = unit_price * qty
        total_quantity += qty
        total_amount += line_total
        store = stores.get(resolved_store_id)
        items.append(
            {
                "cart_key": normalized_key,
                "product": product,
                "store": store,
                "store_id": resolved_store_id,
                "quantity": qty,
                "unit_price": unit_price,
                "line_total": line_total,
            }
        )
    if cart_changed or normalized_cart != cart:
        request.session["cart"] = normalized_cart
        request.session.modified = True
    return items, total_quantity, total_amount


def _ensure_role_groups():
    groups = {}
    for role_value, _role_label in ROLE_CHOICES:
        groups[role_value], _ = Group.objects.get_or_create(name=role_value)
    return groups


def _ensure_user_role(user):
    groups = _ensure_role_groups()
    if not user or not user.is_authenticated:
        return None

    target_role = None
    for role_value, _role_label in ROLE_CHOICES:
        if user.groups.filter(name=role_value).exists():
            target_role = role_value
            break
    if target_role is None:
        for legacy_name, mapped_role in LEGACY_ROLE_MAP.items():
            if user.groups.filter(name=legacy_name).exists():
                target_role = mapped_role
                break
    if target_role is None:
        if user.is_superuser or user.is_staff:
            target_role = ROLE_SYSTEM_ADMIN
        else:
            target_role = ROLE_CUSTOMER

    target_group = groups[target_role]
    needs_group_sync = not user.groups.filter(pk=target_group.pk).exists() or user.groups.exclude(pk=target_group.pk).exists()
    expected_is_staff = target_role in INTERNAL_ROLES
    needs_staff_sync = user.is_staff != expected_is_staff

    if needs_group_sync:
        user.groups.set([target_group])
    if needs_staff_sync:
        user.is_staff = expected_is_staff
        user.save(update_fields=["is_staff"])

    return target_role


def _get_user_role(user):
    return _ensure_user_role(user) or ROLE_CUSTOMER


def _sync_user_role(user, role: str):
    groups = _ensure_role_groups()
    if role not in groups:
        role = ROLE_CUSTOMER
    user.groups.set([groups[role]])
    user.is_staff = role in INTERNAL_ROLES
    user.save(update_fields=["is_staff"])


def _role_label(role: str) -> str:
    return _fix_text(ROLE_LABELS.get(role, role))


def _current_user_role(user):
    return _get_user_role(user) if user and user.is_authenticated else ROLE_CUSTOMER


def _has_admin_page_access(user, page_key: str, action: str = "view") -> bool:
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    role = _current_user_role(user)
    allowed_roles = ADMIN_PAGE_ROLE_ACTIONS.get(page_key, {}).get(action, set())
    return role in allowed_roles


def _has_module_access(user, model_slug: str, action: str = "view") -> bool:
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    role = _current_user_role(user)
    action_map = MODULE_ROLE_ACTIONS.get(model_slug, {})
    allowed_roles = action_map.get(action, action_map.get("view", set()))
    return role in allowed_roles


def _require_admin_permission(request, page_key: str, action: str = "view"):
    unauthorized = _require_admin_user(request)
    if unauthorized:
        return unauthorized
    if _has_admin_page_access(request.user, page_key, action):
        return None
    messages.error(request, _admin_pref_context(request)["t"]["no_access"])
    return redirect("store:admin_dashboard")


def _require_module_permission(request, model_slug: str, action: str = "view"):
    unauthorized = _require_admin_user(request)
    if unauthorized:
        return unauthorized
    if _has_module_access(request.user, model_slug, action):
        return None
    messages.error(request, _admin_pref_context(request)["t"]["no_access"])
    return redirect("store:admin_dashboard")


def _clean_user_email(raw_email: str, exclude_user_id=None):
    email = (raw_email or "").strip().lower()
    if not email:
        return "", None

    try:
        validate_email(email)
    except ValidationError:
        return email, "Email không đúng định dạng."

    query = User.objects.filter(email__iexact=email)
    if exclude_user_id is not None:
        query = query.exclude(pk=exclude_user_id)
    if query.exists():
        return email, "Email đã tồn tại."

    return email, None


def _normalize_phone(raw_phone: str) -> str:
    digits = re.sub(r"\D", "", raw_phone or "")
    return digits


def _generate_register_otp(length: int = 6) -> str:
    return "".join(random.choices("0123456789", k=length))


OTP_COOLDOWN_SECONDS = 60
OTP_MAX_PER_DAY = 5


def _check_otp_rate_limit(request, *, key: str, cooldown_seconds=OTP_COOLDOWN_SECONDS, max_per_day=OTP_MAX_PER_DAY):
    now = timezone.now()
    state_map = request.session.get("otp_rate_limits") or {}
    state = state_map.get(key, {})
    today = now.strftime("%Y-%m-%d")
    if state.get("date") != today:
        state = {"date": today, "count": 0}
    last_sent = state.get("last_sent")
    if last_sent:
        wait_seconds = cooldown_seconds - (now.timestamp() - float(last_sent))
        if wait_seconds > 0:
            state_map[key] = state
            request.session["otp_rate_limits"] = state_map
            request.session.modified = True
            return False, f"Vui lòng chờ {int(wait_seconds)} giây rồi thử lại."
    if state.get("count", 0) >= max_per_day:
        state_map[key] = state
        request.session["otp_rate_limits"] = state_map
        request.session.modified = True
        return False, "Bạn đã vượt quá số lần gửi OTP trong ngày. Vui lòng thử lại vào ngày mai."
    return True, ""


def _record_otp_sent(request, *, key: str):
    now = timezone.now()
    state_map = request.session.get("otp_rate_limits") or {}
    state = state_map.get(key, {})
    today = now.strftime("%Y-%m-%d")
    if state.get("date") != today:
        state = {"date": today, "count": 0}
    state["last_sent"] = now.timestamp()
    state["count"] = int(state.get("count", 0)) + 1
    state_map[key] = state
    request.session["otp_rate_limits"] = state_map
    request.session.modified = True


def _otp_email_html(*, title: str, subtitle: str, otp_code: str, expires_text: str):
    return f"""
    <div style="font-family: Arial, sans-serif; background:#f6f8fb; padding:24px;">
      <div style="max-width:560px; margin:0 auto; background:#ffffff; border-radius:14px; padding:24px 24px 20px; border:1px solid #e8edf3;">
        <h2 style="margin:0 0 8px; color:#0f172a;">{title}</h2>
        <p style="margin:0 0 16px; color:#475569; line-height:1.6;">{subtitle}</p>
        <div style="background:#ecfeff; color:#0f766e; padding:14px 16px; border-radius:12px; font-size:20px; font-weight:700; text-align:center; letter-spacing:2px;">
          {otp_code}
        </div>
        <p style="margin:14px 0 0; color:#64748b; font-size:14px;">Mã có hiệu lực đến <strong>{expires_text}</strong>.</p>
        <p style="margin:12px 0 0; color:#94a3b8; font-size:13px;">Nếu bạn không yêu cầu, hãy bỏ qua email này.</p>
      </div>
    </div>
    """

def _clear_register_otp_session(request):
    request.session.pop("register_otp", None)
    request.session.pop("register_pending", None)
    request.session.modified = True


def _issue_register_otp(request, *, email: str, full_name: str, phone: str, username: str):
    allow, rate_error = _check_otp_rate_limit(request, key=f"register:{email}")
    if not allow:
        request.session["register_otp_error"] = rate_error
        request.session.modified = True
        return None

    otp_code = _generate_register_otp()
    expires_at = timezone.now() + timedelta(minutes=5)
    request.session["register_otp"] = {
        "code": otp_code,
        "expires_at": expires_at.timestamp(),
    }
    request.session.modified = True

    display_name = full_name or username or "bạn"
    expires_text = timezone.localtime(expires_at).strftime("%H:%M %d/%m/%Y")
    subject = "Mã OTP đăng ký tài khoản Circle K & GS25"
    message = (
        f"Xin chào {display_name},\n\n"
        f"Mã OTP của bạn là: {otp_code}\n"
        f"Mã có hiệu lực đến {expires_text} (5 phút).\n\n"
        f"Số điện thoại đăng ký: {phone or '-'}\n"
        "Nếu bạn không yêu cầu đăng ký, hãy bỏ qua email này.\n"
        "Trân trọng."
    )
    html_message = _otp_email_html(
        title="Xác nhận đăng ký tài khoản",
        subtitle=f"Xin chào {display_name}, đây là mã OTP để xác nhận đăng ký.",
        otp_code=otp_code,
        expires_text=expires_text,
    )
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
            html_message=html_message,
        )
    except Exception as exc:
        request.session["register_otp_error"] = str(exc)
        request.session.modified = True
        return None
    _record_otp_sent(request, key=f"register:{email}")
    return otp_code


def _client_ip(request) -> str:
    forwarded = (request.META.get("HTTP_X_FORWARDED_FOR") or "").split(",")[0].strip()
    return forwarded or (request.META.get("REMOTE_ADDR") or "")


def _client_user_agent(request) -> str:
    return (request.META.get("HTTP_USER_AGENT") or "")[:255]


def _issue_inventory_otp(request, movement):
    recipient = (movement.nhan_vien.email if movement.nhan_vien_id else "") or ""
    if not recipient:
        return None
    allow, rate_error = _check_otp_rate_limit(request, key=f"inventory:{recipient}")
    if not allow:
        return None
    otp_code = _generate_register_otp()
    expires_at = timezone.now() + timedelta(minutes=5)
    movement.otp_code_hash = make_password(otp_code)
    movement.otp_expires_at = expires_at
    movement.otp_recipient_email = recipient
    movement.otp_verified_at = None
    movement.otp_verified_by = None
    movement.otp_verified_ip = ""
    movement.otp_verified_user_agent = ""
    movement.save(
        update_fields=[
            "otp_code_hash",
            "otp_expires_at",
            "otp_recipient_email",
            "otp_verified_at",
            "otp_verified_by",
            "otp_verified_ip",
            "otp_verified_user_agent",
        ]
    )

    verify_url = request.build_absolute_uri(
        reverse("store:admin_inventory_verify_otp", args=[movement.pk])
    )
    verify_url = f"{verify_url}?code={otp_code}"
    expires_text = timezone.localtime(expires_at).strftime("%H:%M %d/%m/%Y")
    subject = "OTP xác nhận phiếu kho"
    message = (
        f"Xin chào {movement.nhan_vien.ho_ten if movement.nhan_vien_id else 'bạn'},\n\n"
        f"Mã OTP xác nhận phiếu kho #{movement.pk}: {otp_code}\n"
        f"Hiệu lực đến {expires_text}.\n"
        f"Bạn có thể xác nhận nhanh tại: {verify_url}\n\n"
        "Nếu bạn không yêu cầu xác nhận, hãy bỏ qua email này."
    )
    html_message = _otp_email_html(
        title=f"Xác nhận phiếu kho #{movement.pk}",
        subtitle="Vui lòng dùng mã OTP dưới đây để xác nhận phiếu kho.",
        otp_code=otp_code,
        expires_text=expires_text,
    )
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [recipient],
            fail_silently=False,
            html_message=html_message,
        )
    except Exception:
        return None
    _record_otp_sent(request, key=f"inventory:{recipient}")
    return otp_code


def _apply_signature_log(movement, request, *, previous_name: str | None = None):
    if not movement.chu_ky:
        return False
    if previous_name is not None and movement.chu_ky.name == previous_name and movement.signed_at:
        return False
    movement.signed_at = timezone.now()
    movement.signed_by = request.user if request.user.is_authenticated else None
    movement.signed_ip = _client_ip(request)
    movement.signed_user_agent = _client_user_agent(request)
    movement.save(update_fields=["signed_at", "signed_by", "signed_ip", "signed_user_agent"])
    return True


def _split_full_name(raw_name: str):
    full_name = " ".join((raw_name or "").split()).strip()
    if not full_name:
        return "", ""

    parts = full_name.split(" ")
    if len(parts) == 1:
        return parts[0], ""

    first_name = parts[-1]
    last_name = " ".join(parts[:-1])
    return first_name, last_name


def _user_display_name(user):
    full_name = " ".join(part for part in [user.last_name, user.first_name] if part).strip()
    if full_name:
        if (not user.first_name or not user.last_name) and user.username:
            username = user.username.strip()
            if username and username.lower() != full_name.lower() and username.isalpha():
                return f"{full_name} {username}"
        return full_name
    return user.get_full_name().strip() or user.username


def _user_header_notifications(user):
    notifications = _user_all_notifications(user, limit=4)

    if not notifications:
        notifications.append(
            {
                "title": u("Ch\u01b0a c\u00f3 th\u00f4ng b\u00e1o m\u1edbi"),
                "body": u("Khi c\u00f3 \u0111\u01a1n h\u00e0ng ho\u1eb7c c\u1eadp nh\u1eadt m\u1edbi, b\u1ea1n s\u1ebd th\u1ea5y t\u1ea1i \u0111\u00e2y."),
                "href": reverse("store:user_profile"),
                "is_new": False,
            }
        )

    return notifications


def _order_status_ui_text(order):
    return {
        "pending": "Chờ thanh toán" if order.trang_thai == "pending" and order.trang_thai_thanh_toan == "unpaid" else "Chờ xử lý",
        "confirmed": "Đã xác nhận",
        "shipping": "Chờ giao hàng",
        "delivered": "Đã giao",
        "done": "Hoàn thành",
        "cancelled": "Đã hủy",
    }.get(order.trang_thai, order.get_trang_thai_display())


def _order_status_notification_text(order):
    status_text = _order_status_ui_text(order)
    if order.trang_thai == "done":
        return f"Đơn #{order.pk} đã hoàn thành", status_text.lower()
    if order.trang_thai == "delivered":
        return f"Đơn #{order.pk} đã giao", status_text.lower()
    if order.trang_thai == "cancelled":
        return f"Đơn #{order.pk} đã hủy", status_text.lower()
    if order.trang_thai == "confirmed":
        return f"Đơn #{order.pk} đã xác nhận", status_text.lower()
    return f"Đơn #{order.pk} đang {status_text.lower()}", status_text.lower()


def _admin_header_notifications(limit=4):
    notifications = []
    for notice in Notification.objects.filter(resolved=False).order_by("-created_at")[:limit]:
        notifications.append(
            {
                "title": notice.title,
                "body": notice.message or u("C\u00f3 c\u1eadp nh\u1eadt m\u1edbi trong h\u1ec7 th\u1ed1ng qu\u1ea3n tr\u1ecb."),
                "href": reverse("store:admin_notifications"),
                "is_new": True,
                "timestamp": notice.created_at,
            }
        )
    return notifications


def _create_admin_notification(title, message, *, level="info", path="", method="", status_code=None):
    Notification.objects.create(
        level=(level or "info")[:20],
        title=(title or u("Th\u00f4ng b\u00e1o h\u1ec7 th\u1ed1ng"))[:200],
        message=message or "",
        path=(path or "")[:255],
        method=(method or "")[:10],
        status_code=status_code,
    )


def _notification_search_text(notification):
    raw_text = " ".join(
        filter(
            None,
            [
                getattr(notification, "title", "") or "",
                getattr(notification, "message", "") or "",
                getattr(notification, "path", "") or "",
            ],
        )
    )
    normalized = unicodedata.normalize("NFKD", raw_text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    return ascii_text.lower()



def _notification_extract_order_id(notification):
    path = (getattr(notification, "path", "") or "").strip()
    if path:
        parsed = urlparse(path)
        params = parse_qs(parsed.query)
        order_id = (params.get("order") or [None])[0]
        if order_id and str(order_id).isdigit():
            return int(order_id)

    haystack = _notification_search_text(notification)
    match = re.search(r"don\s*hang\s*moi\s*#(\d+)|don\s*#(\d+)|ma\s*don[:\s#]*(\d+)", haystack, re.IGNORECASE)
    if match:
        for group in match.groups():
            if group and str(group).isdigit():
                return int(group)
    return None



def _notification_extract_review_id(notification):
    path = (getattr(notification, "path", "") or "").strip()
    if not path:
        return None
    parsed = urlparse(path)
    params = parse_qs(parsed.query)
    review_id = (params.get("focus_review") or [None])[0]
    if review_id and str(review_id).isdigit():
        return int(review_id)
    return None



def _notification_category(notification):
    level = (getattr(notification, "level", "") or "").lower()
    path = (getattr(notification, "path", "") or "").lower()
    haystack = _notification_search_text(notification)

    if "danh-gia" in path or "focus_review" in path or "danh gia" in haystack:
        return "review"
    if "chi-tiet-don-hang" in path or "don-hang" in path or "don hang" in haystack:
        return "order"
    if level in {"error", "warning"}:
        return "error"
    return "system"



def _notification_target_path(notification):
    path = (getattr(notification, "path", "") or "").strip()
    if path:
        return path

    review_id = _notification_extract_review_id(notification)
    if review_id:
        return f"{reverse('store:admin_list', kwargs={'model_slug': 'danh-gia-cua-hang'})}?focus_review={review_id}"

    order_id = _notification_extract_order_id(notification)
    if order_id:
        return f"{reverse('store:admin_list', kwargs={'model_slug': ORDER_ITEM_MODULE_SLUG})}?order={order_id}"
    return ""



def _notification_thumbnail(notification):
    category = _notification_category(notification)

    if category == "review":
        review_id = _notification_extract_review_id(notification)
        if review_id:
            review = DanhGiaCuaHang.objects.filter(pk=review_id).prefetch_related("tep_dinh_kem").first()
            if review:
                media_items = _build_review_media_context(review)
                if media_items:
                    first_media = media_items[0]
                    return {
                        "kind": first_media["kind"],
                        "url": first_media["url"],
                        "label": "Danh gia",
                    }

    if category == "order":
        order_id = _notification_extract_order_id(notification)
        if order_id:
            order = DonHang.objects.filter(pk=order_id).prefetch_related("items__san_pham__hinh_anh_phu").first()
            if order:
                first_item = order.items.all().first()
                product = first_item.san_pham if first_item and first_item.san_pham_id else None
                if product:
                    try:
                        if product.hinh_anh:
                            return {"kind": "image", "url": product.hinh_anh.url, "label": "Đơn hàng"}
                    except Exception:
                        pass
                    extra_image = product.hinh_anh_phu.all().first()
                    if extra_image and extra_image.hinh_anh:
                        return {"kind": "image", "url": extra_image.hinh_anh.url, "label": "Đơn hàng"}

    return {"kind": "", "url": "", "label": ""}



def _build_notification_card(notification):
    target_path = _notification_target_path(notification)
    thumb = _notification_thumbnail(notification)
    full_message = ((getattr(notification, "message", "") or "").strip()) or "Không có nội dung chi tiết."
    preview = " ".join(full_message.split())
    if len(preview) > 180:
        preview = preview[:177].rstrip() + "..."
    return {
        "notification": notification,
        "category": _notification_category(notification),
        "target_path": target_path,
        "thumb_kind": thumb.get("kind", ""),
        "thumb_url": thumb.get("url", ""),
        "thumb_label": thumb.get("label", ""),
        "preview": preview,
        "full_message": full_message,
    }


def _user_all_notifications(user, limit=None):
    notifications = []
    orders_qs = (
        DonHang.objects.filter(khach_hang=user)
        .prefetch_related("items__san_pham__hinh_anh_phu")
        .order_by("-created_at")
    )
    if limit is not None:
        orders_qs = orders_qs[:limit]

    for order in orders_qs:
        first_item = order.items.all().first()
        item_name = first_item.san_pham.ten if first_item and first_item.san_pham_id else "đơn hàng của bạn"
        thumb_url = ""
        if first_item and first_item.san_pham_id:
            product = first_item.san_pham
            if product.hinh_anh:
                thumb_url = product.hinh_anh.url
            else:
                extra_image = product.hinh_anh_phu.all().first()
                thumb_url = extra_image.hinh_anh.url if extra_image and extra_image.hinh_anh else ""

        status_label = _order_status_ui_text(order)
        notification_title, notification_status_text = _order_status_notification_text(order)
        action_label = "Xem chi tiết"
        accent = "warm"
        if order.trang_thai == "done":
            action_label = "Mua lại"
            accent = "success"
        elif order.trang_thai == "cancelled":
            action_label = "Xem chi tiết"
            accent = "muted"

        notifications.append(
            {
                "title": notification_title,
                "body": f"{item_name} • {timezone.localtime(order.created_at).strftime('%d/%m/%Y %H:%M')}",
                "message": f"Đơn hàng #{order.pk} với sản phẩm {item_name} hiện ở trạng thái {notification_status_text}.",
                "href": reverse("store:order_detail", args=[order.pk]),
                "is_new": order.created_at >= timezone.now() - timedelta(days=2),
                "created_at": order.created_at,
                "created_text": timezone.localtime(order.created_at).strftime("%H:%M %d/%m/%Y"),
                "thumbnail_url": thumb_url,
                "status_label": status_label,
                "action_label": action_label,
                "accent": accent,
                "order_code": f"#{order.pk}",
            }
        )

    for notification in notifications:
        for key in ("title", "body", "message", "status_label", "action_label", "order_code"):
            if key in notification:
                notification[key] = _fix_text(notification[key])

    return notifications


def _mask_middle(value, *, prefix=2, suffix=2, mask="*"):
    raw = (value or "").strip()
    if not raw:
        return ""
    if len(raw) <= prefix + suffix:
        return raw[0] + (mask * max(len(raw) - 1, 0))
    return f"{raw[:prefix]}{mask * (len(raw) - prefix - suffix)}{raw[-suffix:]}"


def _user_profile_extra_state(request):
    state = request.session.get("user_profile_extra_state") or {}
    return {
        "gender": state.get("gender") or "other",
        "birth_date": state.get("birth_date") or "",
    }


def _save_user_profile_extra_state(request, payload):
    request.session["user_profile_extra_state"] = payload
    request.session.modified = True


def _user_notification_settings_state(request):
    state = request.session.get("user_notification_settings_state") or {}
    defaults = {
        "email_enabled": True,
        "email_order": True,
        "email_promotion": False,
        "email_survey": False,
        "sms_enabled": True,
        "sms_promotion": False,
        "zalo_enabled": True,
        "zalo_promotion": True,
    }
    defaults.update({key: bool(value) for key, value in state.items() if key in defaults})
    return defaults


def _save_user_notification_settings_state(request, payload):
    request.session["user_notification_settings_state"] = payload
    request.session.modified = True


def _user_privacy_state(request):
    state = request.session.get("user_privacy_state") or {}
    return {
        "delete_requested": bool(state.get("delete_requested")),
    }


def _save_user_privacy_state(request, payload):
    request.session["user_privacy_state"] = payload
    request.session.modified = True


def _user_personal_info_state(request, user):
    state = request.session.get("user_personal_info_state") or {}
    default_name = _user_display_name(user)
    default_address = _format_customer_address(_get_default_customer_address(user))
    return {
        "full_name": state.get("full_name") or default_name,
        "national_id": state.get("national_id") or "",
        "address": state.get("address") or default_address,
    }


def _save_user_personal_info_state(request, payload):
    request.session["user_personal_info_state"] = payload
    request.session.modified = True


def _user_shell_context(request, *, section="account", subsection="", notification_section="", account_subsection="", page_title=""):
    profile = _get_customer_profile(request.user)
    display_name = _user_display_name(request.user)
    avatar_url = ""
    try:
        if profile.avatar and getattr(profile.avatar, "url", ""):
            avatar_url = profile.avatar.url
    except Exception:
        avatar_url = ""

    return {
        "page_title": page_title,
        "display_name": display_name,
        "avatar_url": avatar_url,
        "account_section": section,
        "account_subsection": subsection,
        "notification_section": notification_section,
        "account_profile_subsection": account_subsection,
        "cart_total_quantity": _cart_items(request)[1],
        "user_notifications": _user_header_notifications(request.user),
        "profile": profile,
    }


def _build_user_notification_feed(user):
    notifications = []
    orders = list(
        DonHang.objects.filter(khach_hang=user)
        .select_related("cua_hang_xu_ly")
        .prefetch_related("items__san_pham__hinh_anh_phu", "items__san_pham__thuong_hieu")
        .order_by("-created_at")
    )

    for order in orders:
        first_item = order.items.all().first()
        product = first_item.san_pham if first_item and first_item.san_pham_id else None
        thumb_url = ""
        if product:
            try:
                if product.hinh_anh:
                    thumb_url = product.hinh_anh.url
            except Exception:
                thumb_url = ""
            if not thumb_url:
                extra = product.hinh_anh_phu.all().first()
                if extra and extra.hinh_anh:
                    thumb_url = extra.hinh_anh.url

        order_status = _order_status_ui_text(order)
        notifications.append(
            {
                "category": "order",
                "title": order_status,
                "message": u("\u0110\u01a1n h\u00e0ng {order} v\u1edbi s\u1ea3n ph\u1ea9m {product} \u0111ang \u1edf tr\u1ea1ng th\u00e1i {status}.").format(
                    order=order.pk,
                    product=product.ten if product else u("trong \u0111\u01a1n"),
                    status=order_status.lower(),
                ),
                "preview": u("\u0110\u01a1n h\u00e0ng {order} hi\u1ec7n \u0111ang \u1edf tr\u1ea1ng th\u00e1i {status}.").format(
                    order=order.pk,
                    status=order_status.lower(),
                ),
                "thumbnail_url": thumb_url,
                "created_at": order.created_at,
                "created_text": timezone.localtime(order.created_at).strftime("%H:%M %d-%m-%Y"),
                "href": reverse("store:order_detail", args=[order.pk]),
                "action_label": u("Xem chi tiết"),
                "highlight": order.created_at >= timezone.now() - timedelta(days=2),
            }
        )

        if order.trang_thai in {"done", "delivered"}:
            notifications.append(
                {
                    "category": "wallet",
                    "title": u("Giao d\u1ecbch thanh to\u00e1n th\u00e0nh c\u00f4ng"),
                    "message": u("\u0110\u01a1n h\u00e0ng {order} \u0111\u00e3 ghi nh\u1eadn thanh to\u00e1n {amount} qua {method}.").format(
                        order=order.pk,
                        amount=order.display_total_amount if hasattr(order, "display_total_amount") else _format_currency(order.tong_tien),
                        method=order.get_phuong_thuc_thanh_toan_display().lower(),
                    ),
                    "preview": u("Thanh to\u00e1n \u0111\u01a1n {order} \u0111\u00e3 ho\u00e0n t\u1ea5t.").format(order=order.pk),
                    "thumbnail_url": thumb_url,
                    "created_at": order.created_at,
                    "created_text": timezone.localtime(order.created_at).strftime("%H:%M %d-%m-%Y"),
                    "href": reverse("store:order_detail", args=[order.pk]),
                    "action_label": u("Xem chi tiết"),
                    "highlight": False,
                }
            )

        if order.trang_thai == "done":
            notifications.append(
                {
                    "category": "shopee",
                    "title": u("\u0110\u01a1n h\u00e0ng \u0111\u00e3 ho\u00e0n t\u1ea5t"),
                    "message": u("\u0110\u01a1n h\u00e0ng {order} \u0111\u00e3 ho\u00e0n t\u1ea5t. H\u00e3y \u0111\u00e1nh gi\u00e1 c\u1eeda h\u00e0ng {store} \u0111\u1ec3 chia s\u1ebb tr\u1ea3i nghi\u1ec7m c\u1ee7a b\u1ea1n.").format(
                        order=order.pk,
                        store=order.cua_hang_xu_ly.ten if order.cua_hang_xu_ly_id else "",
                    ),
                    "preview": u("\u0110\u01a1n h\u00e0ng {order} \u0111\u00e3 ho\u00e0n t\u1ea5t.").format(order=order.pk),
                    "thumbnail_url": thumb_url,
                    "created_at": order.created_at,
                    "created_text": timezone.localtime(order.created_at).strftime("%H:%M %d-%m-%Y"),
                    "href": reverse("store:order_detail", args=[order.pk]),
                    "action_label": u("\u0110\u00e1nh gi\u00e1 s\u1ea3n ph\u1ea9m"),
                    "highlight": False,
                }
            )

    promotions = list(
        KhuyenMai.objects.filter(dang_ap_dung=True).order_by("-ngay_bat_dau", "-id")[:12]
    )
    for voucher in promotions:
        promo_thumb = ""
        related_brand = voucher.thuong_hieu.first()
        related_store = voucher.cua_hang.first()
        if related_brand:
            products = SanPham.objects.filter(thuong_hieu=related_brand).order_by("pk")
        elif related_store:
            stock = TonKhoCuaHang.objects.filter(cua_hang=related_store).select_related("san_pham").order_by("pk").first()
            products = SanPham.objects.filter(pk=stock.san_pham_id) if stock else SanPham.objects.none()
        else:
            products = SanPham.objects.order_by("pk")
        first_product = products.first()
        if first_product:
            try:
                if first_product.hinh_anh:
                    promo_thumb = first_product.hinh_anh.url
            except Exception:
                promo_thumb = ""
        notifications.append(
            {
                "category": "promotion",
                "title": voucher.ten,
                "message": voucher.mo_ta or u("\u01afu \u0111\u00e3i m\u00e3 {code} d\u00e0nh cho b\u1ea1n.").format(code=voucher.ma_code or "-"),
                "preview": voucher.mo_ta or u("M\u00e3 {code} \u0111ang s\u1eb5n s\u00e0ng s\u1eed d\u1ee5ng.").format(code=voucher.ma_code or "-"),
                "thumbnail_url": promo_thumb,
                "created_at": voucher.ngay_bat_dau or voucher.ngay_ket_thuc or timezone.now(),
                "created_text": timezone.localtime(voucher.ngay_bat_dau or voucher.ngay_ket_thuc or timezone.now()).strftime("%H:%M %d-%m-%Y"),
                "href": reverse("store:user_voucher_wallet"),
                "action_label": "Xem chi tiết",
                "highlight": True,
            }
        )

    recent_reviews = list(
        DanhGiaCuaHang.objects.filter(user=user).prefetch_related("tep_dinh_kem", "cua_hang").order_by("-created_at")[:6]
    )
    for review in recent_reviews:
        media = review.tep_dinh_kem.first()
        media_thumb = ""
        if media and media.loai == "image":
            try:
                media_thumb = media.tep.url
            except Exception:
                media_thumb = ""
        notifications.append(
            {
                "category": "shopee",
                "title": u("\u0110\u00e1nh gi\u00e1 m\u1edbi cho {store}").format(store=review.cua_hang.ten),
                "message": review.binh_luan or u("B\u1ea1n \u0111\u00e3 g\u1eedi {stars} sao cho c\u1eeda h\u00e0ng {store}.").format(stars=review.so_sao, store=review.cua_hang.ten),
                "preview": review.binh_luan or u("B\u1ea1n \u0111\u00e3 g\u1eedi {stars} sao.").format(stars=review.so_sao),
                "thumbnail_url": media_thumb,
                "created_at": review.created_at,
                "created_text": timezone.localtime(review.created_at).strftime("%H:%M %d-%m-%Y"),
                "href": f"{reverse('store:store_detail_page', args=[review.cua_hang_id])}#reviews",
                "action_label": u("Xem chi ti\u1ebft"),
                "highlight": review.created_at >= timezone.now() - timedelta(days=7),
            }
        )

    notifications.sort(key=lambda item: item["created_at"], reverse=True)
    for notification in notifications:
        for key in ("title", "message", "preview", "action_label"):
            if key in notification:
                notification[key] = _fix_text(notification[key])
    return notifications


def _order_status_timeline(order):
    created_at = order.created_at or timezone.now()
    raw_steps = [
        ("pending", "Đơn hàng đã đặt", created_at),
        ("confirmed", "Đã xác nhận", created_at + timedelta(hours=2)),
        ("shipping", "Đang giao", created_at + timedelta(hours=8)),
        ("delivered", "Đã giao hàng", created_at + timedelta(days=1)),
        ("done", "Hoàn tất", created_at + timedelta(days=2)),
    ]
    order_statuses = [item[0] for item in raw_steps]
    active_index = order_statuses.index(order.trang_thai) if order.trang_thai in order_statuses else -1

    timeline = []
    if order.trang_thai == "cancelled":
        for code, label, moment in raw_steps:
            timeline.append(
                {
                    "code": code,
                    "label": label,
                    "time": moment,
                    "state": "done" if code == "pending" else "pending",
                }
            )
        timeline.append(
            {
                "code": "cancelled",
                "label": "Đã hủy",
                "time": created_at + timedelta(hours=4),
                "state": "active",
            }
        )
        return timeline

    for index, (code, label, moment) in enumerate(raw_steps):
        if index < active_index:
            state = "done"
        elif index == active_index:
            state = "active"
        else:
            state = "pending"
        timeline.append(
            {
                "code": code,
                "label": label,
                "time": moment if state in {"done", "active"} else None,
                "state": state,
            }
        )
    return timeline


def _password_strength(password: str):
    password = password or ""
    score = 0
    if len(password) >= 8:
        score += 1
    if len(password) >= 12:
        score += 1
    if re.search(r"[A-Z]", password):
        score += 1
    if re.search(r"[a-z]", password):
        score += 1
    if re.search(r"\d", password):
        score += 1
    if re.search(r"[^A-Za-z0-9]", password):
        score += 1

    if score <= 3:
        return "weak"
    if score <= 4:
        return "medium"
    return "strong"


def _enforce_password_strength(form, pref):
    password = (
        form.data.get("new_password1")
        or form.data.get("password1")
        or ""
    )
    strength = _password_strength(password)
    if password and strength == "weak":
        target_field = "new_password1" if "new_password1" in form.fields else "password1"
        form.add_error(target_field, pref["t"]["password_too_weak"])
    return strength


def _require_admin_user(request):
    if not request.user.is_authenticated:
        return redirect("store:admin_login")
    if not request.user.is_active:
        logout(request)
        messages.error(request, "Tài khoản của bạn đã bị khóa. Vui lòng liên hệ quản trị hệ thống.")
        return redirect("store:admin_login")
    if _is_admin_user(request.user):
        return None
    return redirect("store:admin_login")


def _resolve_model(model_slug):
    # Swapped per admin requirement: order list <-> order detail pages.
    if model_slug == ORDER_MODULE_SLUG:
        return DonHang
    if model_slug == ORDER_ITEM_MODULE_SLUG:
        return ChiTietDonHang

    model = MODEL_REGISTRY.get(model_slug)
    if model is None:
        raise Http404("Không tìm thấy model.")
    return model


def _resolve_model_alias(model_slug):
    model = MODEL_REGISTRY.get(model_slug)
    if model is None:
        raise Http404("Không tìm thấy model.")
    return model


def _admin_pref_context(request):
    lang = request.session.get("admin_lang", "vi")
    if lang not in CMS_TRANSLATIONS:
        lang = "vi"
    theme = request.session.get("admin_theme", "light")
    if theme not in {"light", "dark"}:
        theme = "light"
    unread_count = Notification.objects.filter(resolved=False).count()
    return {
        "admin_lang": lang,
        "admin_theme": theme,
        "admin_unread_notifications": unread_count,
        "show_admin_link": _is_admin_user(request.user),
        "current_admin_role": _current_user_role(request.user),
        "current_admin_role_label": _role_label(_current_user_role(request.user)),
        "can_manage_settings": _has_admin_page_access(request.user, "settings"),
        "can_manage_users": _has_admin_page_access(request.user, "user_management"),
        "can_view_inventory_hub": _has_admin_page_access(request.user, "inventory_hub"),
        "can_view_trash": _has_admin_page_access(request.user, "trash"),
        "can_view_notifications": _has_admin_page_access(request.user, "notifications"),
        "t": _fix_text_dict(CMS_TRANSLATIONS[lang]),
    }

def _model_label(model_slug, lang, plural=True):
    labels = MODULE_LABELS.get(model_slug, {})
    if lang == "en":
        return _fix_text(labels.get("en_plural" if plural else "en_singular", model_slug))
    return _fix_text(labels.get("vi_plural" if plural else "vi_singular", model_slug))


def _inventory_hub_context():
    cutoff_30d = timezone.now() - timedelta(days=30)
    restock_target = 25
    stock_qs = (
        SanPham.objects.select_related("nhom_san_pham", "thuong_hieu").annotate(
            import_30d=dj_models.Sum(
                "giao_dich_kho__so_luong",
                filter=Q(giao_dich_kho__loai="import", giao_dich_kho__created_at__gte=cutoff_30d),
            ),
            export_30d=dj_models.Sum(
                "giao_dich_kho__so_luong",
                filter=Q(giao_dich_kho__loai="export", giao_dich_kho__created_at__gte=cutoff_30d),
            ),
        )
        .order_by("ten")
    )

    products = list(stock_qs)
    product_ids = [product.pk for product in products]
    store_stock_totals = {}
    if product_ids:
        store_stock_totals = {
            row["san_pham_id"]: int(row["total_stock"] or 0)
            for row in TonKhoCuaHang.objects.filter(san_pham_id__in=product_ids)
            .values("san_pham_id")
            .annotate(total_stock=Coalesce(dj_models.Sum("ton_kho"), 0))
        }
    for product in products:
        product.ton_kho = store_stock_totals.get(product.pk, 0)

    product_store_stats = _get_product_store_stats(product_ids)
    total_skus = len(products)
    total_units = sum(int(product.ton_kho or 0) for product in products)

    for product in products:
        store_stats = product_store_stats.get(product.pk, {})
        stores_with_stock_count = int(store_stats.get("stores_with_stock_count") or 0)
        tracked_store_count = int(store_stats.get("tracked_store_count") or 0)
        low_stock_store_count = int(store_stats.get("low_stock_store_count") or 0)
        empty_stock_store_count = int(store_stats.get("empty_stock_store_count") or 0)
        product.stores_with_stock_count = stores_with_stock_count
        product.tracked_store_count = tracked_store_count
        product.low_stock_store_count = low_stock_store_count
        product.empty_stock_store_count = empty_stock_store_count
        product.affected_store_count = low_stock_store_count + empty_stock_store_count
        product.avg_store_stock_display = (
            int(round((product.ton_kho or 0) / stores_with_stock_count))
            if stores_with_stock_count
            else 0
        )
        product.import_30d = int(product.import_30d or 0)
        product.export_30d = int(product.export_30d or 0)
        product.net_30d = product.import_30d - product.export_30d
        product.has_branch_shortage = product.affected_store_count > 0
        product.stock_label_display = SanPham.stock_label.fget(product)
        product.stock_hint_display = SanPham.stock_hint.fget(product)
        if product.empty_stock_store_count > 0 and (product.ton_kho or 0) > 0:
            product.stock_label_display = f"Thieu hang tai {product.empty_stock_store_count} cua hang"
        elif product.low_stock_store_count > 0 and (product.ton_kho or 0) > SanPham.LOW_STOCK_THRESHOLD:
            product.stock_label_display = f"Can bo sung tai {product.low_stock_store_count} cua hang"

    out_of_stock_count = sum(
        1
        for product in products
        if (product.ton_kho or 0) <= 0
        or (product.tracked_store_count > 0 and product.stores_with_stock_count <= 0)
    )
    low_stock_count = sum(
        1
        for product in products
        if (
            0 < (product.ton_kho or 0) <= SanPham.LOW_STOCK_THRESHOLD
            or product.has_branch_shortage
        )
        and not (
            (product.ton_kho or 0) <= 0
            or (product.tracked_store_count > 0 and product.stores_with_stock_count <= 0)
        )
    )
    overstock_count = sum(
        1
        for product in products
        if (product.ton_kho or 0) >= max(SanPham.LOW_STOCK_THRESHOLD * 4, 20)
    )

    import_suggestions = []
    shortage_rows = list(
        TonKhoCuaHang.objects.filter(ton_kho__lte=SanPham.LOW_STOCK_THRESHOLD)
        .select_related(
            "cua_hang",
            "cua_hang__chuoi",
            "san_pham",
            "san_pham__nhom_san_pham",
            "san_pham__thuong_hieu",
        )
        .order_by("ton_kho", "cua_hang__ten", "san_pham__ten")
    )
    product_lookup = {product.pk: product for product in products}
    for row in shortage_rows:
        product = product_lookup.get(row.san_pham_id)
        if product is None:
            continue
        suggestion = row
        suggestion.product = product
        suggestion.store_display = row.cua_hang.ten
        suggestion.chain_display = row.cua_hang.chuoi.ten if row.cua_hang and row.cua_hang.chuoi_id else "-"
        suggestion.current_stock = int(row.ton_kho or 0)
        suggestion.recommended_restock = max(restock_target - suggestion.current_stock, 0)
        suggestion.product_total_stock = int(product.ton_kho or 0)
        suggestion.product_avg_store_stock_display = product.avg_store_stock_display
        suggestion.product_export_30d = int(product.export_30d or 0)
        suggestion.product_import_30d = int(product.import_30d or 0)
        suggestion.status_label = "Hết hàng" if suggestion.current_stock <= 0 else f"Sắp hết ({suggestion.current_stock})"
        import_suggestions.append(suggestion)

    import_suggestions = sorted(
        import_suggestions,
        key=lambda item: (
            item.current_stock,
            -(item.product_export_30d or 0),
            -item.recommended_restock,
            item.store_display.lower(),
            item.product.ten.lower(),
        ),
    )[:8]

    export_suggestions = sorted(
        [
            product
            for product in products
            if (product.ton_kho or 0) >= max(SanPham.LOW_STOCK_THRESHOLD * 4, 20)
            or (
                (product.ton_kho or 0) > SanPham.LOW_STOCK_THRESHOLD
                and (product.import_30d or 0) > (product.export_30d or 0)
            )
        ],
        key=lambda item: (
            -max((item.ton_kho or 0) - max(item.export_30d or 0, SanPham.LOW_STOCK_THRESHOLD), 0),
            item.export_30d or 0,
            -max((item.import_30d or 0) - (item.export_30d or 0), 0),
            item.ten.lower(),
        ),
    )[:8]

    movement_totals = GiaoDichKho.objects.aggregate(
        import_30d=Coalesce(
            dj_models.Sum("so_luong", filter=Q(loai="import", created_at__gte=cutoff_30d)),
            0,
        ),
        export_30d=Coalesce(
            dj_models.Sum("so_luong", filter=Q(loai="export", created_at__gte=cutoff_30d)),
            0,
        ),
    )

    recent_movements = list(
        GiaoDichKho.objects.select_related("san_pham", "nhan_vien", "cua_hang")
        .order_by("-created_at", "-id")[:10]
    )

    store_stock_rows = list(
        CuaHang.objects.select_related("chuoi").annotate(
            total_units=Coalesce(dj_models.Sum("ton_kho_san_pham__ton_kho"), 0),
            sku_count=Coalesce(
                dj_models.Count(
                    "ton_kho_san_pham",
                    filter=Q(ton_kho_san_pham__ton_kho__gt=0),
                    distinct=True,
                ),
                0,
            ),
            low_stock_count=Coalesce(
                dj_models.Count(
                    "ton_kho_san_pham",
                    filter=Q(
                        ton_kho_san_pham__ton_kho__gt=0,
                        ton_kho_san_pham__ton_kho__lte=SanPham.LOW_STOCK_THRESHOLD,
                    ),
                    distinct=True,
                ),
                0,
            ),
            empty_stock_count=Coalesce(
                dj_models.Count(
                    "ton_kho_san_pham",
                    filter=Q(ton_kho_san_pham__ton_kho__lte=0),
                    distinct=True,
                ),
                0,
            ),
        ).order_by("-total_units", "ten")[:8]
    )

    return {
        "inventory_stats": {
            "total_skus": total_skus,
            "total_units": total_units,
            "out_of_stock_count": out_of_stock_count,
            "low_stock_count": low_stock_count,
            "overstock_count": overstock_count,
            "import_30d": int(movement_totals["import_30d"] or 0),
            "export_30d": int(movement_totals["export_30d"] or 0),
            "restock_target": restock_target,
        },
        "import_suggestions": import_suggestions,
        "export_suggestions": export_suggestions,
        "recent_stock_movements": recent_movements,
        "store_stock_rows": store_stock_rows,
    }


def _get_product_store_stats(product_ids=None):
    stock_rows = TonKhoCuaHang.objects.all()
    if product_ids is not None:
        stock_rows = stock_rows.filter(san_pham_id__in=product_ids)
    return {
        row["san_pham_id"]: row
        for row in stock_rows.values("san_pham_id").annotate(
            tracked_store_count=Coalesce(
                dj_models.Count("cua_hang", distinct=True),
                0,
            ),
            stores_with_stock_count=Coalesce(
                dj_models.Count(
                    "cua_hang",
                    filter=Q(ton_kho__gt=0),
                    distinct=True,
                ),
                0,
            ),
            low_stock_store_count=Coalesce(
                dj_models.Count(
                    "cua_hang",
                    filter=Q(
                        ton_kho__gt=0,
                        ton_kho__lte=SanPham.LOW_STOCK_THRESHOLD,
                    ),
                    distinct=True,
                ),
                0,
            ),
            empty_stock_store_count=Coalesce(
                dj_models.Count(
                    "cua_hang",
                    filter=Q(ton_kho__lte=0),
                    distinct=True,
                ),
                0,
            ),
        )
    }


def _dashboard_context():
    today = timezone.localdate()
    tz = timezone.get_current_timezone()

    def _day_bounds(day):
        start = timezone.make_aware(datetime.combine(day, time.min), tz)
        end = start + timedelta(days=1)
        return start, end

    today_start, tomorrow_start = _day_bounds(today)
    paid_statuses = {"paid"}
    zero_money = dj_models.Value(0, output_field=dj_models.DecimalField(max_digits=12, decimal_places=0))

    order_qs = DonHang.objects.select_related("khach_hang", "cua_hang_xu_ly", "khuyen_mai")
    total_orders = order_qs.count()
    today_orders = order_qs.filter(created_at__gte=today_start, created_at__lt=tomorrow_start).count()
    pending_orders = order_qs.filter(trang_thai="pending").count()
    awaiting_transfer_orders = order_qs.filter(
        phuong_thuc_thanh_toan="bank_transfer",
        trang_thai_thanh_toan="awaiting_confirmation",
    ).count()
    paid_revenue = order_qs.filter(trang_thai_thanh_toan__in=paid_statuses).aggregate(
        total=Coalesce(dj_models.Sum("tong_tien"), zero_money)
    )["total"]
    today_revenue = order_qs.filter(
        created_at__gte=today_start,
        created_at__lt=tomorrow_start,
        trang_thai_thanh_toan__in=paid_statuses,
    ).aggregate(total=Coalesce(dj_models.Sum("tong_tien"), zero_money))["total"]

    product_qs = SanPham.objects.all().order_by("id")
    products = list(product_qs)
    product_count = len(products)
    product_ids = [product.pk for product in products]
    store_stock_totals = {}
    if product_ids:
        store_stock_totals = {
            row["san_pham_id"]: int(row["total_stock"] or 0)
            for row in TonKhoCuaHang.objects.filter(san_pham_id__in=product_ids)
            .values("san_pham_id")
            .annotate(total_stock=Coalesce(dj_models.Sum("ton_kho"), 0))
        }
    product_store_stats = _get_product_store_stats(product_ids)

    low_stock_count = 0
    out_stock_count = 0
    for product in products:
        total_stock = store_stock_totals.get(product.pk, int(product.ton_kho or 0))
        store_stats = product_store_stats.get(product.pk, {})
        tracked_store_count = int(store_stats.get("tracked_store_count") or 0)
        stores_with_stock_count = int(store_stats.get("stores_with_stock_count") or 0)
        low_stock_store_count = int(store_stats.get("low_stock_store_count") or 0)
        empty_stock_store_count = int(store_stats.get("empty_stock_store_count") or 0)
        has_branch_shortage = (low_stock_store_count + empty_stock_store_count) > 0
        is_out_of_stock = total_stock <= 0 or (
            tracked_store_count > 0 and stores_with_stock_count <= 0
        )
        is_low_stock = (
            (0 < total_stock <= SanPham.LOW_STOCK_THRESHOLD) or has_branch_shortage
        ) and not is_out_of_stock
        if is_out_of_stock:
            out_stock_count += 1
        elif is_low_stock:
            low_stock_count += 1

    recent_orders = list(order_qs.order_by("-created_at")[:8])
    for order in recent_orders:
        order.display_total_amount = _format_currency(order.tong_tien)

    payment_mix = []
    payment_rows = (
        order_qs.values("phuong_thuc_thanh_toan")
        .annotate(total=dj_models.Count("id"))
        .order_by("-total")
    )
    method_labels = dict(DonHang.PAYMENT_METHOD_CHOICES)
    payment_colors = ["#0f766e", "#f97316", "#2563eb", "#7c3aed", "#ea580c", "#0891b2"]
    for row in payment_rows:
        payment_mix.append(
            {
                "label": method_labels.get(row["phuong_thuc_thanh_toan"], row["phuong_thuc_thanh_toan"]),
                "value": row["total"],
            }
        )
    payment_total = sum(int(item["value"] or 0) for item in payment_mix)
    payment_conic_segments = []
    payment_cumulative = Decimal("0")
    for index, item in enumerate(payment_mix):
        item["color"] = payment_colors[index % len(payment_colors)]
        if payment_total > 0:
            item["percent"] = round((Decimal(item["value"]) / Decimal(payment_total)) * Decimal("100"), 2)
        else:
            item["percent"] = Decimal("0")
        start = payment_cumulative
        payment_cumulative += Decimal(item["percent"])
        payment_conic_segments.append(f"{item['color']} {start}% {payment_cumulative}%")
    payment_conic_gradient = (
        f"conic-gradient({', '.join(payment_conic_segments)})"
        if payment_conic_segments
        else "conic-gradient(#e2e8f0 0% 100%)"
    )

    seven_day_series = []
    revenue_points = []
    order_points = []
    max_revenue = Decimal("0")
    max_orders = 0
    for offset in range(6, -1, -1):
        day = today - timedelta(days=offset)
        day_start, day_end = _day_bounds(day)
        day_orders = order_qs.filter(created_at__gte=day_start, created_at__lt=day_end)
        order_count = day_orders.count()
        day_revenue = day_orders.filter(trang_thai_thanh_toan__in=paid_statuses).aggregate(
            total=Coalesce(dj_models.Sum("tong_tien"), zero_money)
        )["total"]
        if day_revenue > max_revenue:
            max_revenue = day_revenue
        if order_count > max_orders:
            max_orders = order_count
        seven_day_series.append(
            {
                "label": day.strftime("%d/%m"),
                "day_name": day.strftime("%a"),
                "order_count": order_count,
                "revenue": day_revenue,
                "display_revenue": _format_currency(day_revenue),
            }
        )

    max_revenue = max_revenue or Decimal("1")
    max_orders = max_orders or 1
    chart_left = Decimal("14")
    chart_top = Decimal("12")
    chart_right = Decimal("88")
    chart_width = chart_right - chart_left
    chart_height = Decimal("74")
    chart_bottom = Decimal("92")
    revenue_line_points = []
    order_line_points = []
    chart_step = chart_width / Decimal(max(len(seven_day_series) - 1, 1))
    for index, item in enumerate(seven_day_series):
        revenue_percent = float((Decimal(item["revenue"]) / Decimal(max_revenue)) * Decimal("100"))
        order_percent = (int(item["order_count"]) / max_orders) * 100
        item["revenue_percent"] = max(8, round(revenue_percent, 2)) if item["revenue"] else 8
        item["order_percent"] = max(8, round(order_percent, 2)) if item["order_count"] else 8
        revenue_points.append(str(round(item["revenue_percent"], 2)))
        order_points.append(str(round(item["order_percent"], 2)))
        revenue_ratio = Decimal(item["revenue"]) / Decimal(max_revenue) if max_revenue else Decimal("0")
        order_ratio = Decimal(item["order_count"]) / Decimal(max_orders) if max_orders else Decimal("0")
        chart_x = chart_left + (chart_step * Decimal(index))
        revenue_y = chart_bottom - (revenue_ratio * chart_height)
        order_y = chart_bottom - (order_ratio * chart_height)
        item["chart_x"] = round(float(chart_x), 2)
        item["bar_x"] = round(float(chart_x - Decimal("3.8")), 2)
        item["bar_y"] = round(float(revenue_y), 2)
        item["bar_height"] = round(float(chart_bottom - revenue_y), 2)
        item["revenue_chart_y"] = round(float(revenue_y), 2)
        item["order_chart_y"] = round(float(order_y), 2)
        item["order_badge_x"] = round(float(chart_x - Decimal("4")), 2)
        item["order_badge_y"] = round(float(order_y - Decimal("9")), 2)
        item["order_badge_text_y"] = round(float(order_y - Decimal("5.8")), 2)
        revenue_line_points.append(f"{item['chart_x']},{item['revenue_chart_y']}")
        order_line_points.append(f"{item['chart_x']},{item['order_chart_y']}")
    revenue_axis_ticks = []
    for y_value, ratio in (
        (chart_top, Decimal("1")),
        (Decimal("37"), Decimal("0.6667")),
        (Decimal("62"), Decimal("0.3333")),
        (chart_bottom, Decimal("0")),
    ):
        revenue_axis_ticks.append(
            {
                "y": round(float(y_value), 2),
                "label": _format_currency((max_revenue * ratio).quantize(Decimal("1"), rounding=ROUND_HALF_UP)),
            }
        )
    order_axis_ticks = []
    for y_value, value in (
        (chart_top, max_orders),
        (Decimal("52"), max(1, math.ceil(max_orders / 2))),
        (chart_bottom, 0),
    ):
        order_axis_ticks.append({"y": round(float(y_value), 2), "label": value})

    store_leaderboard = list(
        CuaHang.objects.select_related("chuoi").annotate(
            total_orders=Coalesce(dj_models.Count("don_hang_xu_ly", distinct=True), 0),
            total_revenue=Coalesce(
                dj_models.Sum(
                    "don_hang_xu_ly__tong_tien",
                    filter=Q(don_hang_xu_ly__trang_thai_thanh_toan="paid"),
                ),
                zero_money,
            ),
            total_units=Coalesce(dj_models.Sum("ton_kho_san_pham__ton_kho"), 0),
        ).order_by("-total_orders", "-total_revenue", "ten")[:8]
    )
    for store in store_leaderboard:
        store.display_total_revenue = _format_currency(store.total_revenue)

    return {
        "dashboard_stats": {
            "total_orders": total_orders,
            "today_orders": today_orders,
            "pending_orders": pending_orders,
            "awaiting_transfer_orders": awaiting_transfer_orders,
            "paid_revenue": _format_currency(paid_revenue),
            "today_revenue": _format_currency(today_revenue),
            "product_count": product_count,
            "low_stock_count": low_stock_count,
            "out_stock_count": out_stock_count,
        },
        "recent_orders_dashboard": recent_orders,
        "payment_mix": payment_mix,
        "store_leaderboard": store_leaderboard,
        "seven_day_series": seven_day_series,
        "dashboard_chart_meta": {
            "max_revenue": _format_currency(max_revenue),
            "max_orders": max_orders,
            "revenue_points": ",".join(revenue_points),
            "order_points": ",".join(order_points),
            "revenue_line_points": " ".join(revenue_line_points),
            "order_line_points": " ".join(order_line_points),
            "payment_total": payment_total,
            "payment_conic_gradient": payment_conic_gradient,
            "chart_left": round(float(chart_left), 2),
            "chart_right": round(float(chart_right), 2),
            "chart_top": round(float(chart_top), 2),
            "chart_bottom": round(float(chart_bottom), 2),
            "revenue_axis_ticks": revenue_axis_ticks,
            "order_axis_ticks": order_axis_ticks,
        },
    }


def admin_dashboard_export_revenue(request):
    unauthorized = _require_admin_permission(request, "dashboard")
    if unauthorized:
        return unauthorized

    context = _dashboard_context()
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    filename = f"dashboard-doanh-thu-{timezone.localdate().strftime('%Y%m%d')}.csv"
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    writer = csv.writer(response)
    writer.writerow(["Ngay", "So don moi", "Doanh thu da thanh toan"])
    for item in context["seven_day_series"]:
        writer.writerow([item["label"], item["order_count"], str(item["revenue"])])
    return response


def _select_fulfillment_store(items):
    if not items:
        return None

    product_ids = sorted({item["product"].pk for item in items if item.get("product")})
    if not product_ids:
        return None

    rows = (
        TonKhoCuaHang.objects.filter(san_pham_id__in=product_ids)
        .select_related("cua_hang")
        .order_by("cua_hang__ten", "san_pham__ten")
    )
    store_map = {}
    for row in rows:
        store_bucket = store_map.setdefault(
            row.cua_hang_id,
            {"store": row.cua_hang, "stock": {}},
        )
        store_bucket["stock"][row.san_pham_id] = int(row.ton_kho or 0)

    candidates = []
    for data in store_map.values():
        if all(data["stock"].get(item["product"].pk, 0) >= int(item["quantity"]) for item in items):
            score = sum(data["stock"].get(item["product"].pk, 0) for item in items)
            candidates.append((score, data["store"].ten.lower(), data["store"]))

    if not candidates:
        return None

    candidates.sort(key=lambda item: (-item[0], item[1]))
    return candidates[0][2]


def _admin_redirect_with_preserved_query(request, model_slug=ORDER_MODULE_SLUG):
    redirect_url = reverse("store:admin_list", kwargs={"model_slug": model_slug})
    query = (request.POST.get("return_query") or request.GET.urlencode() or "").strip("&?")
    if query:
        redirect_url = f"{redirect_url}?{query}"
    return redirect(redirect_url)


def _release_order_inventory_if_needed(order, *, reason=""):
    if order is None or order.trang_thai_thanh_toan == "paid":
        return False

    movements = list(
        GiaoDichKho.objects.filter(don_hang=order, loai="export")
        .select_related("san_pham")
        .order_by("-created_at", "-id")
    )
    if not movements:
        return False

    for movement in movements:
        product_name = movement.san_pham.ten if movement.san_pham_id else f"SP #{movement.pk}"
        try:
            movement.delete()
        except ValidationError:
            _create_admin_notification(
                f"Không thể hoàn tồn kho đơn #{order.pk}",
                (
                    f"Không thể xóa giao dịch kho cho {product_name} vì có ràng buộc tồn kho. "
                    "Vui lòng kiểm tra lại chuỗi giao dịch kho."
                ),
                level="error",
                path=reverse("store:admin_list", kwargs={"model_slug": "giao-dich-kho"}),
                method="PATCH",
                status_code=409,
            )
            return False
        else:
            _create_admin_notification(
                f"Hoàn tồn kho cho đơn #{order.pk}",
                (
                    f"Đã hoàn {movement.so_luong} sản phẩm của {product_name} "
                    f"về kho do {reason or 'đơn chưa thanh toán bị hủy'}."
                ),
                level="warning",
                path=reverse("store:admin_list", kwargs={"model_slug": "giao-dich-kho"}),
                method="PATCH",
                status_code=200,
            )
    return True


def _log_payment_confirmation(order, action, *, performed_by=None, note=""):
    if order is None:
        return None
    return XacNhanThanhToan.objects.create(
        don_hang=order,
        hanh_dong=action,
        ghi_chu=note or "",
        performed_by=performed_by if getattr(performed_by, "is_authenticated", False) else None,
    )


def _field_label(field, lang):
    if lang != "en":
        return field.verbose_name
    return FIELD_LABELS.get("en", {}).get(field.name, field.verbose_name)


def _menu_context(lang="vi", user=None):
    menu = []
    for slug, model in MODEL_REGISTRY.items():
        if user is not None and not _has_module_access(user, slug, "view"):
            continue
        section_key = MENU_SECTION_MAP.get(slug, "operations")
        menu.append(
            {
                "slug": slug,
                "name": _model_label(slug, lang, plural=True),
                "count": model.objects.count(),
                "section_key": section_key,
                "section_label": _fix_text(MENU_SECTION_LABELS.get(lang, MENU_SECTION_LABELS["vi"]).get(section_key, "Khác")),
                "sort_order": MENU_ITEM_ORDER.get(slug, 999),
                "section_order": MENU_SECTION_ORDER.index(section_key) if section_key in MENU_SECTION_ORDER else 999,
            }
        )
    menu.sort(key=lambda item: (item["section_order"], item["sort_order"], item["name"]))
    return menu


def _build_file_preview_context(model, obj=None):
    previews = {}
    image_exts = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".svg", ".jfif"}
    for field in model._meta.fields:
        if field.get_internal_type() not in {"ImageField", "FileField"}:
            continue
        is_image_field = field.get_internal_type() == "ImageField"
        if obj is None:
            previews[field.name] = {"url": "", "is_image": is_image_field}
            continue
        value = getattr(obj, field.name, None)
        if value:
            is_image = is_image_field
            if not is_image:
                try:
                    ext = os.path.splitext(str(value.name))[1].lower()
                    is_image = ext in image_exts
                except Exception:
                    is_image = False
            try:
                previews[field.name] = {"url": value.url, "is_image": is_image}
            except Exception:
                previews[field.name] = {"url": "", "is_image": is_image}
        else:
            previews[field.name] = {"url": "", "is_image": is_image_field}
    return previews


def _build_review_media_context(review):
    if not review or not getattr(review, "pk", None):
        return []
    items = []
    for media in review.tep_dinh_kem.all().order_by("created_at", "id"):
        url = ""
        try:
            url = media.tep.url if media.tep else ""
        except Exception:
            url = ""
        if not url:
            continue
        items.append(
            {
                "id": media.pk,
                "url": url,
                "kind": media.loai,
                "name": os.path.basename(getattr(media.tep, "name", "") or ""),
                "created_at": media.created_at,
            }
        )
    return items


def _build_product_image_preview_context(obj=None):
    previews = {
        "product_images": {"url": "", "is_image": True},
        "gallery_items": [],
    }
    if obj is None:
        return previews

    try:
        if obj.hinh_anh:
            previews["product_images"]["url"] = obj.hinh_anh.url
    except Exception:
        pass

    related_images = list(obj.hinh_anh_phu.all().order_by("thu_tu", "id"))
    previews["gallery_items"] = [
        {
            "id": image.pk,
            "url": image.hinh_anh.url,
            "caption": image.chu_thich or f"Ảnh phụ {index}",
            "order": index,
        }
        for index, image in enumerate(related_images, start=1)
        if getattr(image, "hinh_anh", None)
    ]
    return previews


def _save_product_gallery(product, files, post_data=None):
    uploaded_images = list(files.getlist("product_images"))
    post_data = post_data or {}
    post_values = post_data.getlist if hasattr(post_data, "getlist") else lambda key: []

    if uploaded_images and not product.hinh_anh:
        product.hinh_anh = uploaded_images.pop(0)
        product.save(update_fields=["hinh_anh"])

    delete_ids = {value for value in post_values("delete_image_ids") if str(value).isdigit()}
    if delete_ids:
        product.hinh_anh_phu.filter(pk__in=delete_ids).delete()

    related_images = list(product.hinh_anh_phu.all().order_by("thu_tu", "id"))

    order_map = {}
    for image in related_images:
        raw_order = (post_data.get(f"image_order_{image.pk}") or "").strip()
        if raw_order.isdigit():
            order_map[image.pk] = int(raw_order)
    if order_map:
        related_images.sort(key=lambda item: (order_map.get(item.pk, item.thu_tu or 9999), item.thu_tu, item.pk))
        for index, image in enumerate(related_images, start=1):
            if image.thu_tu != index:
                image.thu_tu = index
                image.save(update_fields=["thu_tu"])

    if uploaded_images:
        current_order = (
            product.hinh_anh_phu.aggregate(max_order=dj_models.Max("thu_tu")).get("max_order") or 0
        )
        for uploaded in uploaded_images:
            current_order += 1
            HinhAnhSanPham.objects.create(
                san_pham=product,
                hinh_anh=uploaded,
                thu_tu=current_order,
                chu_thich=f"Ảnh phụ {current_order}",
            )

    normalized_images = list(product.hinh_anh_phu.all().order_by("thu_tu", "id"))
    for index, image in enumerate(normalized_images, start=1):
        if image.thu_tu != index:
            image.thu_tu = index
            image.save(update_fields=["thu_tu"])


def _build_product_card_gallery(product):
    images = []
    if product.hinh_anh:
        try:
            images.append(product.hinh_anh.url)
        except Exception:
            pass

    for image in product.hinh_anh_phu.all():
        try:
            if image.hinh_anh:
                images.append(image.hinh_anh.url)
        except Exception:
            continue

    if not images:
        images.append("https://www.circlek.com/sites/default/files/2024-03/our_products_920x575.jpg")
    return images[:8]


def _attach_stock_ui_fields(product):
    product.catalog_stock_label = SanPham.stock_label.fget(product)
    product.catalog_stock_hint = SanPham.stock_hint.fget(product)
    product.stock_css = {
        "out": "out-stock",
        "low": "low-stock",
        "ok": "in-stock",
    }.get(product.stock_level, "in-stock")
    return product


def _admin_form_class_for_model(model_slug, model):
    if model_slug == "san-pham":
        return SanPhamAdminForm
    if model_slug == "giao-dich-kho":
        return GiaoDichKhoAdminForm
    if model_slug == "khuyen-mai":
        return KhuyenMaiAdminForm
    return modelform_factory(model, fields="__all__")


def _apply_giao_dich_kho_hidden_fields(form):
    hidden_names = {
        "signed_at",
        "signed_by",
        "signed_ip",
        "signed_user_agent",
        "otp_code_hash",
        "otp_expires_at",
        "otp_verified_at",
        "otp_verified_by",
        "otp_verified_ip",
        "otp_verified_user_agent",
        "otp_recipient_email",
        "ton_truoc",
        "ton_sau",
        "created_at",
    }
    for name in hidden_names:
        if name in form.fields:
            form.fields.pop(name, None)
    return form


def _log_stock_audit(request, movement, action: str, reason: str = ""):
    if movement is None:
        return None
    return TonKhoAudit.objects.create(
        giao_dich=movement if movement.pk else None,
        san_pham=movement.san_pham,
        cua_hang=movement.cua_hang,
        loai=movement.loai,
        so_luong=movement.so_luong or 0,
        ton_truoc=movement.ton_truoc if movement.ton_truoc is not None else 0,
        ton_sau=movement.ton_sau if movement.ton_sau is not None else 0,
        hanh_dong=action,
        ly_do=(reason or "").strip(),
        created_by=request.user if getattr(request, "user", None) and request.user.is_authenticated else None,
    )


def _sanitize_admin_form(form):
    # Remove Django's default "---------" empty option labels for select fields.
    for field in form.fields.values():
        if hasattr(field, "empty_label") and field.empty_label == "---------":
            field.empty_label = ""
        try:
            choices = list(getattr(field, "choices", []))
            if choices and choices[0][1] == "---------":
                choices[0] = (choices[0][0], "")
                field.choices = choices
        except Exception:
            pass
    return form


def _validate_coord_from_map(request, form, instance=None):
    if not form.is_valid():
        return False

    source = (request.POST.get("_coord_from_map") or "").strip()
    lat = form.cleaned_data.get("vi_do")
    lon = form.cleaned_data.get("kinh_do")

    changed = not bool(instance and instance.pk)
    if instance and instance.pk and lat is not None and lon is not None:
        try:
            old_lat = float(instance.vi_do)
            old_lon = float(instance.kinh_do)
            changed = abs(float(lat) - old_lat) > 1e-12 or abs(float(lon) - old_lon) > 1e-12
        except Exception:
            changed = True

    if changed and source != "map":
        pref = _admin_pref_context(request)
        msg = pref["t"]["coord_required_from_map"]
        form.add_error("vi_do", msg)
        form.add_error("kinh_do", msg)
        return False
    return True


@method_decorator(never_cache, name="dispatch")
class AdminLoginView(LoginView):
    template_name = "user/login.html"
    authentication_form = AuthenticationForm
    redirect_authenticated_user = False

    def dispatch(self, request, *args, **kwargs):
        if _is_admin_user(request.user):
            return redirect("store:admin_dashboard")
        if _is_regular_user(request.user):
            next_url = request.GET.get("next")
            if next_url:
                return redirect(next_url)
            return redirect("store:user_dashboard")
        if request.user.is_authenticated:
            logout(request)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        user = self.request.user
        if _is_admin_user(user):
            return reverse("store:admin_dashboard")
        resumed_url = _resume_post_login_cart_action(self.request)
        if resumed_url:
            return resumed_url
        next_url = self.request.POST.get("next") or self.request.GET.get("next")
        if next_url:
            return next_url
        return reverse("store:user_dashboard")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pref = _admin_pref_context(self.request)
        context.update(pref)
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        _ensure_user_role(self.request.user)
        return response


@method_decorator(never_cache, name="dispatch")
class UserLoginView(LoginView):
    template_name = "user/login.html"
    authentication_form = AuthenticationForm
    redirect_authenticated_user = False

    def dispatch(self, request, *args, **kwargs):
        if _is_admin_user(request.user) and not request.GET.get("next"):
            return redirect("store:admin_dashboard")
        if _is_regular_user(request.user):
            next_url = request.GET.get("next")
            if next_url:
                return redirect(next_url)
            return redirect("store:user_dashboard")
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        user = self.request.user
        if _is_admin_user(user):
            return reverse("store:admin_dashboard")
        resumed_url = _resume_post_login_cart_action(self.request)
        if resumed_url:
            return resumed_url
        next_url = self.request.POST.get("next") or self.request.GET.get("next")
        if next_url:
            return next_url
        return reverse("store:user_dashboard")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pref = _admin_pref_context(self.request)
        context.update(pref)
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        _ensure_user_role(self.request.user)
        return response


_password_reset_token = PasswordResetTokenGenerator()


def _clear_password_reset_session(request):
    request.session.pop("password_reset_pending", None)
    request.session.pop("password_reset_otp", None)
    request.session.pop("password_reset_verified", None)
    request.session.modified = True


def _issue_password_reset_otp(request, *, user):
    allow, rate_error = _check_otp_rate_limit(request, key=f"reset:{user.email}")
    if not allow:
        request.session["password_reset_otp_error"] = rate_error
        request.session.modified = True
        return None

    otp_code = _generate_register_otp()
    expires_at = timezone.now() + timedelta(minutes=5)
    request.session["password_reset_otp"] = {
        "code": otp_code,
        "expires_at": expires_at.timestamp(),
    }
    request.session.modified = True

    expires_text = timezone.localtime(expires_at).strftime("%H:%M %d/%m/%Y")
    subject = "Mã OTP đặt lại mật khẩu"
    message = (
        f"Xin chào {user.get_full_name() or user.username},\n\n"
        f"Mã OTP đặt lại mật khẩu của bạn là: {otp_code}\n"
        f"Mã có hiệu lực đến {expires_text}.\n\n"
        "Nếu bạn không yêu cầu đặt lại mật khẩu, hãy bỏ qua email này."
    )
    html_message = _otp_email_html(
        title="Đặt lại mật khẩu",
        subtitle="Bạn vừa yêu cầu đặt lại mật khẩu. Dùng mã OTP bên dưới để xác nhận.",
        otp_code=otp_code,
        expires_text=expires_text,
    )
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
            html_message=html_message,
        )
    except Exception as exc:
        request.session["password_reset_otp_error"] = str(exc)
        request.session.modified = True
        return None
    _record_otp_sent(request, key=f"reset:{user.email}")
    return otp_code


def user_password_reset_request(request):
    pref = _admin_pref_context(request)
    email_value = ""
    info_message = ""
    errors = []
    otp_required = False
    otp_verified = False
    form = None

    if request.user.is_authenticated and _is_regular_user(request.user):
        return redirect("store:user_dashboard")

    if request.method == "POST":
        action = (request.POST.get("action") or "").strip()
        if action == "reset_flow":
            _clear_password_reset_session(request)
            return redirect("store:user_password_reset")

        pending = request.session.get("password_reset_pending") or {}
        otp_state = request.session.get("password_reset_otp") or {}
        otp_verified = bool(request.session.get("password_reset_verified"))

        if action == "send_otp":
            email_value = (request.POST.get("email") or "").strip()
            try:
                validate_email(email_value)
            except ValidationError:
                errors.append("Email không đúng định dạng.")

            if not errors:
                _clear_password_reset_session(request)
                user = User.objects.filter(email__iexact=email_value).first()
                if user:
                    request.session["password_reset_pending"] = {
                        "email": user.email,
                        "user_id": user.pk,
                    }
                    request.session.modified = True
                    otp_sent = _issue_password_reset_otp(request, user=user)
                    if otp_sent:
                        info_message = "Đã gửi OTP đến email. Vui lòng kiểm tra hộp thư."
                    else:
                        error_text = request.session.pop("password_reset_otp_error", "")
                        errors.append("Không gửi được OTP. Vui lòng thử lại sau.")
                        if error_text:
                            errors.append(error_text)
                else:
                    info_message = "Nếu email tồn tại, hệ thống đã gửi OTP đặt lại mật khẩu."

        elif action == "resend_otp":
            if pending.get("user_id"):
                request.session.pop("password_reset_verified", None)
                request.session.modified = True
                user = User.objects.filter(pk=pending.get("user_id")).first()
                if user:
                    otp_sent = _issue_password_reset_otp(request, user=user)
                    if otp_sent:
                        info_message = "Đã gửi lại OTP. Vui lòng kiểm tra email."
                    else:
                        error_text = request.session.pop("password_reset_otp_error", "")
                        errors.append("Không gửi được OTP. Vui lòng thử lại sau.")
                        if error_text:
                            errors.append(error_text)
                else:
                    errors.append("Không tìm thấy tài khoản để gửi OTP.")
            else:
                errors.append("Vui lòng gửi OTP trước.")

        elif action == "verify_otp":
            otp_input = (request.POST.get("otp") or "").strip()
            if not otp_input:
                errors.append("Vui lòng nhập mã OTP.")
            elif not pending or not otp_state:
                errors.append("Vui lòng gửi OTP trước.")
            else:
                expires_at = otp_state.get("expires_at")
                if not expires_at or timezone.now().timestamp() > float(expires_at):
                    errors.append("OTP đã hết hạn. Vui lòng gửi lại OTP.")
                elif otp_input != str(otp_state.get("code", "")):
                    errors.append("OTP không đúng. Vui lòng thử lại.")
                else:
                    request.session["password_reset_verified"] = True
                    request.session.modified = True
                    info_message = "OTP hợp lệ. Vui lòng đặt mật khẩu mới."

        elif action == "set_password":
            if not otp_verified or not pending.get("user_id"):
                errors.append("Vui lòng xác nhận OTP trước khi đặt mật khẩu.")
            else:
                user = User.objects.filter(pk=pending.get("user_id")).first()
                if not user:
                    errors.append("Không tìm thấy tài khoản để đặt lại mật khẩu.")
                else:
                    form = SetPasswordForm(user=user, data=request.POST or None)
                    _enforce_password_strength(form, pref)
                    if form.is_valid():
                        form.save()
                        _clear_password_reset_session(request)
                        messages.success(request, "Đã đặt lại mật khẩu. Bạn có thể đăng nhập lại.")
                        return redirect("store:user_login")
        else:
            email_value = (request.POST.get("email") or "").strip()

    pending = request.session.get("password_reset_pending") or {}
    otp_required = bool(pending)
    otp_verified = bool(request.session.get("password_reset_verified"))
    if pending:
        email_value = pending.get("email", email_value)

    if otp_verified and pending.get("user_id"):
        user = User.objects.filter(pk=pending.get("user_id")).first()
        if user and form is None:
            form = SetPasswordForm(user=user)

    return render(
        request,
        "user/password_reset_request.html",
        {
            "email_value": email_value,
            "info_message": info_message,
            "errors": errors,
            "otp_required": otp_required,
            "otp_verified": otp_verified,
            "form": form,
            **pref,
        },
    )


def user_password_reset_confirm(request, uidb64, token):
    messages.info(
        request,
        "Trang đặt lại mật khẩu bằng link không còn sử dụng. Vui lòng dùng OTP."
    )
    return redirect("store:user_password_reset")


def user_register(request):
    pref = _admin_pref_context(request)
    form = UserCreationForm()
    email_value = ""
    full_name_value = ""
    phone_value = ""
    password_strength = ""
    info_message = ""

    if request.user.is_authenticated:
        if _is_admin_user(request.user):
            return redirect("store:admin_dashboard")
        return redirect("store:user_dashboard")

    if request.method == "POST":
        pending = request.session.get("register_pending") or {}
        otp_state = request.session.get("register_otp") or {}
        otp_input = (request.POST.get("otp") or "").strip()
        resend_otp = request.POST.get("resend_otp")
        reset_otp = request.POST.get("reset_otp")

        if reset_otp:
            _clear_register_otp_session(request)
            return redirect("store:user_register")

        if resend_otp and pending:
            otp_sent = _issue_register_otp(
                request,
                email=pending.get("email", ""),
                full_name=pending.get("full_name", ""),
                phone=pending.get("phone", ""),
                username=pending.get("username", ""),
            )
            if otp_sent:
                info_message = "Đã gửi lại OTP. Vui lòng kiểm tra email."
            else:
                error_text = request.session.pop("register_otp_error", "")
                form.add_error(None, "Không gửi được OTP. Vui lòng thử lại sau.")
                if error_text:
                    form.add_error(None, error_text)
        elif otp_input:
            if not pending or not otp_state:
                form.add_error(None, "Không tìm thấy yêu cầu OTP. Vui lòng đăng ký lại.")
                _clear_register_otp_session(request)
            else:
                expires_at = otp_state.get("expires_at")
                if not expires_at or timezone.now().timestamp() > float(expires_at):
                    form.add_error(None, "OTP đã hết hạn. Vui lòng gửi lại OTP.")
                elif otp_input != str(otp_state.get("code", "")):
                    form.add_error(None, "OTP không đúng. Vui lòng thử lại.")
                else:
                    email = pending.get("email", "")
                    email, email_error = _clean_user_email(email)
                    if email_error:
                        form.add_error(None, email_error)
                    elif User.objects.filter(username=pending.get("username", "")).exists():
                        form.add_error(None, "Tài khoản đã tồn tại. Vui lòng đăng ký lại.")
                    else:
                        user = User.objects.create_user(
                            username=pending.get("username", ""),
                            email=email,
                            password=pending.get("password", ""),
                        )
                        if pending.get("full_name"):
                            user.first_name, user.last_name = _split_full_name(pending["full_name"])
                            user.save(update_fields=["first_name", "last_name"])
                        _sync_user_role(user, ROLE_USER)
                        profile = _get_customer_profile(user)
                        if pending.get("phone"):
                            profile.so_dien_thoai = pending["phone"]
                            profile.save(update_fields=["so_dien_thoai"])
                        _clear_register_otp_session(request)
                        login(request, user)
                        messages.success(request, pref["t"]["user_created"])
                        return redirect("store:user_dashboard")
        else:
            if pending:
                form.add_error(None, "Vui lòng nhập OTP để xác nhận đăng ký.")
            else:
                form = UserCreationForm(request.POST)
                email_value = (request.POST.get("email") or "").strip()
                full_name_value = (request.POST.get("full_name") or "").strip()
                phone_value = (request.POST.get("phone") or "").strip()
                password_strength = _password_strength(request.POST.get("password1") or "")
                email, email_error = _clean_user_email(email_value)
                if email_error:
                    form.add_error(None, email_error)
                if password_strength == "weak":
                    form.add_error("password1", pref["t"]["password_too_weak"])
                normalized_phone = _normalize_phone(phone_value)
                if not normalized_phone:
                    form.add_error(None, "Vui lòng nhập số điện thoại để nhận OTP.")
                elif len(normalized_phone) < 9 or len(normalized_phone) > 11:
                    form.add_error(None, "Số điện thoại không hợp lệ.")
                if form.is_valid():
                    request.session["register_pending"] = {
                        "username": form.cleaned_data.get("username", ""),
                        "email": email,
                        "full_name": full_name_value,
                        "phone": normalized_phone,
                        "password": form.cleaned_data.get("password1", ""),
                    }
                    request.session.modified = True
                    otp_sent = _issue_register_otp(
                        request,
                        email=email,
                        full_name=full_name_value,
                        phone=normalized_phone,
                        username=form.cleaned_data.get("username", ""),
                    )
                    if otp_sent:
                        info_message = "Đã gửi OTP đến email. Vui lòng kiểm tra Mailtrap và nhập mã OTP."
                    else:
                        error_text = request.session.pop("register_otp_error", "")
                        form.add_error(None, "Không gửi được OTP. Vui lòng thử lại sau.")
                        if error_text:
                            form.add_error(None, error_text)

    pending_state = request.session.get("register_pending") or {}
    otp_required = bool(pending_state)
    if otp_required:
        if not info_message:
            info_message = "Vui lòng nhập OTP đã gửi về email để hoàn tất đăng ký."
        email_value = pending_state.get("email", email_value)
        full_name_value = pending_state.get("full_name", full_name_value)
        phone_value = pending_state.get("phone", phone_value)
        if "username" in pending_state:
            form.fields["username"].initial = pending_state.get("username")
            form.fields["username"].widget.attrs["readonly"] = "readonly"
        for pwd_name in ("password1", "password2"):
            field = form.fields.get(pwd_name)
            if field:
                field.widget.attrs["readonly"] = "readonly"
                field.widget.attrs["disabled"] = "disabled"
                field.widget.attrs["placeholder"] = "Đã lưu mật khẩu"

    return render(
        request,
        "user/register.html",
        {
            "form": form,
            "email_value": email_value,
            "full_name_value": full_name_value,
            "phone_value": phone_value,
            "password_strength_value": password_strength,
            "otp_required": otp_required,
            "info_message": info_message,
            **pref,
        },
    )


def admin_logout(request):
    logout(request)
    return redirect("store:admin_login")


def user_logout(request):
    logout(request)
    return redirect("store:user_login")


def admin_dashboard(request):
    unauthorized = _require_admin_permission(request, "dashboard")
    if unauthorized:
        return unauthorized

    pref = _admin_pref_context(request)
    lang = pref["admin_lang"]
    defaults = _about_page_defaults()
    modules = _menu_context(lang, request.user)
    return render(
        request,
        "admin/index.html",
        {
            "modules": modules,
            "total_records": sum(item["count"] for item in modules),
            **_dashboard_context(),
            **pref,
        },
    )


def home(request):
    featured_products = list(
        SanPham.objects.prefetch_related("hinh_anh_phu").order_by("ten")[:8]
    )
    for product in featured_products:
        product.display_price = _format_currency(product.gia_ban)
        product.card_gallery = _build_product_card_gallery(product)
    return render(
        request,
        "store/home.html",
        {
            "featured_products": featured_products,
            "cart_total_quantity": _cart_items(request)[1],
            **_admin_pref_context(request),
        },
    )


def info_page(request, slug):
    pref = _admin_pref_context(request)
    if slug == "gioi-thieu-circle-k":
        return render(request, "store/info_page.html", context=_build_about_public_page_context(pref))

    page = INFO_PAGES.get(slug)
    if not page:
        return render(
            request,
            "store/info_page.html",
            status=404,
            context={
                "title": "Không tìm thấy nội dung",
                "kicker": "404",
                "summary": "Trang bạn yêu cầu không tồn tại hoặc đã được di chuyển.",
                "sections": [],
                "hero_image": "https://images.unsplash.com/photo-1585238342024-78d387f4a707?auto=format&fit=crop&w=1400&q=80",
                "is_not_found": True,
                **pref,
            },
        )

    media = PAGE_MEDIA.get(slug, {})
    section_images = media.get("section_images", [])

    sections = []
    for idx, section in enumerate(page.get("sections", [])):
        section_data = dict(section)
        if section_images:
            section_data["image"] = section_images[idx % len(section_images)]
        sections.append(section_data)

    context = dict(page)
    context["page_slug"] = slug
    context["sections"] = sections
    context["hero_image"] = media.get(
        "hero_image",
        "https://images.unsplash.com/photo-1521791136064-7986c2920216?auto=format&fit=crop&w=1400&q=80",
    )
    if slug == "tin-tuc-su-kien":
        featured_news, news_items = _news_entries()
        context["featured_news"] = featured_news
        context["news_items"] = news_items
    context.update(pref)
    return render(request, "store/info_page.html", context=context)


def admin_about(request):
    unauthorized = _require_admin_permission(request, "about")
    if unauthorized:
        return unauthorized

    pref = _admin_pref_context(request)
    lang = pref["admin_lang"]
    page, _ = TrangGioiThieu.objects.get_or_create(pk=1, defaults=_about_page_defaults())

    form = TrangGioiThieuAdminForm(instance=page)
    if request.method == "POST":
        form = TrangGioiThieuAdminForm(request.POST, request.FILES, instance=page)
        if form.is_valid():
            deleted_groups = 0
            slot_payloads, slot_errors = _collect_about_gallery_slot_payloads(
                request.FILES,
                request.POST,
                slot_count=4,
                min_images_per_slot=3,
            )
            if slot_errors:
                for error in slot_errors:
                    form.add_error(None, error)
            else:
                page = form.save()
                deleted_groups = _delete_about_gallery_groups(page, request.POST)
                _update_about_gallery_group_details(page, request.POST)
                _update_about_gallery_details(page, request.POST)
                _save_about_gallery_slots(page, slot_payloads)
                success_message = "Đã lưu nội dung trang giới thiệu."
                if deleted_groups:
                    success_message += f" Đã xóa {deleted_groups} ảnh từ các bài cũ đã chọn."
                messages.success(request, success_message)
                return redirect("store:admin_about")

    file_previews = _build_file_preview_context(TrangGioiThieu, page)
    preview_images = []
    for field_name in ("anh_bia", "anh_noi_dung_1", "anh_noi_dung_2", "anh_noi_dung_3"):
        preview = file_previews.get(field_name, {})
        if preview.get("url"):
            preview_images.append({"name": field_name, "url": preview["url"]})
    gallery_preview_images = [
        {"name": f"gallery_{item.pk}", "pk": item.pk, "url": item.hinh_anh.url, "title": item.tieu_de, "caption": item.chu_thich}
        for item in page.hinh_anh_phu.all().order_by("thu_tu", "id")
        if getattr(item.hinh_anh, "url", "")
    ]
    for image in gallery_preview_images:
        image["title_input_name"] = f"gallery_title_{image['pk']}"
        image["caption_input_name"] = f"gallery_caption_{image['pk']}"
    gallery_admin_groups = _about_page_gallery_admin_groups(page)
    for group in gallery_admin_groups:
        group["title_input_name"] = f"group_title::{group['group_key']}"
        group["caption_input_name"] = f"group_caption::{group['group_key']}"
    gallery_input_slots = [{"index": index} for index in range(1, 5)]

    return render(
        request,
        "admin/about.html",
        {
            "modules": _menu_context(lang, request.user),
            "form": form,
            "file_previews": file_previews,
            "preview_images": preview_images,
            "gallery_preview_images": gallery_preview_images,
            "gallery_admin_groups": gallery_admin_groups,
            "gallery_input_slots": gallery_input_slots,
            "public_about_url": reverse("store:info_page", kwargs={"slug": "gioi-thieu-circle-k"}),
            "about_is_customized": _about_page_has_custom_content(page),
            "public_preview": _build_about_public_page_context(pref),
            "page_obj": page,
            **pref,
        },
    )


def admin_inventory_hub(request):
    unauthorized = _require_admin_permission(request, "inventory_hub")
    if unauthorized:
        return unauthorized

    pref = _admin_pref_context(request)
    lang = pref["admin_lang"]
    return render(
        request,
        "admin/inventory_hub.html",
        {
            "modules": _menu_context(lang, request.user),
            **_inventory_hub_context(),
            **pref,
        },
    )


def admin_inventory_restock(request):
    unauthorized = _require_module_permission(request, "giao-dich-kho", "create")
    if unauthorized:
        return unauthorized

    pref = _admin_pref_context(request)
    lang = pref["admin_lang"]
    stores = list(CuaHang.objects.select_related("chuoi").order_by("chuoi__ten", "ten", "pk"))
    selected_store_ids = [str(store.pk) for store in stores]
    target_stock = 25

    trigger_threshold = SanPham.LOW_STOCK_THRESHOLD
    note = "Nhập bù cho các cửa hàng đang thiếu hàng"

    if request.method == "POST":
        selected_store_ids = [value for value in request.POST.getlist("store_ids") if value.strip()]
        note = (request.POST.get("note") or note).strip()
        try:
            target_stock = int(request.POST.get("target_stock") or 25)
        except (TypeError, ValueError):
            target_stock = 0
        try:
            trigger_threshold = int(request.POST.get("trigger_threshold") or SanPham.LOW_STOCK_THRESHOLD)
        except (TypeError, ValueError):
            trigger_threshold = -1

        if not selected_store_ids:
            messages.error(request, "Vui lòng chọn ít nhất một cửa hàng để nhập kho.")
        elif not note:
            messages.error(request, "Vui lòng nhập lý do điều chỉnh tồn kho.")
        else:
            try:
                summary = restock_products(
                    target_stock=target_stock,
                    note=note,
                    store_ids=[int(store_id) for store_id in selected_store_ids],
                    trigger_threshold=trigger_threshold,
                )
            except ValueError as exc:
                messages.error(request, str(exc))
            except LookupError as exc:
                messages.error(request, str(exc))
            else:
                if summary["created_movements"] > 0:
                    messages.success(
                        request,
                        (
                            "Đã nhập bù thành công cho "
                            f"{summary['store_count']} cửa hàng, "
                            f"tạo {summary['created_movements']} phiếu nhập, "
                            f"bổ sung {summary['imported_units']} đơn vị hàng. "
                            f"Đã đối chiếu lại {summary['reconciled_stock_rows']} dòng tồn kho."
                        ),
                    )
                else:
                    messages.info(
                        request,
                        (
                            "Không có cửa hàng nào cần nhập thêm theo ngưỡng đã chọn. "
                            f"Hệ thống đã đối chiếu lại {summary['reconciled_stock_rows']} dòng tồn kho "
                            f"và không thấy cặp cửa hàng x sản phẩm nào có tồn <= {summary['trigger_threshold']}."
                        ),
                    )
                return redirect("store:admin_inventory_restock")

    return render(
        request,
        "admin/inventory_restock.html",
        {
            "modules": _menu_context(lang, request.user),
            "stores": stores,
            "selected_store_ids": selected_store_ids,
            "target_stock": target_stock,
            "trigger_threshold": trigger_threshold,
            "note_value": note,
            "model_slug": "giao-dich-kho",
            **pref,
        },
    )


def admin_inventory_report(request):
    unauthorized = _require_module_permission(request, "giao-dich-kho", "view")
    if unauthorized:
        return unauthorized

    pref = _admin_pref_context(request)
    lang = pref["admin_lang"]

    store_id = (request.GET.get("store_id") or "").strip()
    start_raw = (request.GET.get("start") or "").strip()
    end_raw = (request.GET.get("end") or "").strip()

    today = timezone.localdate()
    default_start = today - timezone.timedelta(days=6)
    try:
        start_date = timezone.datetime.strptime(start_raw, "%Y-%m-%d").date() if start_raw else default_start
    except ValueError:
        start_date = default_start
    try:
        end_date = timezone.datetime.strptime(end_raw, "%Y-%m-%d").date() if end_raw else today
    except ValueError:
        end_date = today
    if start_date > end_date:
        start_date, end_date = end_date, start_date

    current_tz = timezone.get_current_timezone()
    start_dt = timezone.make_aware(datetime.combine(start_date, time.min), current_tz)
    end_dt = timezone.make_aware(datetime.combine(end_date + timedelta(days=1), time.min), current_tz)

    qs = GiaoDichKho.objects.select_related("cua_hang").filter(
        created_at__gte=start_dt,
        created_at__lt=end_dt,
    )
    if store_id.isdigit():
        qs = qs.filter(cua_hang_id=int(store_id))

    from django.db.models import Sum, Case, When, IntegerField
    from django.db.models.functions import TruncDate

    daily_rows = (
        qs.annotate(day=TruncDate("created_at", tzinfo=current_tz))
        .values("day", "cua_hang__ten", "cua_hang_id")
        .annotate(
            import_total=Sum(
                Case(When(loai="import", then="so_luong"), default=0, output_field=IntegerField())
            ),
            export_total=Sum(
                Case(When(loai="export", then="so_luong"), default=0, output_field=IntegerField())
            ),
        )
        .order_by("-day", "cua_hang__ten")
    )

    totals = qs.aggregate(
        import_total=Sum(
            Case(When(loai="import", then="so_luong"), default=0, output_field=IntegerField())
        ),
        export_total=Sum(
            Case(When(loai="export", then="so_luong"), default=0, output_field=IntegerField())
        ),
    )

    stores = list(CuaHang.objects.select_related("chuoi").order_by("chuoi__ten", "ten"))

    return render(
        request,
        "admin/inventory_report.html",
        {
            "modules": _menu_context(lang, request.user),
            "stores": stores,
            "selected_store_id": store_id,
            "start_date": start_date,
            "end_date": end_date,
            "daily_rows": daily_rows,
            "totals": totals,
            **pref,
        },
    )


def admin_store_stock_list(request):
    unauthorized = _require_module_permission(request, "ton-kho-cua-hang", "view")
    if unauthorized:
        return unauthorized

    pref = _admin_pref_context(request)
    lang = pref["admin_lang"]
    q = (request.GET.get("q") or "").strip()

    store_qs = CuaHang.objects.select_related("chuoi").annotate(
        total_units=Coalesce(dj_models.Sum("ton_kho_san_pham__ton_kho"), 0),
        sku_count=Coalesce(
            dj_models.Count(
                "ton_kho_san_pham",
                filter=Q(ton_kho_san_pham__ton_kho__gt=0),
                distinct=True,
            ),
            0,
        ),
        last_updated=dj_models.Max("ton_kho_san_pham__updated_at"),
    )

    if q:
        store_qs = store_qs.filter(
            Q(ten__icontains=q)
            | Q(dia_chi__icontains=q)
            | Q(quan_huyen__icontains=q)
            | Q(chuoi__ten__icontains=q)
        )

    store_qs = store_qs.order_by("-total_units", "ten", "pk")

    paginator = Paginator(store_qs, 15)
    page_obj = paginator.get_page(request.GET.get("page"))

    persisted_params = []
    for key in request.GET.keys():
        if key == "page":
            continue
        for value in request.GET.getlist(key):
            if value != "":
                persisted_params.append((key, value))
    persisted_query = urlencode(persisted_params, doseq=True)

    return render(
        request,
        "admin/store_stock_list.html",
        {
            "model_slug": "ton-kho-cua-hang",
            "model_name": "Tồn kho cửa hàng",
            "query_value": q,
            "page_obj": page_obj,
            "paginator": paginator,
            "persisted_query": persisted_query,
            "modules": _menu_context(lang, request.user),
            **pref,
        },
    )


def admin_store_stock_detail(request, store_id: int):
    unauthorized = _require_module_permission(request, "ton-kho-cua-hang", "view")
    if unauthorized:
        return unauthorized

    pref = _admin_pref_context(request)
    lang = pref["admin_lang"]
    store = get_object_or_404(CuaHang.objects.select_related("chuoi"), pk=store_id)

    q = (request.GET.get("q") or "").strip()

    qs = (
        TonKhoCuaHang.objects.filter(cua_hang=store)
        .select_related("san_pham", "san_pham__nhom_san_pham", "san_pham__thuong_hieu")
        .order_by("-ton_kho", "san_pham__ten", "pk")
    )
    if q:
        qs = qs.filter(
            Q(san_pham__ten__icontains=q)
            | Q(san_pham__nhom_san_pham__ten__icontains=q)
            | Q(san_pham__thuong_hieu__ten__icontains=q)
        )

    paginator = Paginator(qs, 20)
    page_obj = paginator.get_page(request.GET.get("page"))

    persisted_params = []
    for key in request.GET.keys():
        if key == "page":
            continue
        for value in request.GET.getlist(key):
            if value != "":
                persisted_params.append((key, value))
    persisted_query = urlencode(persisted_params, doseq=True)

    back_url = (request.GET.get("back") or "").strip()
    if not back_url or not back_url.startswith("/") or back_url.startswith("//"):
        back_url = reverse("store:admin_list", args=["ton-kho-cua-hang"])

    return render(
        request,
        "admin/store_stock_detail.html",
        {
            "store": store,
            "model_slug": "ton-kho-cua-hang",
            "model_name": "Tồn kho cửa hàng",
            "query_value": q,
            "page_obj": page_obj,
            "paginator": paginator,
            "persisted_query": persisted_query,
            "back_url": back_url,
            "modules": _menu_context(lang, request.user),
            **pref,
        },
    )


def admin_store_employees(request, pk):
    unauthorized = _require_module_permission(request, "giao-dich-kho", "view")
    if unauthorized:
        return JsonResponse({"error": "forbidden"}, status=403)

    employees = (
        NhanVien.objects.filter(cua_hang_id=pk, co_quyen_nhap_kho=True)
        .order_by("ho_ten")
        .values("id", "ho_ten")
    )
    return JsonResponse({"employees": list(employees)})


def admin_employee_store(request, pk):
    unauthorized = _require_module_permission(request, "giao-dich-kho", "view")
    if unauthorized:
        return JsonResponse({"error": "forbidden"}, status=403)

    employee = get_object_or_404(NhanVien, pk=pk)
    store = employee.cua_hang
    return JsonResponse(
        {
            "id": store.pk,
            "ten": store.ten,
        }
    )


def admin_user_password(request, pk):
    unauthorized = _require_admin_permission(request, "user_management")
    if unauthorized:
        return unauthorized

    pref = _admin_pref_context(request)
    user_obj = get_object_or_404(User, pk=pk)
    form = SetPasswordForm(user=user_obj)
    password_strength = ""

    if request.method == "POST":
        form = SetPasswordForm(user=user_obj, data=request.POST)
        password_strength = _enforce_password_strength(form, pref)
        if form.is_valid():
            form.save()
            messages.success(request, pref["t"]["password_updated"])
            return redirect("store:admin_user_management")

    return render(
        request,
        "admin/password_form.html",
        {
            "modules": _menu_context(pref["admin_lang"], request.user),
            "form": form,
            "page_heading": f'{pref["t"]["reset_password"]}: {user_obj.username}',
            "password_strength_value": password_strength,
            **pref,
        },
    )


@require_POST
def admin_order_status_action(request, pk, status):
    unauthorized = _require_module_permission(request, ORDER_MODULE_SLUG, "status")
    if unauthorized:
        return unauthorized

    if status not in {"confirmed", "shipping", "delivered", "done", "cancelled"}:
        return _admin_redirect_with_preserved_query(request)

    order = get_object_or_404(DonHang, pk=pk)
    allowed_transitions = {
        "pending": {"confirmed", "cancelled"},
        "confirmed": {"shipping", "cancelled"},
        "shipping": {"delivered", "cancelled"},
        "delivered": {"done"},
        "done": set(),
        "cancelled": set(),
    }
    if status not in allowed_transitions.get(order.trang_thai, set()):
        return _admin_redirect_with_preserved_query(request)

    with transaction.atomic():
        order.trang_thai = status
        order.save(update_fields=["trang_thai"])
        if status == "cancelled":
            _release_order_inventory_if_needed(order, reason="đơn hàng bị hủy")
    _create_admin_notification(
        f"Cập nhật đơn hàng #{order.pk}",
        (
            f"Đơn #{order.pk} của khách hàng {order.khach_hang.username} "
            f"đã được chuyển sang trạng thái {order.get_trang_thai_display().lower()}."
        ),
        level="info",
        path=reverse("store:admin_list", kwargs={"model_slug": ORDER_MODULE_SLUG}),
        method="PATCH",
        status_code=200,
    )
    messages.success(request, _admin_pref_context(request)["t"]["order_status_updated"])

    return _admin_redirect_with_preserved_query(request)


@require_POST
def admin_order_payment_status_action(request, pk, status):
    unauthorized = _require_module_permission(request, ORDER_MODULE_SLUG, "payment_status")
    if unauthorized:
        return unauthorized

    if status not in {"unpaid", "paid", "awaiting_confirmation", "refunded"}:
        return _admin_redirect_with_preserved_query(request)

    order = get_object_or_404(DonHang, pk=pk)
    allowed_transitions = {
        "unpaid": {"paid", "awaiting_confirmation"},
        "awaiting_confirmation": {"paid", "unpaid", "refunded"},
        "paid": {"refunded"},
        "refunded": set(),
    }
    if status not in allowed_transitions.get(order.trang_thai_thanh_toan, set()):
        return _admin_redirect_with_preserved_query(request)

    with transaction.atomic():
        order.trang_thai_thanh_toan = status
        order.save(update_fields=["trang_thai_thanh_toan"])
        if status == "unpaid" and order.trang_thai == "pending":
            order.trang_thai = "cancelled"
            order.save(update_fields=["trang_thai"])
            _release_order_inventory_if_needed(order, reason="thanh toán bị trả về chưa thanh toán")
    _create_admin_notification(
        f"Cập nhật thanh toán đơn #{order.pk}",
        (
            f"Trạng thái thanh toán của đơn #{order.pk} "
            f"đã chuyển sang {order.get_trang_thai_thanh_toan_display().lower()}."
        ),
        level="info",
        path=reverse("store:admin_list", kwargs={"model_slug": ORDER_MODULE_SLUG}),
        method="PATCH",
        status_code=200,
    )
    messages.success(request, "Đã cập nhật trạng thái thanh toán.")

    return _admin_redirect_with_preserved_query(request)


@require_POST
def admin_order_receipt_review_action(request, pk, action):
    unauthorized = _require_module_permission(request, ORDER_MODULE_SLUG, "payment_status")
    if unauthorized:
        return unauthorized

    if action not in {"approve", "reject"}:
        return _admin_redirect_with_preserved_query(request)

    order = get_object_or_404(DonHang, pk=pk)
    if order.phuong_thuc_thanh_toan != "bank_transfer" or not order.anh_bien_lai:
        return _admin_redirect_with_preserved_query(request)

    rejection_note = (request.POST.get("rejection_note") or "").strip()
    if action == "reject" and not rejection_note:
        messages.error(request, "Vui lòng nhập ghi chú từ chối biên lai.")
        return _admin_redirect_with_preserved_query(request)

    if order.trang_thai_thanh_toan not in {"awaiting_confirmation", "unpaid"}:
        return _admin_redirect_with_preserved_query(request)

    with transaction.atomic():
        if action == "approve":
            order.trang_thai_thanh_toan = "paid"
            order.save(update_fields=["trang_thai_thanh_toan"])
            _log_payment_confirmation(
                order,
                "approved",
                performed_by=request.user,
                note="Biên lai chuyển khoản đã được duyệt.",
            )
            messages.success(request, "Đã duyệt biên lai chuyển khoản.")
        else:
            order.trang_thai_thanh_toan = "unpaid"
            order.save(update_fields=["trang_thai_thanh_toan"])
            _log_payment_confirmation(
                order,
                "rejected",
                performed_by=request.user,
                note=rejection_note,
            )
            messages.warning(request, "Đã từ chối biên lai chuyển khoản.")

    return _admin_redirect_with_preserved_query(request)


@require_POST
def admin_store_toggle_24h(request, pk):
    unauthorized = _require_module_permission(request, "cua-hang", "update")
    if unauthorized:
        return unauthorized

    store = get_object_or_404(CuaHang, pk=pk)
    new_state = not bool(store.hoat_dong_24h)
    store.hoat_dong_24h = new_state
    store.save(update_fields=["hoat_dong_24h"])
    status_label = "hoạt động 24h" if new_state else "không hoạt động 24h"
    _create_admin_notification(
        f"Cập nhật cửa hàng #{store.pk}",
        f"Cửa hàng {store.ten} đã được chuyển sang trạng thái {status_label}.",
        level="info",
        path=reverse("store:admin_list", kwargs={"model_slug": "cua-hang"}),
        method="PATCH",
        status_code=200,
    )
    messages.success(request, f"Đã cập nhật: {store.ten} {status_label}.")

    return _admin_redirect_with_preserved_query(request, model_slug="cua-hang")


def admin_user_management(request):
    unauthorized = _require_admin_permission(request, "user_management")
    if unauthorized:
        return unauthorized

    _ensure_role_groups()
    pref = _admin_pref_context(request)
    lang = pref["admin_lang"]
    form = UserCreationForm()
    create_user_email = ""
    create_user_full_name = ""
    create_user_role = ROLE_CUSTOMER
    create_user_is_active = True
    create_user_password_strength = ""
    query = request.GET.get("q", "").strip()
    filter_field = request.GET.get("f", "").strip()

    if request.method == "POST":
        action = request.POST.get("action") or "update_role"
        if action == "create_user":
            form = UserCreationForm(request.POST)
            create_user_email = (request.POST.get("email") or "").strip()
            create_user_full_name = (request.POST.get("full_name") or "").strip()
            create_user_role = request.POST.get("role", ROLE_CUSTOMER)
            create_user_is_active = request.POST.get("is_active") == "on"
            create_user_password_strength = _password_strength(request.POST.get("password1") or "")
            email, email_error = _clean_user_email(create_user_email)
            if email_error:
                form.add_error(None, email_error)
            if create_user_password_strength == "weak":
                form.add_error("password1", pref["t"]["password_too_weak"])
            if form.is_valid():
                user = form.save(commit=False)
                if create_user_full_name:
                    user.first_name, user.last_name = _split_full_name(create_user_full_name)
                user.email = email
                user.is_active = create_user_is_active
                user.save()
                _sync_user_role(user, create_user_role)
                messages.success(request, pref["t"]["user_created"])
                return redirect("store:admin_user_management")
        elif action == "toggle_lock":
            user = get_object_or_404(User, pk=request.POST.get("user_id"))
            if user.is_superuser:
                messages.error(request, "Không thể khóa tài khoản superuser.")
                return redirect("store:admin_user_management")
            if user.pk == request.user.pk:
                messages.error(request, "Bạn không thể tự khóa tài khoản của chính mình.")
                return redirect("store:admin_user_management")
            if _get_user_role(user) != ROLE_SYSTEM_ADMIN:
                messages.error(request, "Chỉ cho phép khóa/mở khóa tài khoản quản trị hệ thống.")
                return redirect("store:admin_user_management")
            user.is_active = not user.is_active
            user.save(update_fields=["is_active"])
            status_text = "đã mở khóa" if user.is_active else "đã khóa"
            messages.success(request, f"Tài khoản {user.username} {status_text}.")
            redirect_url = reverse("store:admin_user_management")
            query_params = []
            if query:
                query_params.append(f"q={query}")
            if filter_field:
                query_params.append(f"f={filter_field}")
            if query_params:
                redirect_url = f"{redirect_url}?{'&'.join(query_params)}"
            return redirect(redirect_url)
        elif action == "update_role":
            user = get_object_or_404(User, pk=request.POST.get("user_id"))
            full_name = (request.POST.get("full_name") or "").strip()
            email_input = (request.POST.get("email") or "").strip()
            email, email_error = _clean_user_email(email_input, exclude_user_id=user.pk)
            if email_error:
                messages.error(request, f"{user.username}: {email_error}")
                redirect_url = reverse("store:admin_user_management")
                query_params = []
                if query:
                    query_params.append(f"q={query}")
                if filter_field:
                    query_params.append(f"f={filter_field}")
                if query_params:
                    redirect_url = f"{redirect_url}?{'&'.join(query_params)}"
                return redirect(redirect_url)

            if full_name:
                user.first_name, user.last_name = _split_full_name(full_name)
            else:
                user.first_name = ""
                user.last_name = ""
            user.email = email
            if not user.is_superuser:
                user.is_active = request.POST.get("is_active") == "on"
                user.save(update_fields=["first_name", "last_name", "email", "is_active"])
            else:
                user.save(update_fields=["first_name", "last_name", "email"])
            _sync_user_role(user, request.POST.get("role", ROLE_CUSTOMER))
            messages.success(request, pref["t"]["user_updated"])
            redirect_url = reverse("store:admin_user_management")
            query_params = []
            if query:
                query_params.append(f"q={query}")
            if filter_field:
                query_params.append(f"f={filter_field}")
            if query_params:
                redirect_url = f"{redirect_url}?{'&'.join(query_params)}"
            return redirect(redirect_url)
        elif action == "delete_user":
            user = get_object_or_404(User, pk=request.POST.get("user_id"))
            if user.is_superuser:
                messages.error(request, "Không thể xóa tài khoản superuser.")
            elif user.pk == request.user.pk:
                messages.error(request, "Bạn không thể tự xóa tài khoản của chính mình.")
            else:
                username = user.username
                full_name = user.get_full_name().strip() or "-"
                email = user.email or "-"
                user.delete()
                _create_admin_notification(
                    f"Đã xóa tài khoản #{request.POST.get('user_id')}",
                    f"Tài khoản {username} ({full_name}) - {email} đã được xóa khỏi hệ thống.",
                    level="warning",
                    path=reverse("store:admin_user_management"),
                    method="DELETE",
                    status_code=200,
                )
                messages.success(request, f"Đã xóa tài khoản {username}.")
            redirect_url = reverse("store:admin_user_management")
            query_params = []
            if query:
                query_params.append(f"q={query}")
            if filter_field:
                query_params.append(f"f={filter_field}")
            if query_params:
                redirect_url = f"{redirect_url}?{'&'.join(query_params)}"
            return redirect(redirect_url)

    user_qs = User.objects.order_by("username")
    if query:
        filter_field = filter_field or ""
        if filter_field == "username":
            user_qs = user_qs.filter(username__icontains=query)
        elif filter_field == "email":
            user_qs = user_qs.filter(email__icontains=query)
        elif filter_field == "full_name":
            user_qs = user_qs.filter(Q(first_name__icontains=query) | Q(last_name__icontains=query))
        elif filter_field == "role":
            role_value = query.strip().lower()
            role_aliases = {
                "admin": ROLE_SYSTEM_ADMIN,
                "administrator": ROLE_SYSTEM_ADMIN,
                "quan tri": ROLE_SYSTEM_ADMIN,
                "quản trị": ROLE_SYSTEM_ADMIN,
                "quan ly kho": ROLE_STOCK_MANAGER,
                "quản lý kho": ROLE_STOCK_MANAGER,
                "kho": ROLE_STOCK_MANAGER,
                "quan ly don hang": ROLE_ORDER_MANAGER,
                "quản lý đơn hàng": ROLE_ORDER_MANAGER,
                "don hang": ROLE_ORDER_MANAGER,
                "đơn hàng": ROLE_ORDER_MANAGER,
                "cskh": ROLE_CUSTOMER_SUPPORT,
                "nhan vien cskh": ROLE_CUSTOMER_SUPPORT,
                "nhân viên cskh": ROLE_CUSTOMER_SUPPORT,
                "support": ROLE_CUSTOMER_SUPPORT,
                "customer": ROLE_CUSTOMER,
                "user": ROLE_CUSTOMER,
                "khach": ROLE_CUSTOMER,
                "khách": ROLE_CUSTOMER,
            }
            role_value = role_aliases.get(role_value, role_value)
            user_qs = user_qs.filter(groups__name=role_value)
        elif filter_field == "status":
            q_lower = query.strip().lower()
            truthy = {"1", "true", "yes", "on", "hoat dong", "hoạt động", "active"}
            falsy = {"0", "false", "no", "off", "ngung", "ngừng", "inactive"}
            if q_lower in truthy:
                user_qs = user_qs.filter(is_active=True)
            elif q_lower in falsy:
                user_qs = user_qs.filter(is_active=False)
            else:
                user_qs = user_qs.none()
        else:
            user_qs = user_qs.filter(
                Q(username__icontains=query)
                | Q(email__icontains=query)
                | Q(first_name__icontains=query)
                | Q(last_name__icontains=query)
            )

    paginator = Paginator(user_qs, 15)
    page_obj = paginator.get_page(request.GET.get("page"))

    users = []
    for user in page_obj.object_list:
        users.append(
            {
                "object": user,
                "role": _get_user_role(user),
                "role_label": _role_label(_get_user_role(user)),
                "full_name": user.get_full_name().strip() or "-",
            }
        )

    return render(
        request,
        "admin/user_management.html",
        {
            "modules": _menu_context(lang, request.user),
            "create_user_form": form,
            "create_user_email": create_user_email,
            "create_user_full_name": create_user_full_name,
            "create_user_role": create_user_role,
            "create_user_is_active": create_user_is_active,
            "create_user_password_strength": create_user_password_strength,
            "users": users,
            "page_obj": page_obj,
            "paginator": paginator,
            "query": query,
            "filter_field": filter_field,
            "role_choices": ROLE_CHOICES,
            **pref,
        },
    )


def admin_settings(request):
    unauthorized = _require_admin_permission(request, "settings")
    if unauthorized:
        return unauthorized

    if request.method == "POST":
        lang = request.POST.get("language", "vi")
        theme = request.POST.get("theme", "light")
        if lang not in CMS_TRANSLATIONS:
            lang = "vi"
        if theme not in {"light", "dark"}:
            theme = "light"
        request.session["admin_lang"] = lang
        request.session["admin_theme"] = theme
        messages.success(request, CMS_TRANSLATIONS[lang]["settings_saved"])
        return redirect("store:admin_settings")

    pref = _admin_pref_context(request)
    return render(request, "admin/settings.html", {"modules": _menu_context(pref["admin_lang"], request.user), **pref})


def _infer_product_ai_category(product) -> str:
    group_name = ""
    try:
        group_name = (product.nhom_san_pham.ten if product.nhom_san_pham else "") or ""
    except Exception:
        group_name = ""
    text = f"{product.ten} {group_name}".lower()
    if any(k in text for k in ["nước", "cà phê", "trà", "sữa", "drink", "sting", "aquafina", "coca", "pepsi"]):
        return "Đồ uống"
    if any(k in text for k in ["mì", "xôi", "bánh mì", "tokbokki", "sandwich", "cơm", "cháo", "lẩu"]):
        return "Đồ ăn nhanh"
    if any(k in text for k in ["snack", "bắp rang", "kẹo", "chip", "ostar"]):
        return "Ăn vặt"
    return "Khác"


def _strip_parenthetical_text(value):
    text = "" if value is None else str(value)
    text = re.sub(r"\s*\([^)]*\)", "", text)
    return re.sub(r"\s{2,}", " ", text).strip()


def _extract_district_from_address(address):
    text = "" if address is None else str(address).strip()
    if not text:
        return ""
    for chunk in [c.strip() for c in text.split(",") if c.strip()]:
        low = chunk.lower()
        if "quận" in low or "huyện" in low or "thủ đức" in low:
            return chunk
    return ""


def _facet_specs_for_model(model_slug):
    return {
        "thuong-hieu": [
            {"param": "brand", "label": "Thương hiệu", "expr": "ten"},
        ],
        "nha-cung-cap": [
            {"param": "supplier", "label": "Nhà cung cấp", "expr": "ten"},
        ],
        "nhom-san-pham": [
            {"param": "group", "label": "Nhóm sản phẩm", "expr": "ten"},
        ],
        "san-pham": [
            {"param": "group", "label": "Nhóm sản phẩm", "expr": "nhom_san_pham__ten"},
            {"param": "supplier", "label": "Nhà cung cấp", "expr": "nha_cung_cap__ten"},
            {"param": "brand", "label": "Thương hiệu", "expr": "thuong_hieu__ten"},
        ],
        "giao-dich-kho": [
            {"param": "product", "label": "Sản phẩm", "expr": "san_pham__ten"},
            {"param": "type", "label": "Loại giao dịch", "expr": "loai"},
            {"param": "staff", "label": "Nhân viên ký", "expr": "nhan_vien__ho_ten"},
        ],
        "chuoi-cua-hang": [
            {"param": "chain", "label": "Chuỗi cửa hàng", "expr": "ten"},
        ],
        "cua-hang": [
            {"param": "chain", "label": "Chuỗi cửa hàng", "expr": "chuoi__ten"},
            {"param": "district", "label": "Quận/Huyện", "expr": "quan_huyen"},
            {"param": "open24", "label": "Hoạt động", "bool_expr": "hoat_dong_24h"},
        ],
        "nhan-vien": [
            {"param": "role", "label": "Chức vụ", "expr": "chuc_vu"},
            {"param": "store", "label": "Cửa hàng", "expr": "cua_hang__ten"},
        ],
        "khuyen-mai": [
            {"param": "promo", "label": "Khuyến mãi", "expr": "ten"},
        ],
        "danh-gia-cua-hang": [
            {"param": "store", "label": u("C\u1eeda h\u00e0ng"), "expr": "cua_hang__ten"},
            {"param": "stars", "label": u("S\u1ed1 sao"), "expr": "so_sao", "custom": "fixed_star_choices"},
            {"param": "user", "label": u("Ng\u01b0\u1eddi d\u00f9ng"), "expr": "user__username"},
            {"param": "created_at_range", "label": u("Ng\u00e0y t\u1ea1o"), "custom": "date_range", "expr": "created_at"},
        ],
        "gop-y-khach-hang": [
            {"param": "topic", "label": "Chủ đề", "expr": "chu_de"},
            {"param": "responded", "label": "Đã phản hồi", "bool_expr": "da_phan_hoi"},
        ],
        "ho-so-khach-hang": [
            {"param": "user", "label": "Tài khoản", "expr": "user__username"},
            {"param": "district", "label": "Quận/Huyện", "custom": "district_from_address", "address_expr": "dia_chi"},
        ],
        "don-hang": [
            {"param": "payment", "label": "Thanh toán", "expr": "trang_thai_thanh_toan"},
            {"param": "store", "label": "Cửa hàng xử lý", "expr": "cua_hang_xu_ly__ten"},
        ],
        "chi-tiet-don-hang": [
            {"param": "order", "label": "Đơn hàng", "expr": "don_hang__id"},
            {"param": "group", "label": "Nhóm sản phẩm", "expr": "san_pham__nhom_san_pham__ten"},
        ],
    }.get(model_slug, [])


def _build_and_apply_facets(request, model_slug, qs, model):
    facet_filters = []
    specs = _facet_specs_for_model(model_slug)
    if not specs:
        return qs, facet_filters

    for spec in specs:
        param = spec["param"]
        selected = [v for v in request.GET.getlist(param) if str(v).strip()]

        if spec.get("bool_expr"):
            expr = spec["bool_expr"]
            options = [
                {"value": "1", "label": "Có", "selected": "1" in selected},
                {"value": "0", "label": "Không", "selected": "0" in selected},
            ]
            if selected:
                bool_values = []
                if "1" in selected:
                    bool_values.append(True)
                if "0" in selected:
                    bool_values.append(False)
                if bool_values:
                    qs = qs.filter(**{f"{expr}__in": bool_values})
            facet_filters.append(
                {
                    "param": param,
                    "label": spec["label"],
                    "options": options,
                    "selected_count": len([x for x in selected if x in {"1", "0"}]),
                }
            )
            continue

        if spec.get("custom") == "ai_product_category":
            all_products = list(model.objects.select_related("nhom_san_pham").all())
            categories = []
            by_id = {}
            for product in all_products:
                cat = _infer_product_ai_category(product)
                by_id[product.pk] = cat
                categories.append(cat)
            unique_cats = sorted(set(categories))
            options = [{"value": cat, "label": cat, "selected": cat in selected} for cat in unique_cats]
            if selected:
                allowed_ids = [pk for pk, cat in by_id.items() if cat in selected]
                qs = qs.filter(pk__in=allowed_ids)
            facet_filters.append(
                {
                    "param": param,
                    "label": spec["label"],
                    "options": options,
                    "selected_count": len(selected),
                }
            )
            continue

        if spec.get("custom") == "district_from_address":
            address_field = spec.get("address_expr")
            all_rows = list(model.objects.all().only("pk", address_field))
            district_by_id = {}
            districts = []
            for row in all_rows:
                district = _extract_district_from_address(getattr(row, address_field, ""))
                district_by_id[row.pk] = district
                if district:
                    districts.append(district)
            unique_districts = sorted(set(districts))
            options = [{"value": d, "label": d, "selected": d in selected} for d in unique_districts]
            if selected:
                allowed_ids = [pk for pk, district in district_by_id.items() if district in selected]
                qs = qs.filter(pk__in=allowed_ids)
            facet_filters.append(
                {
                    "param": param,
                    "label": spec["label"],
                    "options": options,
                    "selected_count": len(selected),
                }
            )
            continue
        if spec.get("custom") == "fixed_star_choices":
            selected_star = next((str(value) for value in selected if str(value) in {"1", "2", "3", "4", "5"}), "")
            if selected_star:
                qs = qs.filter(so_sao=int(selected_star))
            options = []
            for star in range(1, 6):
                star_value = str(star)
                params = request.GET.copy()
                if selected_star == star_value:
                    params.pop(param, None)
                else:
                    params.setlist(param, [star_value])
                query_string = params.urlencode()
                options.append(
                    {
                        "value": star_value,
                        "label": star_value,
                        "selected": selected_star == star_value,
                        "url": f"{request.path}?{query_string}" if query_string else request.path,
                    }
                )
            clear_params = request.GET.copy()
            clear_params.pop(param, None)
            clear_query_string = clear_params.urlencode()
            facet_filters.append(
                {
                    "param": param,
                    "label": spec["label"],
                    "options": options,
                    "selected_count": int(bool(selected_star)),
                    "clear_url": f"{request.path}?{clear_query_string}" if clear_query_string else request.path,
                }
            )
            continue
        if spec.get("custom") == "date_range":
            expr = spec["expr"]
            start_value = (request.GET.get(f"{param}_from") or "").strip()
            end_value = (request.GET.get(f"{param}_to") or "").strip()
            field = model._meta.get_field(expr)
            if field.get_internal_type() == "DateTimeField":
                start_date = parse_date(start_value) if start_value else None
                end_date = parse_date(end_value) if end_value else None
                current_tz = timezone.get_current_timezone()
                if start_date:
                    start_dt = timezone.make_aware(datetime.combine(start_date, time.min), current_tz)
                    qs = qs.filter(**{f"{expr}__gte": start_dt})
                if end_date:
                    end_dt = timezone.make_aware(datetime.combine(end_date + timedelta(days=1), time.min), current_tz)
                    qs = qs.filter(**{f"{expr}__lt": end_dt})
            else:
                if start_value:
                    qs = qs.filter(**{f"{expr}__gte": start_value})
                if end_value:
                    qs = qs.filter(**{f"{expr}__lte": end_value})
            facet_filters.append(
                {
                    "type": "date_range",
                    "param": param,
                    "label": spec["label"],
                    "from_name": f"{param}_from",
                    "to_name": f"{param}_to",
                    "from_value": start_value,
                    "to_value": end_value,
                    "selected_count": int(bool(start_value)) + int(bool(end_value)),
                }
            )
            continue


        expr = spec["expr"]
        values = list(
            model.objects.order_by(expr).values_list(expr, flat=True).distinct()
        )
        values = [str(v) for v in values if v not in (None, "")]
        options = [{"value": v, "label": _strip_parenthetical_text(v), "selected": v in selected} for v in values[:120]]
        if selected:
            qs = qs.filter(**{f"{expr}__in": selected})
        facet_filters.append(
            {
                "param": param,
                "label": spec["label"],
                "options": options,
                "selected_count": len(selected),
            }
        )

    return qs, facet_filters


def admin_list(request, model_slug):
    unauthorized = _require_module_permission(request, model_slug, "view")
    if unauthorized:
        return unauthorized

    _purge_expired_trash()

    pref = _admin_pref_context(request)
    lang = pref["admin_lang"]

    model = _resolve_model(model_slug)
    query = request.GET.get("q", "").strip()
    filter_field = request.GET.get("f", "").strip()
    status_filters = [
        value
        for value in request.GET.getlist("status")
        if value in {"pending", "confirmed", "shipping", "delivered", "done", "cancelled"}
    ]
    status_filter = status_filters[0] if len(status_filters) == 1 else ""
    qs = model.objects.all().order_by("-pk")
    if model_slug == "danh-gia-cua-hang":
        qs = qs.select_related("cua_hang", "user").prefetch_related("tep_dinh_kem")
    qs, facet_filters = _build_and_apply_facets(request, model_slug, qs, model)

    order_summary = None
    if model_slug == ORDER_ITEM_MODULE_SLUG:
        order_id = (request.GET.get("order") or "").strip()
        if order_id.isdigit():
            order_summary = (
                DonHang.objects.select_related("khach_hang", "cua_hang_xu_ly", "khuyen_mai")
                .filter(pk=int(order_id))
                .first()
            )
    if model_slug == ORDER_MODULE_SLUG and status_filters:
        selected_statuses = set(status_filters)
        final_statuses = set()
        if "done" in selected_statuses:
            final_statuses.update({"done", "delivered"})
        if "delivered" in selected_statuses:
            final_statuses.add("delivered")
        final_statuses.update(selected_statuses - {"done", "delivered"})
        qs = qs.filter(trang_thai__in=sorted(final_statuses))
    if query:
        valid_fields = {
            f.name
            for f in model._meta.fields
            if f.name != "id" and f.get_internal_type() not in {"ImageField", "FileField"}
        }
        if filter_field and filter_field not in valid_fields:
            filter_field = ""
        if filter_field:
            field_obj = model._meta.get_field(filter_field)
            field_type = field_obj.get_internal_type()
            if field_type in {"CharField", "TextField", "EmailField", "SlugField"}:
                qs = qs.filter(**{f"{filter_field}__icontains": query})
            elif field_type in {
                "IntegerField",
                "PositiveIntegerField",
                "BigIntegerField",
                "AutoField",
                "BigAutoField",
                "SmallIntegerField",
                "PositiveSmallIntegerField",
            }:
                try:
                    qs = qs.filter(**{filter_field: int(query)})
                except Exception:
                    qs = qs.none()
            elif field_type in {"DecimalField", "FloatField"}:
                try:
                    qs = qs.filter(**{filter_field: Decimal(query)})
                except Exception:
                    qs = qs.none()
            elif field_type == "BooleanField":
                truthy = {"1", "true", "yes", "on", "có", "co"}
                falsy = {"0", "false", "no", "off", "không", "khong"}
                q_lower = query.lower()
                if q_lower in truthy:
                    qs = qs.filter(**{filter_field: True})
                elif q_lower in falsy:
                    qs = qs.filter(**{filter_field: False})
                else:
                    qs = qs.none()
            elif field_type in {"DateField", "DateTimeField"}:
                dt_value = parse_datetime(query) or parse_date(query)
                if dt_value:
                    qs = qs.filter(**{filter_field: dt_value})
                else:
                    qs = qs.none()
            else:
                qs = qs.none()
        else:
            text_fields = [f.name for f in model._meta.fields if f.get_internal_type() in {"CharField", "TextField"}]
            if text_fields:
                from django.db.models import Q

                conditions = Q()
                for field_name in text_fields:
                    conditions |= Q(**{f"{field_name}__icontains": query})
                qs = qs.filter(conditions)

    if model_slug == "san-pham":
        qs = qs.annotate(
            store_stock_total=Coalesce(
                Sum("ton_kho_theo_cua_hang__ton_kho", distinct=True),
                0,
            )
        )

    fields = [
        {"name": f.name, "verbose_name": _field_label(f, lang), "type": f.get_internal_type()}
        for f in model._meta.fields
        if f.name != "id"
    ]
    compact_detail_mode = model_slug in {ORDER_MODULE_SLUG, "giao-dich-kho", "danh-gia-cua-hang"}
    compact_primary_field_names = []
    if compact_detail_mode:
        if model_slug == ORDER_MODULE_SLUG:
            preferred_names = [
                "khach_hang",
                "ho_ten_nguoi_nhan",
                "trang_thai",
                "trang_thai_thanh_toan",
                "tong_tien",
                "phuong_thuc_thanh_toan",
                "created_at",
            ]
        elif model_slug == "giao-dich-kho":
            preferred_names = [
                "san_pham",
                "cua_hang",
                "nhan_vien",
                "loai",
                "so_luong",
                "ton_truoc",
                "ton_sau",
                "created_at",
            ]
        elif model_slug == "danh-gia-cua-hang":
            preferred_names = [
                "cua_hang",
                "user",
                "so_sao",
                "created_at",
            ]
        else:
            preferred_names = [
                "khach_hang",
                "ho_ten_nguoi_nhan",
                "trang_thai",
                "trang_thai_thanh_toan",
                "tong_tien",
                "cua_hang_xu_ly",
            ]
        field_names = [field["name"] for field in fields]
        compact_primary_field_names = [name for name in preferred_names if name in field_names]
        if not compact_primary_field_names:
            compact_primary_field_names = field_names[: min(5, len(field_names))]
    display_fields = [
        field for field in fields if (not compact_detail_mode or field["name"] in compact_primary_field_names)
    ]
    filter_fields = [
        {"name": f["name"], "verbose_name": f["verbose_name"]}
        for f in fields
        if f["type"] not in {"ImageField", "FileField"}
    ]
    paginator = Paginator(qs, 15)
    page_obj = paginator.get_page(request.GET.get("page"))
    persisted_params = []
    for key in request.GET.keys():
        if key == "page":
            continue
        for value in request.GET.getlist(key):
            if value != "":
                persisted_params.append((key, value))
    persisted_query = urlencode(persisted_params, doseq=True)

    can_create = _has_module_access(request.user, model_slug, "create")
    if model_slug == "danh-gia-cua-hang":
        can_create = False
    can_update = _has_module_access(request.user, model_slug, "update")
    can_delete = _has_module_access(request.user, model_slug, "delete")
    can_change_order_status = _has_module_access(request.user, model_slug, "status")
    can_change_payment_status = _has_module_access(request.user, model_slug, "payment_status")
    can_print_inventory = _has_module_access(request.user, model_slug, "print")

    rows = []
    for item in page_obj.object_list:
        values = []
        for field in fields:
            raw_value = getattr(item, field["name"])
            field_obj = model._meta.get_field(field["name"])
            field_type = field_obj.get_internal_type()
            if field_type in {"ImageField", "FileField"}:
                if raw_value:
                    try:
                        cell_type = "image"
                        if model_slug == "giao-dich-kho" and field["name"] == "chu_ky":
                            cell_type = "signature"
                        values.append({"type": cell_type, "url": raw_value.url, "text": str(raw_value)})
                    except Exception:
                        values.append({"type": "text", "text": str(raw_value)})
                else:
                    values.append({"type": "text", "text": ""})
            elif model_slug == "cua-hang" and field["name"] == "hoat_dong_24h":
                values.append({"type": "toggle_24h", "value": bool(raw_value)})
            elif model_slug == "gop-y-khach-hang" and field["name"] == "da_phan_hoi":
                values.append(
                    {
                        "type": "status",
                        "value": "feedback_done" if bool(raw_value) else "feedback_pending",
                        "text": "Đã phản hồi" if bool(raw_value) else "Chưa phản hồi",
                    }
                )
            elif field_type == "BooleanField":
                values.append({"type": "bool", "value": bool(raw_value)})
            elif field["name"] in {"trang_thai"}:
                display = str(raw_value)
                try:
                    display = getattr(item, f"get_{field['name']}_display")()
                except Exception:
                    pass
                values.append({"type": "status", "value": str(raw_value), "text": display})
            elif model_slug == ORDER_MODULE_SLUG and field["name"] == "trang_thai_thanh_toan":
                display = str(raw_value)
                try:
                    display = item.get_trang_thai_thanh_toan_display()
                except Exception:
                    pass
                values.append({"type": "status", "value": f"pay_{raw_value}", "text": display})
            elif field["name"] in {"gia_ban", "tong_tien", "don_gia"}:
                values.append({"type": "money", "text": _format_currency(raw_value)})
            elif model_slug == "danh-gia-cua-hang" and field["name"] == "so_sao":
                star_value = int(raw_value or 0)
                values.append(
                    {
                        "type": "stock_move",
                        "level": "import" if star_value >= 4 else ("low" if star_value == 3 else "export"),
                        "text": f"{star_value} sao",
                    }
                )
            elif model_slug == ORDER_MODULE_SLUG and field["name"] == "giam_gia":
                values.append({"type": "money", "text": _format_currency(raw_value)})
            elif model_slug == ORDER_MODULE_SLUG and field["name"] == "ma_voucher_ap_dung":
                values.append(
                    {
                        "type": "stock_move",
                        "level": "import" if raw_value else "export",
                        "text": str(raw_value) if raw_value else "Không áp dụng",
                    }
                )
            elif model_slug == ORDER_MODULE_SLUG and field["name"] == "phuong_thuc_thanh_toan":
                display = str(raw_value)
                try:
                    display = item.get_phuong_thuc_thanh_toan_display()
                except Exception:
                    pass
                level = "info"
                if raw_value == "cod":
                    level = "export"
                elif raw_value == "bank_transfer":
                    level = "import"
                elif raw_value == "momo":
                    level = "low"
                values.append({"type": "stock_move", "level": level, "text": display})
            elif model_slug == ORDER_MODULE_SLUG and field["name"] in {"vi_do_giao_hang", "kinh_do_giao_hang"}:
                if raw_value is None:
                    values.append({"type": "text", "text": "-"})
                else:
                    values.append({"type": "text", "text": f"{float(raw_value):.6f}"})
            elif model_slug == "san-pham" and field["name"] == "ton_kho":
                stock_value = int(getattr(item, "store_stock_total", raw_value) or 0)
                if stock_value <= 0:
                    values.append({"type": "stock", "level": "out", "text": "Hết hàng"})
                elif stock_value <= SanPham.LOW_STOCK_THRESHOLD:
                    values.append({"type": "stock", "level": "low", "text": f"Sắp hết ({stock_value})"})
                else:
                    values.append({"type": "stock", "level": "ok", "text": f"Còn {stock_value}"})
            elif model_slug == "giao-dich-kho" and field["name"] == "loai":
                values.append(
                    {
                        "type": "stock_move",
                        "level": "import" if raw_value == "import" else "export",
                        "text": u("Nh\u1eadp kho") if raw_value == "import" else u("Xu\u1ea5t kho"),
                    }
                )
            elif field_type == "DateTimeField":
                if raw_value:
                    try:
                        local_dt = timezone.localtime(raw_value)
                        values.append({"type": "text", "text": local_dt.strftime("%d/%m/%Y %H:%M:%S")})
                    except Exception:
                        values.append({"type": "text", "text": _strip_parenthetical_text(raw_value)})
                else:
                    values.append({"type": "text", "text": "-"})
            elif field_type == "DateField":
                if raw_value:
                    try:
                        values.append({"type": "text", "text": raw_value.strftime("%d/%m/%Y")})
                    except Exception:
                        values.append({"type": "text", "text": _strip_parenthetical_text(raw_value)})
                else:
                    values.append({"type": "text", "text": "-"})
            else:
                values.append({"type": "text", "text": _strip_parenthetical_text(raw_value)})
            row = {
            "object": item,
            "values": values,
            "can_edit": can_update,
            "can_delete": can_delete,
            "can_change_status": can_change_order_status,
            "can_change_payment_status": can_change_payment_status,
            "can_review_receipt": False,
        }
        if model_slug == ORDER_MODULE_SLUG:
            status_actions = []
            payment_actions = []
            receipt_actions = []
            if can_change_order_status and item.trang_thai == "pending":
                status_actions.append({"value": "confirmed", "label": pref["t"]["confirm_order"]})
                status_actions.append({"value": "cancelled", "label": pref["t"]["cancel_order"]})
            elif can_change_order_status and item.trang_thai == "confirmed":
                status_actions.append({"value": "shipping", "label": pref["t"]["ship_order"]})
                status_actions.append({"value": "cancelled", "label": pref["t"]["cancel_order"]})
            elif can_change_order_status and item.trang_thai == "shipping":
                status_actions.append({"value": "delivered", "label": pref["t"]["deliver_order"]})
                status_actions.append({"value": "cancelled", "label": pref["t"]["cancel_order"]})
            elif item.trang_thai == "delivered":
                status_actions.append({"value": "done", "label": pref["t"]["complete_order"]})
            row["status_actions"] = status_actions
            if can_change_payment_status and item.trang_thai_thanh_toan == "unpaid":
                payment_actions.append({"value": "paid", "label": "Đánh dấu đã thanh toán"})
                if item.phuong_thuc_thanh_toan == "bank_transfer":
                    payment_actions.append({"value": "awaiting_confirmation", "label": "Chờ xác nhận CK"})
            elif can_change_payment_status and item.trang_thai_thanh_toan == "awaiting_confirmation":
                payment_actions.append({"value": "paid", "label": "Xác nhận đã nhận tiền"})
                payment_actions.append({"value": "unpaid", "label": "Trả về chưa thanh toán"})
            elif can_change_payment_status and item.trang_thai_thanh_toan == "paid":
                payment_actions.append({"value": "refunded", "label": "Hoàn tiền"})
            row["payment_actions"] = payment_actions
            if (
                can_change_payment_status
                and item.phuong_thuc_thanh_toan == "bank_transfer"
                and bool(item.anh_bien_lai)
                and item.trang_thai_thanh_toan in {"awaiting_confirmation", "unpaid"}
            ):
                receipt_actions = [
                    {"value": "approve", "label": "Duyệt biên lai"},
                    {"value": "reject", "label": "Từ chối biên lai"},
                ]
                row["receipt_preview_url"] = item.anh_bien_lai.url
            row["receipt_actions"] = receipt_actions
            row["can_review_receipt"] = bool(receipt_actions)
            row["order_items_url"] = (
                f"{reverse('store:admin_list', kwargs={'model_slug': ORDER_ITEM_MODULE_SLUG})}?order={item.pk}"
            )
        if model_slug == "giao-dich-kho" and can_print_inventory and item.loai == "import":
            row["print_url"] = reverse("store:admin_inventory_print", args=[item.pk])
            row["pdf_url"] = reverse("store:admin_inventory_pdf", args=[item.pk])
        if (
            model_slug == ORDER_MODULE_SLUG
            and item.vi_do_giao_hang is not None
            and item.kinh_do_giao_hang is not None
        ):
            row["map_url"] = (
                f"{reverse('store:map_page')}?"
                f"center_lat={float(item.vi_do_giao_hang):.6f}"
                f"&center_lon={float(item.kinh_do_giao_hang):.6f}"
            )
        if compact_detail_mode:
            detail_allowlist = None
            if model_slug == "giao-dich-kho":
                detail_allowlist = {
                    "don_hang",
                    "ghi_chu",
                    "chu_ky",
                    "signed_at",
                    "signed_by",
                    "signed_ip",
                    "otp_recipient_email",
                }
            elif model_slug == "danh-gia-cua-hang":
                detail_allowlist = {
                    "binh_luan",
                    "updated_at",
                }
            compact_values = []
            detail_values = []
            for field_meta, cell in zip(fields, values):
                cell_type = cell.get("type", "text")
                text_value = cell.get("text", "")
                if cell_type == "bool":
                    text_value = "Có" if cell.get("value") else "Không"
                elif cell_type in {"image", "signature"}:
                    text_value = cell.get("url") or text_value or "Co tep dinh kem"
                elif not text_value:
                    text_value = "-"
                payload = {
                    "field_name": field_meta["name"],
                    "label": field_meta["verbose_name"],
                    "text": text_value,
                    "type": cell_type,
                    "url": cell.get("url", ""),
                }
                if field_meta["name"] in compact_primary_field_names:
                    compact_values.append(cell)
                else:
                    if detail_allowlist is not None and field_meta["name"] not in detail_allowlist:
                        continue
                    if text_value in {"", "-"}:
                        continue
                    detail_values.append(payload)

            if model_slug == ORDER_ITEM_MODULE_SLUG:
                try:
                    line_total = (item.don_gia or Decimal("0")) * (item.so_luong or 0)
                except Exception:
                    line_total = None
                if line_total is not None:
                    detail_values.append(
                        {
                            "label": "Thành tiền",
                            "text": _format_currency(line_total),
                            "type": "money",
                            "url": "",
                        }
                    )
            elif model_slug == "danh-gia-cua-hang":
                media_items = _build_review_media_context(item)
                if media_items:
                    detail_values.append(
                        {
                            "label": "Ảnh / video",
                            "text": f"{len(media_items)} tệp đính kèm",
                            "type": "media_gallery",
                            "url": "",
                            "items": media_items,
                        }
                    )
            row["values"] = compact_values
            row["detail_values"] = detail_values
            if model_slug == "giao-dich-kho":
                row["title_text"] = f"Mã phiếu: {item.pk}"
            elif model_slug == "danh-gia-cua-hang":
                row["title_text"] = f"Đánh giá #{item.pk}"
            elif model_slug == ORDER_ITEM_MODULE_SLUG:
                row["title_text"] = f"Mã chi tiết: {item.pk}"
            else:
                row["title_text"] = f"Mã đơn: {item.pk}"
        rows.append(row)

    return render(
        request,
        "admin/change_list.html",
        {
            "modules": _menu_context(lang, request.user),
            "model_slug": model_slug,
            "model_name": _model_label(model_slug, lang, plural=True),
            "fields": fields,
            "display_fields": display_fields,
            "compact_detail_mode": compact_detail_mode,
            "filter_fields": filter_fields,
            "rows": rows,
            "query": query,
            "filter_field": filter_field,
            "status_filter": status_filter,
            "status_filters": status_filters,
            "page_obj": page_obj,
            "paginator": paginator,
            "facet_filters": facet_filters,
            "persisted_query": persisted_query,
            "show_create": can_create,
            "order_module_slug": ORDER_MODULE_SLUG,
            "order_summary": order_summary,
            **pref,
        },
    )


def admin_create(request, model_slug):
    unauthorized = _require_module_permission(request, model_slug, "create")
    if unauthorized:
        return unauthorized

    pref = _admin_pref_context(request)
    lang = pref["admin_lang"]

    model = _resolve_model(model_slug)
    form_cls = _admin_form_class_for_model(model_slug, model)
    coord_picker_enabled = model_slug == "cua-hang"
    if request.method == "POST":
        form = form_cls(request.POST, request.FILES)
        if model_slug == "giao-dich-kho":
            _apply_giao_dich_kho_hidden_fields(form)
            audit_reason = (request.POST.get("audit_reason") or "").strip()
            if not audit_reason:
                form.add_error(None, "Vui lòng nhập lý do điều chỉnh tồn kho.")
        form = _sanitize_admin_form(form)
        valid = _validate_coord_from_map(request, form) if coord_picker_enabled else form.is_valid()
        if valid:
            obj = form.save(commit=False) if model_slug == "giao-dich-kho" else form.save()
            if model_slug == "giao-dich-kho":
                audit_reason = (request.POST.get("audit_reason") or "").strip()
                obj.created_by = request.user
                obj.save()
                _apply_signature_log(obj, request)
                _log_stock_audit(request, obj, "create", audit_reason)
                if obj.loai == "import" and obj.nhan_vien_id and not obj.otp_verified_at:
                    _issue_inventory_otp(request, obj)
            if model_slug == "san-pham":
                _save_product_gallery(obj, request.FILES, request.POST)
            messages.success(request, pref["t"]["saved_successfully"])
            return redirect("store:admin_list", model_slug=model_slug)
    else:
        form = form_cls()
        if model_slug == "giao-dich-kho":
            _apply_giao_dich_kho_hidden_fields(form)
        form = _sanitize_admin_form(form)

    return render(
        request,
        "admin/change_form.html",
        {
            "modules": _menu_context(lang, request.user),
            "form": form,
            "model_slug": model_slug,
            "model_name": _model_label(model_slug, lang, plural=False),
            "mode": "create",
            "file_previews": _build_product_image_preview_context() if model_slug == "san-pham" else _build_file_preview_context(model),
            "review_media_items": [],
            "coord_picker_enabled": coord_picker_enabled,
            **pref,
        },
    )


def admin_update(request, model_slug, pk):
    unauthorized = _require_module_permission(request, model_slug, "update")
    if unauthorized:
        return unauthorized

    pref = _admin_pref_context(request)
    lang = pref["admin_lang"]

    model = _resolve_model(model_slug)
    obj = get_object_or_404(model, pk=pk)
    previous_signature = obj.chu_ky.name if getattr(obj, "chu_ky", None) else ""
    form_cls = _admin_form_class_for_model(model_slug, model)
    coord_picker_enabled = model_slug == "cua-hang"

    if request.method == "POST":
        form = form_cls(request.POST, request.FILES, instance=obj)
        if model_slug == "giao-dich-kho":
            _apply_giao_dich_kho_hidden_fields(form)
            audit_reason = (request.POST.get("audit_reason") or "").strip()
            if not audit_reason:
                form.add_error(None, "Vui lòng nhập lý do điều chỉnh tồn kho.")
        form = _sanitize_admin_form(form)
        valid = _validate_coord_from_map(request, form, instance=obj) if coord_picker_enabled else form.is_valid()
        if valid:
            obj = form.save(commit=False) if model_slug == "giao-dich-kho" else form.save()
            if model_slug == "giao-dich-kho":
                audit_reason = (request.POST.get("audit_reason") or "").strip()
                if not obj.created_by_id:
                    obj.created_by = request.user
                obj.save()
                _apply_signature_log(obj, request, previous_name=previous_signature)
                _log_stock_audit(request, obj, "update", audit_reason)
                if obj.loai == "import" and obj.nhan_vien_id and not obj.otp_verified_at:
                    if not obj.otp_expires_at or obj.otp_expires_at < timezone.now():
                        _issue_inventory_otp(request, obj)
            if model_slug == "san-pham":
                _save_product_gallery(obj, request.FILES, request.POST)
            messages.success(request, pref["t"]["saved_successfully"])
            return redirect("store:admin_list", model_slug=model_slug)
    else:
        form = form_cls(instance=obj)
        if model_slug == "giao-dich-kho":
            _apply_giao_dich_kho_hidden_fields(form)
        form = _sanitize_admin_form(form)

    return render(
        request,
        "admin/change_form.html",
        {
            "modules": _menu_context(lang, request.user),
            "form": form,
            "model_slug": model_slug,
            "model_name": _model_label(model_slug, lang, plural=False),
            "mode": "update",
            "object": obj,
            "file_previews": _build_product_image_preview_context(obj) if model_slug == "san-pham" else _build_file_preview_context(model, obj),
            "review_media_items": _build_review_media_context(obj) if model_slug == "danh-gia-cua-hang" else [],
            "coord_picker_enabled": coord_picker_enabled,
            **pref,
        },
    )


def admin_delete(request, model_slug, pk):
    unauthorized = _require_module_permission(request, model_slug, "delete")
    if unauthorized:
        return unauthorized

    _purge_expired_trash()

    pref = _admin_pref_context(request)
    lang = pref["admin_lang"]

    model = _resolve_model(model_slug)
    obj = get_object_or_404(model, pk=pk)
    if request.method == "POST":
        try:
            original_pk = obj.pk
            trash_data = _serialize_for_trash(obj)
            if model_slug == "giao-dich-kho":
                _log_stock_audit(request, obj, "delete", "Xóa giao dịch kho")
            obj.delete()
            _move_to_trash(obj, data=trash_data, object_id=original_pk)
            messages.success(request, pref["t"]["deleted_successfully"])
        except ValidationError as exc:
            messages.error(request, "; ".join(exc.messages) or "Không thể xóa bản ghi này.")
            return redirect("store:admin_list", model_slug=model_slug)
        return redirect("store:admin_list", model_slug=model_slug)

    return render(
        request,
        "admin/delete_confirmation.html",
        {
            "modules": _menu_context(lang, request.user),
            "model_slug": model_slug,
            "model_name": _model_label(model_slug, lang, plural=False),
            "object": obj,
            **pref,
        },
    )


def admin_trash_list(request):
    unauthorized = _require_admin_permission(request, "trash")
    if unauthorized:
        return unauthorized

    _purge_expired_trash()
    pref = _admin_pref_context(request)
    lang = pref["admin_lang"]
    query = request.GET.get("q", "").strip()
    filter_field = request.GET.get("f", "").strip()

    all_rows = []
    for item in TrashRecord.objects.all():
        model_slug = _model_slug_from_label(item.model_label)
        object_id_display = str(item.object_id or "")
        if object_id_display.strip().lower() in {"none", "null"}:
            object_id_display = ""
        all_rows.append(
            {
                "id": item.pk,
                "object_id": object_id_display or "-",
                "model_name": _model_label(model_slug, lang, plural=False),
                "display_name": _trash_display_name(item.data or {}, item.model_label) or "-",
                "deleted_at": item.deleted_at,
                "expires_at": item.expires_at,
            }
        )

    fields = [
        {"name": "model_name", "verbose_name": "Module"},
        {"name": "display_name", "verbose_name": "Tên"},
        {"name": "deleted_at", "verbose_name": pref["t"]["deleted_at"]},
        {"name": "expires_at", "verbose_name": pref["t"]["expires_at"]},
    ]

    valid_fields = {f["name"] for f in fields}
    if filter_field not in valid_fields:
        filter_field = ""

    if query and filter_field:
        q_lower = query.lower()
        all_rows = [
            row
            for row in all_rows
            if q_lower in str(row.get(filter_field, "")).lower()
        ]
    elif query:
        q_lower = query.lower()
        all_rows = [
            row
            for row in all_rows
            if any(q_lower in str(row.get(name, "")).lower() for name in valid_fields)
        ]

    paginator = Paginator(all_rows, 20)
    page_obj = paginator.get_page(request.GET.get("page"))

    rows = []
    for item in page_obj.object_list:
        rows.append(
            {
                "id": item["id"],
                "object_id": item["object_id"],
                "model_name": item["model_name"],
                "display_name": item["display_name"],
                "deleted_at": item["deleted_at"],
                "expires_at": item["expires_at"],
                "restore_url": reverse("store:admin_trash_restore", args=[item["id"]]),
                "delete_url": reverse("store:admin_trash_delete", args=[item["id"]]),
            }
        )
    display_fields = fields
    compact_detail_mode = False
    return render(
        request,
        "admin/trash_list.html",
        {
            "modules": _menu_context(lang, request.user),
            "model_slug": "trash",
            "model_name": pref["t"]["trash"],
            "fields": fields,
            "display_fields": display_fields,
            "compact_detail_mode": compact_detail_mode,
            "rows": rows,
            "query": query,
            "filter_field": filter_field,
            "status_filter": "",
            "page_obj": page_obj,
            "paginator": paginator,
            "trash_retention_days": getattr(settings, "TRASH_RETENTION_DAYS", 15),
            "show_create": False,
            **pref,
        },
    )


def admin_trash_restore(request, pk):
    unauthorized = _require_admin_permission(request, "trash", "restore")
    if unauthorized:
        return unauthorized

    _purge_expired_trash()
    pref = _admin_pref_context(request)
    trash = get_object_or_404(TrashRecord, pk=pk)
    try:
        model = apps.get_model(trash.model_label)
        payload = dict(trash.data or {})
        normalized = {}
        m2m_payload = {}
        for field in model._meta.fields:
            name = field.name
            if name not in payload:
                continue
            value = payload.get(name)
            if isinstance(field, dj_models.ForeignKey):
                if value in ("", None):
                    if field.null:
                        normalized[field.attname] = None
                        continue
                    raise ValueError("missing_fk")
                if not field.remote_field.model.objects.filter(pk=value).exists():
                    if field.null:
                        normalized[field.attname] = None
                        continue
                    raise ValueError("fk_not_found")
                normalized[field.attname] = value
                continue
            field_type = field.get_internal_type()
            if field_type in {"DateTimeField"} and isinstance(value, str):
                normalized[name] = parse_datetime(value) or value
            elif field_type in {"DateField"} and isinstance(value, str):
                normalized[name] = parse_date(value) or value
            elif field_type in {"DecimalField"} and value not in (None, ""):
                normalized[name] = Decimal(str(value))
            elif field_type in {
                "IntegerField",
                "PositiveIntegerField",
                "BigIntegerField",
                "AutoField",
                "BigAutoField",
                "SmallIntegerField",
                "PositiveSmallIntegerField",
            } and value not in (None, ""):
                normalized[name] = int(value)
            elif field_type == "BooleanField":
                if isinstance(value, str):
                    normalized[name] = value.lower() in {"1", "true", "yes", "on", "có", "co"}
                else:
                    normalized[name] = bool(value)
            else:
                normalized[name] = value
        for field in model._meta.many_to_many:
            raw_values = payload.get(field.name)
            if not isinstance(raw_values, (list, tuple)):
                continue
            valid_ids = list(
                field.remote_field.model.objects.filter(pk__in=raw_values).values_list("pk", flat=True)
            )
            m2m_payload[field.name] = valid_ids

        pk_value = (trash.object_id or "").strip()
        if pk_value.lower() in {"", "none", "null"}:
            pk_value = None
        if pk_value is not None:
            pk_field = model._meta.pk
            if pk_field.get_internal_type() in {"AutoField", "BigAutoField", "IntegerField", "PositiveIntegerField"}:
                try:
                    pk_value = int(pk_value)
                except Exception:
                    pk_value = None
        instance = model(**normalized)
        if pk_value and not model.objects.filter(pk=pk_value).exists():
            instance.pk = pk_value

        if model is GiaoDichKho:
            with transaction.atomic():
                instance.full_clean()
                model.objects.bulk_create([instance])
                try:
                    sync_product_stock(instance.san_pham)
                except Exception:
                    pass
                if instance.cua_hang_id:
                    try:
                        sync_store_stock(instance.san_pham, instance.cua_hang)
                    except Exception:
                        pass
        else:
            instance.save()
            for field_name, related_ids in m2m_payload.items():
                getattr(instance, field_name).set(related_ids)
        trash.delete()
        messages.success(request, pref["t"]["saved_successfully"])
    except Exception as exc:
        detail = ""
        if isinstance(exc, ValidationError):
            detail = "; ".join(getattr(exc, "messages", []) or []) or str(exc)
        else:
            detail = str(exc)
        if getattr(settings, "DEBUG", False) and detail:
            messages.error(request, f"Không thể khôi phục bản ghi: {detail}")
        else:
            messages.error(request, "Không thể khôi phục bản ghi. Vui lòng kiểm tra dữ liệu.")
    return redirect("store:admin_trash")


def admin_trash_delete(request, pk):
    unauthorized = _require_admin_permission(request, "trash", "delete")
    if unauthorized:
        return unauthorized

    _purge_expired_trash()
    pref = _admin_pref_context(request)
    trash = get_object_or_404(TrashRecord, pk=pk)
    trash.delete()
    messages.success(request, pref["t"]["deleted_successfully"])
    return redirect("store:admin_trash")


def admin_notifications(request):
    unauthorized = _require_admin_permission(request, "notifications")
    if unauthorized:
        return unauthorized

    pref = _admin_pref_context(request)
    lang = pref["admin_lang"]
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "delete_selected":
            ids = [int(i) for i in request.POST.getlist("selected_ids") if str(i).isdigit()]
            if ids:
                Notification.objects.filter(pk__in=ids).delete()
                messages.success(request, pref["t"]["deleted_successfully"])
            else:
                messages.warning(request, "Vui lòng chọn ít nhất một thông báo.")
            return redirect("store:admin_notifications")
        if action == "mark_all_read":
            Notification.objects.filter(resolved=False).update(resolved=True)
            messages.success(request, "Đã đánh dấu tất cả thông báo là đã đọc.")
            return redirect("store:admin_notifications")
    all_notifications = list(Notification.objects.all().order_by("resolved", "-created_at"))
    notification_cards_all = [_build_notification_card(notification) for notification in all_notifications]
    active_tab = (request.GET.get("tab") or "all").strip().lower()
    valid_tabs = {"all", "order", "review", "error"}
    if active_tab not in valid_tabs:
        active_tab = "all"

    if active_tab == "all":
        filtered_cards = notification_cards_all
    else:
        filtered_cards = [card for card in notification_cards_all if card["category"] == active_tab]

    paginator = Paginator(filtered_cards, 12)
    page_obj = paginator.get_page(request.GET.get("page"))
    notification_stats = {
        "total": len(notification_cards_all),
        "unread": sum(1 for card in notification_cards_all if not card["notification"].resolved),
        "error": sum(1 for card in notification_cards_all if card["category"] == "error"),
        "info": sum(1 for card in notification_cards_all if card["notification"].level == "info"),
    }
    notification_tabs = [
        {"key": "all", "label": u("T\u1ea5t c\u1ea3"), "count": len(notification_cards_all)},
        {"key": "order", "label": u("\u0110\u01a1n h\u00e0ng"), "count": sum(1 for card in notification_cards_all if card["category"] == "order")},
        {"key": "review", "label": u("\u0110\u00e1nh gi\u00e1"), "count": sum(1 for card in notification_cards_all if card["category"] == "review")},
        {"key": "error", "label": u("L\u1ed7i h\u1ec7 th\u1ed1ng"), "count": sum(1 for card in notification_cards_all if card["category"] == "error")},
    ]
    
    return render(
        request,
        "admin/notifications.html",
        {
            "modules": _menu_context(lang, request.user),
            "page_obj": page_obj,
            "paginator": paginator,
            "notification_cards": list(page_obj.object_list),
            "notification_stats": notification_stats,
            "notification_tabs": notification_tabs,
            "active_tab": active_tab,
            **pref,
        },
    )


def admin_notification_detail(request, pk):
    unauthorized = _require_admin_permission(request, "notifications")
    if unauthorized:
        return unauthorized

    pref = _admin_pref_context(request)
    lang = pref["admin_lang"]
    notification = get_object_or_404(Notification, pk=pk)
    if not notification.resolved:
        notification.resolved = True
        notification.save(update_fields=["resolved"])

    return render(
        request,
        "admin/notification_detail.html",
        {
            "modules": _menu_context(lang, request.user),
            "notification": notification,
            **pref,
        },
    )


def admin_notification_open(request, pk):
    unauthorized = _require_admin_permission(request, "notifications")
    if unauthorized:
        return unauthorized

    notification = get_object_or_404(Notification, pk=pk)
    if not notification.resolved:
        notification.resolved = True
        notification.save(update_fields=["resolved"])

    target = _notification_target_path(notification)
    if target:
        return redirect(target)
    return redirect("store:admin_notification_detail", pk=notification.pk)


def admin_inventory_verify_otp(request, pk):
    unauthorized = _require_module_permission(request, "giao-dich-kho", "update")
    if unauthorized:
        return unauthorized

    movement = get_object_or_404(GiaoDichKho, pk=pk)
    code = (request.GET.get("code") or request.POST.get("code") or "").strip()
    if not code:
        messages.error(request, "Thiếu mã OTP.")
        return redirect("store:admin_list", model_slug="giao-dich-kho")

    if movement.otp_verified_at:
        messages.info(request, "Phiếu kho đã được xác nhận OTP.")
        return redirect("store:admin_list", model_slug="giao-dich-kho")

    if not movement.otp_code_hash or not movement.otp_expires_at:
        messages.error(request, "OTP không còn hiệu lực. Vui lòng gửi lại OTP.")
        return redirect("store:admin_list", model_slug="giao-dich-kho")

    if movement.otp_expires_at < timezone.now():
        messages.error(request, "OTP đã hết hạn. Vui lòng gửi lại OTP.")
        return redirect("store:admin_list", model_slug="giao-dich-kho")

    if not check_password(code, movement.otp_code_hash):
        messages.error(request, "OTP không đúng.")
        return redirect("store:admin_list", model_slug="giao-dich-kho")

    movement.otp_verified_at = timezone.now()
    movement.otp_verified_by = request.user if request.user.is_authenticated else None
    movement.otp_verified_ip = _client_ip(request)
    movement.otp_verified_user_agent = _client_user_agent(request)
    movement.otp_code_hash = ""
    movement.otp_expires_at = None
    movement.save(
        update_fields=[
            "otp_verified_at",
            "otp_verified_by",
            "otp_verified_ip",
            "otp_verified_user_agent",
            "otp_code_hash",
            "otp_expires_at",
        ]
    )
    _create_admin_notification(
        f"Xác nhận OTP phiếu kho #{movement.pk}",
        "OTP đã được xác nhận cho phiếu kho.",
        level="info",
        path=reverse("store:admin_list", kwargs={"model_slug": "giao-dich-kho"}),
        method="PATCH",
        status_code=200,
    )
    messages.success(request, "Đã xác nhận OTP.")
    return redirect("store:admin_list", model_slug="giao-dich-kho")


def admin_inventory_print(request, pk):
    unauthorized = _require_module_permission(request, "giao-dich-kho", "print")
    if unauthorized:
        return unauthorized

    movement = get_object_or_404(
        GiaoDichKho.objects.select_related(
            "san_pham",
            "nhan_vien",
            "nhan_vien__cua_hang",
            "nhan_vien__cua_hang__chuoi",
            "created_by",
        ),
        pk=pk,
        loai="import",
    )
    document_code = f"PNK-{movement.pk}"
    barcode_svg = ""
    qr_svg = ""
    lookup_url = request.build_absolute_uri(reverse("store:admin_inventory_print", args=[movement.pk]))
    try:
        from reportlab.graphics import renderSVG
        from reportlab.graphics.barcode import createBarcodeDrawing
        from reportlab.graphics.shapes import Drawing
        from reportlab.graphics.barcode.qr import QrCodeWidget

        barcode_svg = renderSVG.drawToString(
            createBarcodeDrawing(
                "Code128",
                value=document_code,
                barHeight=42,
                barWidth=1.1,
                humanReadable=True,
            )
        )
        if isinstance(barcode_svg, bytes):
            barcode_svg = barcode_svg.decode("utf-8")
        qr_widget = QrCodeWidget(lookup_url)
        bounds = qr_widget.getBounds()
        qr_width = bounds[2] - bounds[0]
        qr_height = bounds[3] - bounds[1]
        qr_drawing = Drawing(88, 88, transform=[88 / qr_width, 0, 0, 88 / qr_height, 0, 0])
        qr_drawing.add(qr_widget)
        qr_svg = renderSVG.drawToString(qr_drawing)
        if isinstance(qr_svg, bytes):
            qr_svg = qr_svg.decode("utf-8")
    except Exception:
        barcode_svg = ""
        qr_svg = ""

    return render(
        request,
        "admin/inventory_print.html",
        {
            "movement": movement,
            "document_code": document_code,
            "barcode_svg": barcode_svg,
            "qr_svg": qr_svg,
            "lookup_url": lookup_url,
            "generated_at": timezone.now(),
        },
    )


def admin_inventory_pdf(request, pk):
    unauthorized = _require_module_permission(request, "giao-dich-kho", "print")
    if unauthorized:
        return unauthorized

    movement = get_object_or_404(
        GiaoDichKho.objects.select_related(
            "san_pham",
            "nhan_vien",
            "nhan_vien__cua_hang",
            "created_by",
        ),
        pk=pk,
        loai="import",
    )

    try:
        from reportlab.graphics import renderPDF
        from reportlab.graphics.barcode import createBarcodeDrawing
        from reportlab.graphics.barcode.qr import QrCodeWidget
        from reportlab.graphics.shapes import Drawing
        from reportlab.lib.colors import HexColor
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.utils import ImageReader, simpleSplit
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.pdfgen import canvas
    except Exception:
        messages.error(request, "Chưa cài thư viện xuất PDF. Hãy cài reportlab để dùng tính năng này.")
        return redirect("store:admin_inventory_print", pk=movement.pk)

    def resolve_font_names():
        regular_name = "InventoryUnicode"
        bold_name = "InventoryUnicodeBold"
        registered = set(pdfmetrics.getRegisteredFontNames())
        if regular_name in registered and bold_name in registered:
            return regular_name, bold_name

        candidates = [
            ("C:\\Windows\\Fonts\\arial.ttf", "C:\\Windows\\Fonts\\arialbd.ttf"),
            ("C:\\Windows\\Fonts\\tahoma.ttf", "C:\\Windows\\Fonts\\tahomabd.ttf"),
            ("C:\\Windows\\Fonts\\segoeui.ttf", "C:\\Windows\\Fonts\\segoeuib.ttf"),
        ]
        for regular_path, bold_path in candidates:
            if not (os.path.exists(regular_path) and os.path.exists(bold_path)):
                continue
            if regular_name not in registered:
                pdfmetrics.registerFont(TTFont(regular_name, regular_path))
                registered.add(regular_name)
            if bold_name not in registered:
                pdfmetrics.registerFont(TTFont(bold_name, bold_path))
                registered.add(bold_name)
            return regular_name, bold_name
        return "Helvetica", "Helvetica-Bold"

    font_regular, font_bold = resolve_font_names()

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="phieu-nhap-kho-{movement.pk}.pdf"'

    pdf = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    margin = 40
    cursor_y = height - margin

    def line(text, x, y, font=None, size=11, color="#102a43"):
        pdf.setFillColor(HexColor(color))
        pdf.setFont(font or font_regular, size)
        pdf.drawString(x, y, text)

    def draw_block(x, y_top, w, h, *, title="", fill="#ffffff", stroke="#d9e2ec", title_color="#0f766e"):
        pdf.setStrokeColor(HexColor(stroke))
        pdf.setFillColor(HexColor(fill))
        pdf.roundRect(x, y_top - h, w, h, 14, stroke=1, fill=1)
        if title:
            line(title, x + 14, y_top - 18, font=font_bold, size=11, color=title_color)

    def draw_label_value(x, y, label, value, *, value_font=None, value_size=11):
        line(label, x, y, font=font_bold, size=10, color="#627d98")
        wrapped = simpleSplit(str(value or "-"), value_font or font_regular, value_size, 210)
        cursor = y - 16
        for item in wrapped[:3]:
            line(item, x, cursor, font=value_font or font_regular, size=value_size, color="#102a43")
            cursor -= 14
        return cursor

    def draw_stat_card(x, y_top, w, h, label, value, *, fill="#ffffff", stroke="#d9e2ec", label_color="#627d98"):
        pdf.setStrokeColor(HexColor(stroke))
        pdf.setFillColor(HexColor(fill))
        pdf.roundRect(x, y_top - h, w, h, 12, stroke=1, fill=1)
        line(label, x + 12, y_top - 18, font=font_bold, size=9, color=label_color)
        line(str(value), x + 12, y_top - 40, font=font_bold, size=18, color="#102a43")

    pdf.setTitle(f"Phiếu nhập kho #{movement.pk}")
    document_code = f"PNK-{movement.pk}"
    lookup_url = request.build_absolute_uri(reverse("store:admin_inventory_print", args=[movement.pk]))

    header_height = 88
    pdf.setFillColor(HexColor("#0f766e"))
    pdf.roundRect(margin, cursor_y - header_height, width - (margin * 2), header_height, 18, stroke=0, fill=1)
    line("SMARTGIS", margin + 18, cursor_y - 28, font=font_bold, size=24, color="#ffffff")
    line("PHIẾU NHẬP KHO NỘI BỘ", margin + 18, cursor_y - 50, font=font_bold, size=12, color="#d1fae5")
    line(f"Số phiếu: {document_code}", width - 180, cursor_y - 28, font=font_bold, size=13, color="#ffffff")
    line(f"Ngày in: {timezone.now().strftime('%d/%m/%Y %H:%M')}", width - 180, cursor_y - 48, size=10, color="#d1fae5")
    cursor_y -= header_height + 20

    draw_block(margin, cursor_y, width - (margin * 2), 120, title="Thông tin chung", fill="#f8fbfc")
    left_x = margin + 16
    right_x = margin + 280
    left_cursor = draw_label_value(left_x, cursor_y - 38, "Sản phẩm", movement.san_pham.ten, value_font=font_bold, value_size=12)
    left_cursor = draw_label_value(left_x, left_cursor - 4, "Nhân viên ký", movement.nhan_vien.ho_ten if movement.nhan_vien else "-")
    store_name = movement.cua_hang.ten if movement.cua_hang else (
        movement.nhan_vien.cua_hang.ten if movement.nhan_vien and movement.nhan_vien.cua_hang else "-"
    )
    draw_label_value(left_x, left_cursor - 4, "Cửa hàng", store_name)
    right_cursor = draw_label_value(right_x, cursor_y - 38, "Người tạo", movement.created_by.username if movement.created_by else "-")
    right_cursor = draw_label_value(right_x, right_cursor - 4, "Thời gian tạo", movement.created_at.strftime("%d/%m/%Y %H:%M"))
    draw_label_value(right_x, right_cursor - 4, "Loại giao dịch", "Nhập kho")
    cursor_y -= 140

    draw_block(margin, cursor_y, width - (margin * 2), 86, title="Tổng hợp số liệu", fill="#fff7ed", stroke="#fdba74", title_color="#c2410c")
    card_y = cursor_y - 28
    card_w = (width - (margin * 2) - 36) / 4
    draw_stat_card(margin + 16, card_y, card_w, 46, "Số lượng", movement.so_luong, fill="#ffffff", stroke="#fed7aa", label_color="#c2410c")
    draw_stat_card(margin + 16 + card_w + 12, card_y, card_w, 46, "Tồn trước", movement.ton_truoc, fill="#ffffff", stroke="#fed7aa", label_color="#c2410c")
    draw_stat_card(margin + 16 + (card_w + 12) * 2, card_y, card_w, 46, "Tồn sau", movement.ton_sau, fill="#ffffff", stroke="#fed7aa", label_color="#c2410c")
    draw_stat_card(margin + 16 + (card_w + 12) * 3, card_y, card_w, 46, "Trạng thái", "Nhập kho", fill="#ffffff", stroke="#fed7aa", label_color="#c2410c")
    cursor_y -= 106

    scan_block_height = 140
    draw_block(margin, cursor_y, width - (margin * 2), scan_block_height, title="Mã tra cứu", fill="#f8fbfc")
    line("Sử dụng mã này hoặc QR để mở nhanh phiếu nhập kho.", margin + 16, cursor_y - 34, size=10, color="#627d98")
    barcode_box_x = margin + 16
    barcode_box_y = cursor_y - 122
    pdf.setStrokeColor(HexColor("#d9e2ec"))
    pdf.roundRect(barcode_box_x, barcode_box_y, 240, 78, 12, stroke=1, fill=0)
    try:
        barcode = createBarcodeDrawing(
            "Code128",
            value=document_code,
            barHeight=28,
            barWidth=1.05,
            humanReadable=True,
        )
        renderPDF.draw(barcode, pdf, barcode_box_x + 8, barcode_box_y + 12)
    except Exception:
        line(document_code, barcode_box_x + 12, barcode_box_y + 36, font=font_bold, size=14, color="#0f172a")
    line(document_code, barcode_box_x + 12, barcode_box_y + 8, size=9, color="#334e68")

    qr_box_x = margin + 280
    qr_box_y = cursor_y - 122
    pdf.roundRect(qr_box_x, qr_box_y, width - margin - qr_box_x, 78, 12, stroke=1, fill=0)
    try:
        qr_widget = QrCodeWidget(lookup_url)
        bounds = qr_widget.getBounds()
        qr_width = bounds[2] - bounds[0]
        qr_height = bounds[3] - bounds[1]
        qr_drawing = Drawing(68, 68, transform=[68 / qr_width, 0, 0, 68 / qr_height, 0, 0])
        qr_drawing.add(qr_widget)
        renderPDF.draw(qr_drawing, pdf, qr_box_x + 10, qr_box_y + 6)
    except Exception:
        line("Không tạo được QR", qr_box_x + 14, qr_box_y + 40, size=9, color="#9b1c1c")
    wrapped_lookup = simpleSplit(lookup_url, font_regular, 9, width - margin - qr_box_x - 90)
    qr_text_y = qr_box_y + 52
    for lookup_line in wrapped_lookup[:2]:
        line(lookup_line, qr_box_x + 88, qr_text_y, size=9, color="#334e68")
        qr_text_y -= 12
    cursor_y -= scan_block_height + 18

    note_height = 90
    draw_block(margin, cursor_y, width - (margin * 2), note_height, title="Ghi chú", fill="#fbfdff")
    note = (movement.ghi_chu or "Không có ghi chú.").strip()
    note_lines = simpleSplit(note, font_regular, 11, width - (margin * 2) - 32)
    note_y = cursor_y - 36
    for note_line in note_lines[:4]:
        line(note_line, margin + 16, note_y, size=11)
        note_y -= 15
    cursor_y -= note_height + 18

    signature_top = cursor_y
    draw_block(margin, signature_top, 250, 150, title="Chữ ký nhân viên", fill="#fcfdff")
    pdf.roundRect(margin + 16, signature_top - 128, 218, 90, 10, stroke=1, fill=0)
    if movement.chu_ky:
        try:
            signature = ImageReader(movement.chu_ky.path)
            pdf.drawImage(signature, margin + 24, signature_top - 120, width=200, height=74, preserveAspectRatio=True, mask="auto")
        except Exception:
            line("Không thể tải ảnh chữ ký", margin + 28, signature_top - 82, size=10, color="#9b1c1c")
    else:
        line("Chưa có chữ ký", margin + 28, signature_top - 82, size=10, color="#627d98")

    draw_block(margin + 268, signature_top, width - margin - (margin + 268), 150, title="Xác nhận", fill="#f8fafc")
    line("Nhân viên ký", margin + 286, signature_top - 48, font=font_bold, size=11, color="#334e68")
    line(movement.nhan_vien.ho_ten if movement.nhan_vien else "-", margin + 286, signature_top - 66, size=11)
    line("Người lập phiếu", margin + 286, signature_top - 96, font=font_bold, size=11, color="#334e68")
    line(movement.created_by.username if movement.created_by else "-", margin + 286, signature_top - 114, size=11)

    line("Chứng từ được tạo từ hệ thống SmartGIS.", margin, 32, size=9, color="#627d98")
    line("Vui lòng đối chiếu thông tin hàng hóa và lưu kèm chữ ký khi cần.", width - 255, 32, size=9, color="#627d98")

    pdf.showPage()
    pdf.save()
    return response


@never_cache
def user_dashboard(request):
    unauthorized = _require_regular_user(request)
    if unauthorized:
        return unauthorized
    _refresh_authenticated_user(request)
    return redirect("store:user_profile")


@never_cache
def user_profile(request):
    unauthorized = _require_regular_user(request)
    if unauthorized:
        return unauthorized

    _refresh_authenticated_user(request)
    pref = _admin_pref_context(request)
    profile = _get_customer_profile(request.user)
    profile_extra = _user_profile_extra_state(request)

    if request.method == "POST":
        full_name = (request.POST.get("full_name") or "").strip()
        email_input = (request.POST.get("email") or "").strip()
        email, email_error = _clean_user_email(email_input, exclude_user_id=request.user.pk)
        gender = (request.POST.get("gender") or "other").strip()
        birth_date = (request.POST.get("birth_date") or "").strip()
        avatar_file = request.FILES.get("avatar")
        avatar_error = None

        if avatar_file:
            allowed_types = {"image/jpeg", "image/png"}
            if avatar_file.size > 1024 * 1024:
                avatar_error = "Ảnh đại diện phải nhỏ hơn hoặc bằng 1 MB."
            elif getattr(avatar_file, "content_type", "") not in allowed_types:
                avatar_error = "Ảnh đại diện chỉ hỗ trợ định dạng JPEG hoặc PNG."
            else:
                try:
                    get_image_dimensions(avatar_file)
                    avatar_file.seek(0)
                except Exception:
                    avatar_error = "File tải lên không phải là ảnh hợp lệ."

        if email_error:
            messages.error(request, email_error)
        elif avatar_error:
            messages.error(request, avatar_error)
        else:
            old_avatar = profile.avatar if avatar_file and profile.avatar else None
            if full_name:
                request.user.first_name = full_name
                request.user.last_name = ""
            request.user.email = email
            request.user.save(update_fields=["email", "first_name", "last_name"])
            if avatar_file:
                profile.avatar = avatar_file
                profile.save(update_fields=["avatar"])
                if old_avatar and old_avatar.name != profile.avatar.name:
                    old_avatar.delete(save=False)
            if gender not in {"male", "female", "other"}:
                gender = "other"
            _save_user_profile_extra_state(
                request,
                {
                    "gender": gender,
                    "birth_date": birth_date,
                },
            )
            messages.success(request, pref["t"]["profile_saved"])
            return redirect("store:user_profile")

    return render(
        request,
        "user/profile.html",
        {
            **_user_shell_context(
                request,
                section="account",
                subsection="profile",
                account_subsection="profile",
                page_title="Hồ sơ của tôi",
            ),
            "profile": profile,
            "profile_extra": profile_extra,
            **pref,
        },
    )


@never_cache
def user_address(request):
    unauthorized = _require_regular_user(request)
    if unauthorized:
        return unauthorized

    _refresh_authenticated_user(request)
    pref = _admin_pref_context(request)
    profile = _get_customer_profile(request.user)
    addresses = list(_customer_addresses_qs(request.user))
    edit_pk = request.GET.get("edit")
    editing_address = None
    if edit_pk and str(edit_pk).isdigit():
        editing_address = next((item for item in addresses if item.pk == int(edit_pk)), None)

    if request.method == "POST":
        action = (request.POST.get("action") or "create").strip()
        address_id = request.POST.get("address_id")

        if action == "delete" and address_id and str(address_id).isdigit():
            deleting_address = get_object_or_404(DiaChiKhachHang, pk=int(address_id), user=request.user)
            deleting_address.delete()
            _normalize_customer_address_defaults(request.user)
            messages.success(request, "Đã xóa địa chỉ.")
            return redirect("store:user_address")

        if action == "set_default" and address_id and str(address_id).isdigit():
            default_address = get_object_or_404(DiaChiKhachHang, pk=int(address_id), user=request.user)
            DiaChiKhachHang.objects.filter(user=request.user).update(mac_dinh=False)
            default_address.mac_dinh = True
            default_address.save(update_fields=["mac_dinh"])
            _sync_legacy_profile_address(request.user)
            messages.success(request, "Đã đặt địa chỉ mặc định.")
            return redirect("store:user_address")

        ho_ten_nguoi_nhan = (request.POST.get("ho_ten_nguoi_nhan") or "").strip()
        so_dien_thoai = (request.POST.get("so_dien_thoai") or "").strip()
        tinh_thanh = (request.POST.get("tinh_thanh") or "").strip()
        quan_huyen = (request.POST.get("quan_huyen") or "").strip()
        phuong_xa = (request.POST.get("phuong_xa") or "").strip()
        dia_chi_cu_the = (request.POST.get("dia_chi_cu_the") or "").strip()
        raw_vi_do = (request.POST.get("vi_do") or "").strip()
        raw_kinh_do = (request.POST.get("kinh_do") or "").strip()
        loai_dia_chi = (request.POST.get("loai_dia_chi") or "home").strip()
        mac_dinh = request.POST.get("mac_dinh") == "on"
        try:
            vi_do = _parse_latitude(raw_vi_do)
            kinh_do = _parse_longitude(raw_kinh_do)
        except ValidationError as exc:
            for error in exc.messages:
                messages.error(request, error)
            vi_do = None
            kinh_do = None
            errors = ["invalid_coords"]
        else:
            errors = []

        if not ho_ten_nguoi_nhan:
            errors.append("Vui lòng nhập họ tên người nhận.")
        if not so_dien_thoai:
            errors.append("Vui lòng nhập số điện thoại.")
        if not dia_chi_cu_the:
            errors.append("Vui lòng nhập địa chỉ cụ thể.")
        if (vi_do is None) ^ (kinh_do is None):
            errors.append("Vui lòng ghim đủ tọa độ trên bản đồ hoặc dùng nút tìm theo địa chỉ.")
        if loai_dia_chi not in dict(DiaChiKhachHang.LOAI_DIA_CHI_CHOICES):
            loai_dia_chi = "home"

        if errors:
            for error in errors:
                if error != "invalid_coords":
                    messages.error(request, error)
            editing_address = None
            if address_id and str(address_id).isdigit():
                editing_address = get_object_or_404(DiaChiKhachHang, pk=int(address_id), user=request.user)
            addresses = list(_customer_addresses_qs(request.user))
            form_state = {
                "pk": editing_address.pk if editing_address else "",
                "ho_ten_nguoi_nhan": ho_ten_nguoi_nhan,
                "so_dien_thoai": so_dien_thoai,
                "tinh_thanh": tinh_thanh,
                "quan_huyen": quan_huyen,
                "phuong_xa": phuong_xa,
                "dia_chi_cu_the": dia_chi_cu_the,
                "vi_do": raw_vi_do,
                "kinh_do": raw_kinh_do,
                "loai_dia_chi": loai_dia_chi,
                "mac_dinh": mac_dinh,
            }
            return render(
                request,
                "user/address.html",
                {
                    "profile": profile,
                    "display_name": _user_display_name(request.user),
                    "cart_total_quantity": _cart_items(request)[1],
                    "addresses": addresses,
                    "editing_address": editing_address,
                    "show_form": True,
                    "form_state": form_state,
                    "user_notifications": _user_header_notifications(request.user),
                    **pref,
                },
            )

        if action == "update" and address_id and str(address_id).isdigit():
            address_obj = get_object_or_404(DiaChiKhachHang, pk=int(address_id), user=request.user)
            success_message = "Đã cập nhật địa chỉ."
        else:
            address_obj = DiaChiKhachHang(user=request.user)
            success_message = "Đã thêm địa chỉ mới."

        address_obj.ho_ten_nguoi_nhan = ho_ten_nguoi_nhan
        address_obj.so_dien_thoai = so_dien_thoai
        address_obj.tinh_thanh = tinh_thanh
        address_obj.quan_huyen = quan_huyen
        address_obj.phuong_xa = phuong_xa
        address_obj.dia_chi_cu_the = dia_chi_cu_the
        address_obj.vi_do = vi_do
        address_obj.kinh_do = kinh_do
        address_obj.loai_dia_chi = loai_dia_chi
        address_obj.mac_dinh = mac_dinh or not addresses
        address_obj.save()

        if address_obj.mac_dinh:
            DiaChiKhachHang.objects.filter(user=request.user).exclude(pk=address_obj.pk).update(mac_dinh=False)
        _normalize_customer_address_defaults(request.user, target=address_obj if address_obj.mac_dinh else None)
        messages.success(request, success_message)
        return redirect("store:user_address")

    default_address = _get_default_customer_address(request.user)
    form_state = {
        "pk": editing_address.pk if editing_address else "",
        "ho_ten_nguoi_nhan": editing_address.ho_ten_nguoi_nhan if editing_address else _user_display_name(request.user),
        "so_dien_thoai": editing_address.so_dien_thoai if editing_address else (profile.so_dien_thoai or ""),
        "tinh_thanh": editing_address.tinh_thanh if editing_address else "",
        "quan_huyen": editing_address.quan_huyen if editing_address else "",
        "phuong_xa": editing_address.phuong_xa if editing_address else "",
        "dia_chi_cu_the": editing_address.dia_chi_cu_the if editing_address else "",
        "vi_do": editing_address.vi_do if editing_address and editing_address.vi_do is not None else "",
        "kinh_do": editing_address.kinh_do if editing_address and editing_address.kinh_do is not None else "",
        "loai_dia_chi": editing_address.loai_dia_chi if editing_address else "home",
        "mac_dinh": editing_address.mac_dinh if editing_address else (default_address is None),
    }

    for address in addresses:
        address.loai_dia_chi_hien_thi = _address_type_label(address)

    return render(
        request,
        "user/address.html",
        {
            **_user_shell_context(
                request,
                section="account",
                subsection="address",
                account_subsection="address",
                page_title="Địa chỉ của tôi",
            ),
            "profile": profile,
            "addresses": addresses,
            "editing_address": editing_address,
            "show_form": bool(editing_address) or not addresses or request.GET.get("new") == "1",
            "form_state": form_state,
            **pref,
        },
    )


@never_cache
def user_password_change(request):
    unauthorized = _require_regular_user(request)
    if unauthorized:
        return unauthorized

    _refresh_authenticated_user(request)
    pref = _admin_pref_context(request)
    form = PasswordChangeForm(user=request.user)
    password_strength = ""

    if request.method == "POST":
        form = PasswordChangeForm(user=request.user, data=request.POST)
        password_strength = _enforce_password_strength(form, pref)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, pref["t"]["password_updated"])
            return redirect("store:user_dashboard")

    return render(
        request,
        "user/password_form.html",
        {
            **_user_shell_context(
                request,
                section="account",
                subsection="password",
                account_subsection="password",
                page_title="Đổi mật khẩu",
            ),
            "form": form,
            "password_strength_value": password_strength,
            **pref,
        },
    )


def product_catalog(request):
    pref = _admin_pref_context(request)
    search_query = (request.GET.get("q") or "").strip()
    group_filter = (request.GET.get("group") or "").strip()
    store_filter = (request.GET.get("store") or "").strip()
    chain_filter = (request.GET.get("chain") or "").strip()

    qs = SanPham.objects.select_related("nhom_san_pham", "thuong_hieu").prefetch_related("hinh_anh_phu").order_by("ten")

    if search_query:
        qs = qs.filter(ten__icontains=search_query)

    if group_filter.isdigit():
        qs = qs.filter(nhom_san_pham_id=int(group_filter))

    if chain_filter.isdigit():
        qs = qs.filter(ton_kho_theo_cua_hang__cua_hang__chuoi_id=int(chain_filter))

    selected_store = None
    if store_filter.isdigit():
        selected_store = CuaHang.objects.select_related("chuoi").filter(pk=int(store_filter)).first()
        if selected_store:
            qs = qs.filter(ton_kho_theo_cua_hang__cua_hang=selected_store)

    qs = qs.distinct()

    group_options = list(NhomSanPham.objects.order_by("ten").values("id", "ten"))
    chain_options = list(ChuoiCuaHang.objects.order_by("ten").values("id", "ten"))

    store_qs = CuaHang.objects.select_related("chuoi").order_by("chuoi__ten", "ten")
    if chain_filter.isdigit():
        store_qs = store_qs.filter(chuoi_id=int(chain_filter))
    store_options = list(store_qs)

    paginator = Paginator(qs, 9)
    page_obj = paginator.get_page(request.GET.get("page"))
    products = list(page_obj.object_list)

    product_ids = [product.pk for product in products]
    stock_map = {}
    if products:
        if selected_store:
            stock_map = {
                row["san_pham_id"]: int(row["ton_kho"] or 0)
                for row in TonKhoCuaHang.objects.filter(
                    cua_hang=selected_store,
                    san_pham_id__in=product_ids,
                ).values("san_pham_id", "ton_kho")
            }
        else:
            stock_map = {
                row["san_pham_id"]: int(row["total_stock"] or 0)
                for row in TonKhoCuaHang.objects.filter(san_pham_id__in=product_ids)
                .values("san_pham_id")
                .annotate(total_stock=Sum("ton_kho"))
            }

    for product in products:
        product.ton_kho = int(stock_map.get(product.pk, 0) or 0)
        if product.ton_kho > 0:
            product.catalog_stock_label = f"Còn {product.ton_kho}"
            product.catalog_stock_hint = f"Còn {product.ton_kho} sản phẩm trong kho."
            product.stock_css = "in-stock"
        else:
            product.catalog_stock_label = "Hết hàng"
            product.catalog_stock_hint = "Sản phẩm đang hết hàng."
            product.stock_css = "out-stock"
        product.display_price = _format_currency(product.gia_ban)
        product.card_gallery = _build_product_card_gallery(product)

    query_params = request.GET.copy()
    query_params.pop("page", None)
    query_string = query_params.urlencode()

    _, cart_total_quantity, _ = _cart_items(request)
    return render(
        request,
        "store/product_catalog.html",
        {
            "products": products,
            "page_obj": page_obj,
            "paginator": paginator,
            "group_options": group_options,
            "chain_options": chain_options,
            "store_options": store_options,
            "selected_store": selected_store,
            "search_query": search_query,
            "selected_group": group_filter,
            "selected_chain": chain_filter,
            "selected_store_id": store_filter,
            "query_string": query_string,
            "cart_total_quantity": cart_total_quantity,
            **pref,
        },
    )


def product_detail(request, pk):
    pref = _admin_pref_context(request)
    product = get_object_or_404(
        SanPham.objects.select_related("nhom_san_pham", "thuong_hieu", "nha_cung_cap").prefetch_related("hinh_anh_phu"),
        pk=pk,
    )
    product.display_price = _format_currency(product.gia_ban)
    gallery_images = []
    if product.hinh_anh:
        gallery_images.append(
            {
                "url": product.hinh_anh.url,
                "alt": product.ten,
                "caption": product.ten,
            }
        )
    for image in product.hinh_anh_phu.all():
        if not image.hinh_anh:
            continue
        gallery_images.append(
            {
                "url": image.hinh_anh.url,
                "alt": image.chu_thich or product.ten,
                "caption": image.chu_thich,
            }
        )
    product.gallery_images = gallery_images
    _attach_stock_ui_fields(product)
    related_products = list(
        SanPham.objects.select_related("nhom_san_pham", "thuong_hieu")
        .exclude(pk=product.pk)
        .order_by("ten")[:4]
    )
    for item in related_products:
        item.display_price = _format_currency(item.gia_ban)

    selected_store_id = request.GET.get("store_id")
    selected_store_id_int = int(selected_store_id) if (selected_store_id and str(selected_store_id).isdigit()) else None

    stock_rows = list(
        TonKhoCuaHang.objects.filter(san_pham=product)
        .select_related("cua_hang__chuoi")
        .order_by("-ton_kho", "cua_hang__chuoi__ten", "cua_hang__ten")
    )
    stock_map = {row.cua_hang_id: int(row.ton_kho or 0) for row in stock_rows}
    total_store_stock = sum(stock_map.values())
    store_ids = set(stock_map.keys())
    store_ids.update(
        CuaHang.san_pham.through.objects.filter(sanpham_id=product.pk).values_list("cuahang_id", flat=True)
    )
    branch_stock = []
    if store_ids:
        stores = list(
            CuaHang.objects.select_related("chuoi")
            .filter(pk__in=store_ids)
            .order_by("chuoi__ten", "ten")
        )
        for store in stores:
            qty = int(stock_map.get(store.pk, 0) or 0)
            branch_stock.append(
                {
                    "id": store.pk,
                    "store": store,
                    "chain_name": store.chuoi.ten if store.chuoi_id else "",
                    "store_name": store.ten,
                    "district": store.quan_huyen,
                    "address": store.dia_chi,
                    "stock": qty,
                    "stock_label": "Hết hàng" if qty <= 0 else f"Còn {qty}",
                    "is_out": qty <= 0,
                }
            )
        branch_stock.sort(key=lambda item: (item["is_out"], item["chain_name"].lower(), item["store_name"].lower()))

    branch_stock_featured = sorted(
        branch_stock,
        key=lambda item: (
            item["is_out"],
            -int(item.get("stock") or 0),
            item.get("chain_name", "").lower(),
            item.get("store_name", "").lower(),
        ),
    )[:5]
    product.branch_stock = branch_stock
    product.available_store_count = sum(1 for item in branch_stock if int(item.get("stock") or 0) > 0)
    selected_store_stock = stock_map.get(selected_store_id_int, 0) if selected_store_id_int is not None else 0

    branch_stock_search = [
        {
            "id": item["id"],
            "store_name": item.get("store_name") or "",
            "chain_name": item.get("chain_name") or "",
            "district": item.get("district") or "",
            "address": item.get("address") or "",
            "stock_label": item.get("stock_label") or "",
            "is_out": bool(item.get("is_out")),
            "stock": int(item.get("stock") or 0),
        }
        for item in branch_stock
    ]

    _, cart_total_quantity, _ = _cart_items(request)
    return render(
        request,
        "store/product_detail.html",
        {
            "product": product,
            "gallery_images": gallery_images,
            "related_products": related_products,
            "branch_stock": branch_stock,
            "branch_stock_featured": branch_stock_featured,
            "selected_store_id": selected_store_id_int,
            "selected_store_stock": selected_store_stock,
            "total_store_stock": total_store_stock,
            "branch_stock_search": branch_stock_search,
            "cart_total_quantity": cart_total_quantity,
            **pref,
        },
    )


def cart_add(request, pk):
    if request.method != "POST":
        return redirect("store:product_catalog")
    unauthorized = _require_customer_account(request)
    if unauthorized:
        _remember_post_login_cart_action(request, pk, request.POST.get("next"), request.POST.get("store_id"))
        messages.error(request, _admin_pref_context(request)["t"]["login_to_buy"])
        return unauthorized

    product = get_object_or_404(SanPham, pk=pk)
    next_url = request.POST.get("next")
    store_id = (request.POST.get("store_id") or "").strip()
    if not store_id.isdigit():
        messages.error(request, "Vui lòng chọn chi nhánh cửa hàng trước khi mua.")
        return redirect(next_url) if next_url else redirect("store:product_detail", pk=product.pk)
    store = get_object_or_404(CuaHang.objects.select_related("chuoi"), pk=int(store_id))
    stock_row = (
        TonKhoCuaHang.objects.filter(san_pham=product, cua_hang=store)
        .select_related("cua_hang", "cua_hang__chuoi")
        .first()
    )
    if stock_row is None:
        messages.error(
            request,
            f"Chi nhánh {store.ten} chưa cập nhật tồn kho cho sản phẩm này.",
        )
        return redirect(next_url) if next_url else redirect("store:product_detail", pk=product.pk)
    available_stock = int(stock_row.ton_kho or 0)
    if available_stock <= 0:
        messages.error(request, "Sản phẩm này hiện đã hết hàng.")
        return redirect(next_url) if next_url else redirect("store:product_detail", pk=product.pk)
    cart = _cart_session(request)
    key = _cart_entry_key(product.pk, store.pk)
    current_qty = int(cart.get(key, 0))
    if current_qty >= available_stock:
        messages.error(
            request,
            f"Chi nhánh {store.ten} chỉ còn {available_stock} sản phẩm cho mặt hàng này.",
        )
        return redirect(next_url) if next_url else redirect("store:cart")
    cart[key] = current_qty + 1
    request.session.modified = True
    messages.success(request, _admin_pref_context(request)["t"]["product_added"])
    return redirect(next_url) if next_url else redirect("store:cart")


def cart_view(request):
    items, total_quantity, total_amount = _cart_items(request)
    for item in items:
        item["display_unit_price"] = _format_currency(item["unit_price"])
        item["display_line_total"] = _format_currency(item["line_total"])
    return render(
        request,
        "store/cart.html",
        {
            "cart_items": items,
            "cart_total_quantity": total_quantity,
            "cart_total_amount": total_amount,
            "display_cart_total_amount": _format_currency(total_amount),
            **_admin_pref_context(request),
        },
    )


def cart_update(request):
    if request.method != "POST":
        return redirect("store:cart")
    unauthorized = _require_customer_account(request)
    if unauthorized:
        messages.error(request, _admin_pref_context(request)["t"]["login_to_buy"])
        return unauthorized

    cart = _cart_session(request)
    parsed_entries = []
    product_ids = set()
    store_ids = set()
    for key in cart.keys():
        product_id, store_id = _parse_cart_entry_key(key)
        if not product_id or not store_id:
            continue
        parsed_entries.append((str(key), product_id, store_id))
        product_ids.add(product_id)
        store_ids.add(store_id)
    products = {p.pk: p for p in SanPham.objects.filter(pk__in=product_ids)}
    stock_map = {
        (row.san_pham_id, row.cua_hang_id): int(row.ton_kho or 0)
        for row in TonKhoCuaHang.objects.filter(san_pham_id__in=product_ids, cua_hang_id__in=store_ids)
    }
    updated_cart = {}
    for key, product_id, store_id in parsed_entries:
        qty = request.POST.get(f"qty_{key}")
        if qty is None:
            continue
        try:
            qty_int = max(int(qty), 0)
        except ValueError:
            qty_int = 0
        product = products.get(product_id)
        if product is None:
            continue
        qty_int = min(qty_int, stock_map.get((product_id, store_id), 0))
        if qty_int > 0:
            updated_cart[key] = qty_int
    request.session["cart"] = updated_cart
    request.session.modified = True
    messages.success(request, _admin_pref_context(request)["t"]["cart_updated"])
    return redirect("store:cart")


def cart_remove(request, pk):
    if request.method != "POST":
        return redirect("store:cart")
    unauthorized = _require_customer_account(request)
    if unauthorized:
        messages.error(request, _admin_pref_context(request)["t"]["login_to_buy"])
        return unauthorized

    cart = _cart_session(request)
    cart_key = (request.POST.get("cart_key") or "").strip()
    if cart_key:
        cart.pop(cart_key, None)
    else:
        cart.pop(str(pk), None)
    request.session.modified = True
    messages.success(request, "Đã xóa sản phẩm khỏi giỏ hàng.")
    return redirect("store:cart")


def cart_clear(request):
    if request.method != "POST":
        return redirect("store:cart")
    unauthorized = _require_customer_account(request)
    if unauthorized:
        messages.error(request, _admin_pref_context(request)["t"]["login_to_buy"])
        return unauthorized

    request.session["cart"] = {}
    request.session.modified = True
    messages.success(request, "Đã xóa toàn bộ giỏ hàng.")
    return redirect("store:cart")


def feedback_view(request):
    pref = _admin_pref_context(request)
    initial_name = ""
    initial_email = ""
    initial_phone = ""
    if request.user.is_authenticated and _is_regular_user(request.user):
        profile = _get_customer_profile(request.user)
        initial_name = request.user.get_full_name().strip()
        initial_email = request.user.email or ""
        initial_phone = profile.so_dien_thoai or ""

    form_data = {
        "ho_ten": initial_name,
        "email": initial_email,
        "so_dien_thoai": initial_phone,
        "chu_de": "",
        "noi_dung": "",
    }
    errors = {}

    if request.method == "POST":
        form_data = {
            "ho_ten": (request.POST.get("ho_ten") or "").strip(),
            "email": (request.POST.get("email") or "").strip(),
            "so_dien_thoai": (request.POST.get("so_dien_thoai") or "").strip(),
            "chu_de": (request.POST.get("chu_de") or "").strip(),
            "noi_dung": (request.POST.get("noi_dung") or "").strip(),
        }
        if not form_data["ho_ten"]:
            errors["ho_ten"] = "Vui lòng nhập họ tên."
        if not form_data["email"]:
            errors["email"] = "Vui lòng nhập email."
        else:
            try:
                validate_email(form_data["email"])
            except ValidationError:
                errors["email"] = "Email không đúng định dạng."
        if not form_data["chu_de"]:
            errors["chu_de"] = "Vui lòng nhập chủ đề."
        if not form_data["noi_dung"]:
            errors["noi_dung"] = "Vui lòng nhập nội dung góp ý."

        if not errors:
            feedback = GopYKhachHang.objects.create(**form_data)
            try:
                _send_feedback_emails(feedback)
                messages.success(request, "Đã gửi góp ý thành công. Vui lòng kiểm tra email để xem phản hồi xác nhận.")
            except Exception:
                messages.warning(
                    request,
                    "Hệ thống đã lưu góp ý, nhưng chưa gửi được email. Hãy kiểm tra lại cấu hình Mailtrap trong .env.",
                )
            return redirect("store:feedback")

    return render(
        request,
        "store/feedback.html",
        {
            "feedback_form": form_data,
            "feedback_errors": errors,
            "cart_total_quantity": _cart_items(request)[1],
            **pref,
        },
    )


def checkout_view(request):
    unauthorized = _require_customer_account(request)
    if unauthorized:
        messages.error(request, _admin_pref_context(request)["t"]["login_to_buy"])
        return unauthorized

    items, total_quantity, total_amount = _cart_items(request)
    for item in items:
        item["display_unit_price"] = _format_currency(item["unit_price"])
        item["display_line_total"] = _format_currency(item["line_total"])
    pref = _admin_pref_context(request)
    if not items:
        messages.error(request, pref["t"]["cart_empty"])
        return redirect("store:product_catalog")

    profile = _get_customer_profile(request.user)
    default_address = _get_default_customer_address(request.user)
    saved_addresses = list(_customer_addresses_qs(request.user))
    initial_name = default_address.ho_ten_nguoi_nhan if default_address else request.user.get_full_name().strip()
    initial_email = request.user.email or ""
    initial_phone = default_address.so_dien_thoai if default_address else (profile.so_dien_thoai or "")
    initial_address = _format_customer_address(default_address) if default_address else (profile.dia_chi or "")
    selected_address_id = str(default_address.pk) if default_address else ""
    note_value = ""
    subtotal_amount = Decimal(total_amount or 0)
    discount_amount = Decimal("0")
    shipping_total = Decimal("0")
    final_amount = subtotal_amount
    voucher_code = ""
    applied_voucher = None
    available_vouchers = _get_checkout_available_vouchers(items, subtotal_amount)
    delivery_lat = str(default_address.vi_do) if default_address and default_address.vi_do is not None else ""
    delivery_lng = str(default_address.kinh_do) if default_address and default_address.kinh_do is not None else ""
    payment_method = "cod"
    transfer_code = ""
    transfer_receipt = None
    payment_method_choices = DonHang.PAYMENT_METHOD_CHOICES
    initial_lat_value = default_address.vi_do if default_address and default_address.vi_do is not None else None
    initial_lng_value = default_address.kinh_do if default_address and default_address.kinh_do is not None else None
    store_groups = _allocate_discount_to_groups(
        _group_cart_items_by_store(items, initial_lat_value, initial_lng_value),
        Decimal("0"),
    )
    shipping_total = sum(((group["shipping_fee"] or Decimal("0")) for group in store_groups), Decimal("0"))
    final_amount = subtotal_amount + shipping_total
    shipping_pending = any(group.get("shipping_pending") for group in store_groups)
    display_shipping_total = "Chưa tính" if shipping_pending else _format_currency(shipping_total)
    display_final_amount = f"{_format_currency(final_amount)} + ship" if shipping_pending else _format_currency(final_amount)
    if request.method == "POST":
        receiver_name = (request.POST.get("receiver_name") or "").strip()
        phone = (request.POST.get("phone") or "").strip()
        address = (request.POST.get("address") or "").strip()
        note = (request.POST.get("note") or "").strip()
        payment_method = (request.POST.get("payment_method") or "cod").strip()
        transfer_code = (request.POST.get("transfer_code") or "").strip()
        transfer_receipt = request.FILES.get("transfer_receipt")
        selected_address_id = (request.POST.get("selected_address_id") or "").strip()
        initial_name = receiver_name
        initial_phone = phone
        initial_address = address
        note_value = note
        voucher_code = _normalize_voucher_code(request.POST.get("voucher_code"))
        delivery_lat = (request.POST.get("delivery_lat") or "").strip()
        delivery_lng = (request.POST.get("delivery_lng") or "").strip()
        preview_only = request.POST.get("preview_voucher") == "1"
        selected_saved_address = None
        if selected_address_id.isdigit():
            selected_saved_address = next((item for item in saved_addresses if item.pk == int(selected_address_id)), None)
        if selected_saved_address and not delivery_lat and not delivery_lng and selected_saved_address.has_coordinates:
            delivery_lat = str(selected_saved_address.vi_do)
            delivery_lng = str(selected_saved_address.kinh_do)

        form_has_error = False
        try:
            lat_value = _parse_latitude(delivery_lat)
            lng_value = _parse_longitude(delivery_lng)
        except ValidationError as exc:
            messages.error(request, "; ".join(exc.messages))
            lat_value = None
            lng_value = None
            form_has_error = True

        if (lat_value is None) ^ (lng_value is None):
            messages.error(request, "Vui lòng nhập đủ cả vĩ độ và kinh độ giao hàng, hoặc để trống cả hai.")
            form_has_error = True

        if payment_method not in dict(DonHang.PAYMENT_METHOD_CHOICES):
            messages.error(request, "Phương thức thanh toán không hợp lệ.")
            form_has_error = True
        if payment_method == "bank_transfer" and not preview_only and not transfer_receipt:
            messages.error(request, "Vui lòng tải ảnh biên lai chuyển khoản trước khi đặt đơn.")
            form_has_error = True

        if voucher_code and not form_has_error:
            try:
                applied_voucher, discount_amount = _resolve_checkout_voucher(voucher_code, items, subtotal_amount)
            except ValidationError as exc:
                messages.error(request, "; ".join(exc.messages))
                form_has_error = True

        store_groups = _allocate_discount_to_groups(
            _group_cart_items_by_store(items, lat_value, lng_value),
            discount_amount,
        )
        shipping_total = sum(((group["shipping_fee"] or Decimal("0")) for group in store_groups), Decimal("0"))
        shipping_pending = any(group.get("shipping_pending") for group in store_groups)
        final_amount = max(subtotal_amount - discount_amount, Decimal("0")) + shipping_total
        display_shipping_total = "Chưa tính" if shipping_pending else _format_currency(shipping_total)
        display_final_amount = (
            f"{_format_currency(max(subtotal_amount - discount_amount, Decimal('0')))} + ship"
            if shipping_pending
            else _format_currency(final_amount)
        )
        if preview_only and not form_has_error:
            if applied_voucher is not None:
                messages.success(
                    request,
                    f"Đã áp dụng voucher {applied_voucher.ma_code}. Đơn hàng đang được giảm {_format_currency(discount_amount)}.",
                )
            return render(
                request,
                "store/checkout.html",
                {
                    "cart_items": items,
                    "cart_total_quantity": total_quantity,
                    "cart_total_amount": total_amount,
                    "display_cart_total_amount": _format_currency(total_amount),
                    "subtotal_amount": subtotal_amount,
                    "display_subtotal_amount": _format_currency(subtotal_amount),
                    "discount_amount": discount_amount,
                    "display_discount_amount": _format_currency(discount_amount),
                    "shipping_total": shipping_total,
                    "display_shipping_total": display_shipping_total,
                    "final_amount": final_amount,
                    "display_final_amount": display_final_amount,
                    "store_groups": store_groups,
                    "initial_name": initial_name,
                    "initial_email": initial_email,
                    "initial_phone": initial_phone,
                    "initial_address": initial_address,
                    "note_value": note_value,
                    "saved_addresses": saved_addresses,
                    "voucher_code": voucher_code,
                    "applied_voucher": applied_voucher,
                    "available_vouchers": available_vouchers,
                    "delivery_lat": delivery_lat,
                    "delivery_lng": delivery_lng,
                    "selected_address_id": selected_address_id,
                    "payment_method": payment_method,
                    "transfer_code": transfer_code,
                    "has_transfer_receipt": bool(transfer_receipt),
                    "payment_method_choices": payment_method_choices,
                    **pref,
                },
            )
        if receiver_name and phone and address and not form_has_error:
            try:
                with transaction.atomic():
                    product_ids = sorted({item["product"].pk for item in items})
                    locked_products = {
                        product.pk: product
                        for product in SanPham.objects.select_for_update().filter(pk__in=product_ids).order_by("pk")
                    }
                    store_ids = sorted({item["store_id"] for item in items if item.get("store_id")})
                    locked_store_rows = (
                        TonKhoCuaHang.objects.select_for_update()
                        .select_related("cua_hang", "cua_hang__chuoi")
                        .filter(cua_hang_id__in=store_ids, san_pham_id__in=product_ids)
                    )
                    store_stock_map = {
                        (row.san_pham_id, row.cua_hang_id): row
                        for row in locked_store_rows
                    }
                    product_running = {
                        product_id: int(product.ton_kho or 0)
                        for product_id, product in locked_products.items()
                    }
                    store_running = {
                        (row.san_pham_id, row.cua_hang_id): int(row.ton_kho or 0)
                        for row in locked_store_rows
                    }
                    store_groups = _allocate_discount_to_groups(
                        _group_cart_items_by_store(items, lat_value, lng_value),
                        discount_amount,
                    )
                    created_orders = []
                    order_items_to_create = []
                    stock_movements_to_create = []
                    store_stock_rows_to_create = []
                    updated_store_stock_rows = {}
                    for group in store_groups:
                        store = group["store"]
                        for item in group["items"]:
                            locked_product = locked_products.get(item["product"].pk)
                            if locked_product is None:
                                raise ValidationError("Một sản phẩm trong giỏ hàng không còn tồn tại.")
                            available = int(store_running.get((locked_product.pk, store.pk), 0))
                            if available < int(item["quantity"]):
                                raise ValidationError(
                                    f"Cửa hàng {store.ten} không đủ tồn kho cho {item['product'].ten}."
                                )
                        shipping_note = (
                            f"Phí giao hàng chi nhánh {store.ten}: {_format_currency(group['shipping_fee'])} "
                            f"(khoảng cách {group['distance_label']})."
                        )
                        order_note = "\n".join(part for part in [note, shipping_note] if part)
                        order = DonHang.objects.create(
                            khach_hang=request.user,
                            ho_ten_nguoi_nhan=receiver_name,
                            so_dien_thoai=phone,
                            dia_chi_giao_hang=address,
                            vi_do_giao_hang=lat_value,
                            kinh_do_giao_hang=lng_value,
                            ghi_chu=order_note,
                            tong_so_luong=group["total_quantity"],
                            phuong_thuc_thanh_toan=payment_method,
                            trang_thai_thanh_toan=_default_payment_status_for_method(payment_method),
                            tong_tien_truoc_giam=group["subtotal"],
                            giam_gia=group["discount_amount"],
                            tong_tien=group["merchandise_total"],
                            cua_hang_xu_ly=store,
                            khuyen_mai=applied_voucher,
                            ma_voucher_ap_dung=applied_voucher.ma_code if applied_voucher else "",
                            anh_bien_lai=transfer_receipt,
                            ma_giao_dich_thanh_toan=transfer_code,
                            thoi_gian_gui_bien_lai=timezone.now() if transfer_receipt else None,
                        )
                        created_orders.append((order, group))
                        _create_admin_notification(
                            f"Đơn hàng mới #{order.pk}",
                            (
                                f"Khách hàng {request.user.username} vừa đặt đơn #{order.pk} "
                                f"gồm {group['total_quantity']} sản phẩm, tổng tiền {_format_currency(group['final_amount'])}. "
                                f"Cửa hàng xử lý: {store.ten}. Phí ship: {_format_currency(group['shipping_fee'])}."
                            ),
                            level="info",
                            path=f"{reverse('store:admin_list', kwargs={'model_slug': ORDER_MODULE_SLUG})}?status=pending",
                            method="ORDER",
                            status_code=201,
                        )
                        if payment_method == "bank_transfer" and transfer_receipt:
                            _log_payment_confirmation(
                                order,
                                "submitted",
                                performed_by=request.user,
                                note=f"Khách đã tải biên lai chuyển khoản. Mã giao dịch: {transfer_code or '-'}",
                            )
                        for item in group["items"]:
                            locked_product = locked_products[item["product"].pk]
                            quantity = int(item["quantity"] or 0)
                            if quantity <= 0:
                                continue

                            product_stock = int(product_running.get(locked_product.pk, 0))
                            store_key = (locked_product.pk, store.pk)
                            store_stock = int(store_running.get(store_key, 0))
                            if product_stock < quantity or store_stock < quantity:
                                raise ValidationError(
                                    f"Tồn kho của {locked_product.ten} vừa thay đổi. Vui lòng cập nhật lại giỏ hàng."
                                )

                            order_items_to_create.append(
                                ChiTietDonHang(
                                    don_hang=order,
                                    san_pham=locked_product,
                                    so_luong=quantity,
                                    don_gia=item["unit_price"],
                                )
                            )
                            stock_movements_to_create.append(
                                GiaoDichKho(
                                    san_pham=locked_product,
                                    cua_hang=store,
                                    loai="export",
                                    so_luong=quantity,
                                    ton_truoc=product_stock,
                                    ton_sau=product_stock - quantity,
                                    don_hang=order,
                                    created_by=request.user,
                                    ghi_chu=f"Xuất kho cho đơn hàng #{order.pk} từ {store.ten}",
                                )
                            )

                            product_running[locked_product.pk] = product_stock - quantity
                            store_running[store_key] = store_stock - quantity

                            stock_row = store_stock_map.get((locked_product.pk, store.pk))
                            if stock_row is None:
                                store_stock_rows_to_create.append(
                                    TonKhoCuaHang(
                                        cua_hang=store,
                                        san_pham=locked_product,
                                        ton_kho=store_running[store_key],
                                    )
                                )
                                store_stock_map[(locked_product.pk, store.pk)] = store_stock_rows_to_create[-1]
                            else:
                                stock_row.ton_kho = store_running[store_key]
                                updated_store_stock_rows[(locked_product.pk, store.pk)] = stock_row

                    if order_items_to_create:
                        ChiTietDonHang.objects.bulk_create(order_items_to_create, batch_size=1000)
                    if stock_movements_to_create:
                        GiaoDichKho.objects.bulk_create(stock_movements_to_create, batch_size=1000)

                    products_to_update = []
                    for product_id, product in locked_products.items():
                        new_total = int(product_running.get(product_id, int(product.ton_kho or 0)))
                        if int(product.ton_kho or 0) != new_total:
                            product.ton_kho = new_total
                            products_to_update.append(product)
                    if products_to_update:
                        SanPham.objects.bulk_update(products_to_update, ["ton_kho"], batch_size=500)

                    if store_stock_rows_to_create:
                        TonKhoCuaHang.objects.bulk_create(store_stock_rows_to_create, batch_size=1000)
                    if updated_store_stock_rows:
                        TonKhoCuaHang.objects.bulk_update(
                            list(updated_store_stock_rows.values()),
                            ["ton_kho", "updated_at"],
                            batch_size=1000,
                        )
            except ValidationError as exc:
                if hasattr(exc, "message_dict"):
                    error_text = "; ".join(
                        msg for messages_list in exc.message_dict.values() for msg in messages_list
                    )
                else:
                    error_text = "; ".join(getattr(exc, "messages", []) or []) or str(exc)
                messages.error(
                    request,
                    error_text
                    or "Không thể tạo đơn hàng do tồn kho vừa thay đổi. Vui lòng thử lại.",
                )
                return redirect("store:cart")
            profile.so_dien_thoai = phone
            profile.save(update_fields=["so_dien_thoai"])
            if not saved_addresses:
                auto_address = DiaChiKhachHang.objects.create(
                    user=request.user,
                    ho_ten_nguoi_nhan=receiver_name,
                    so_dien_thoai=phone,
                    dia_chi_cu_the=address,
                    vi_do=lat_value,
                    kinh_do=lng_value,
                    mac_dinh=True,
                )
                _normalize_customer_address_defaults(request.user, target=auto_address)
            request.session["cart"] = {}
            request.session.modified = True
            if len(created_orders) > 1:
                messages.success(
                    request,
                    f"Đã tách đơn thành {len(created_orders)} đơn theo từng chi nhánh để xử lý tồn kho và phí giao hàng riêng.",
                )
            else:
                messages.success(request, pref["t"]["order_success"])
            try:
                confirmation_order, confirmation_group = created_orders[0]
                if not _send_order_confirmation(confirmation_order, confirmation_group["items"]):
                    messages.warning(
                        request,
                        "Đã tạo đơn hàng nhưng khách hàng chưa có email để gửi xác nhận.",
                    )
            except Exception:
                messages.warning(
                    request,
                        "Cảm ơn bạn đã đặt hàng.",
                )
            if payment_method == "momo":
                messages.info(request, "Đơn hàng đã tạo. Hãy hoàn tất bước thanh toán MoMo demo cho đơn đầu tiên.")
                return redirect("store:momo_demo_payment", pk=created_orders[0][0].pk)
            return redirect("store:my_orders")
        if not form_has_error:
            messages.error(request, "Vui lòng điền đầy đủ thông tin nhận hàng.")
    return render(
        request,
        "store/checkout.html",
        {
            "cart_items": items,
            "cart_total_quantity": total_quantity,
            "cart_total_amount": total_amount,
            "display_cart_total_amount": _format_currency(total_amount),
            "subtotal_amount": subtotal_amount,
            "display_subtotal_amount": _format_currency(subtotal_amount),
            "discount_amount": discount_amount,
            "display_discount_amount": _format_currency(discount_amount),
            "shipping_total": shipping_total,
            "display_shipping_total": display_shipping_total,
            "final_amount": final_amount,
            "display_final_amount": display_final_amount,
            "store_groups": store_groups,
            "initial_name": initial_name,
            "initial_email": initial_email,
            "initial_phone": initial_phone,
            "initial_address": initial_address,
            "note_value": note_value,
            "saved_addresses": saved_addresses,
            "voucher_code": voucher_code,
            "applied_voucher": applied_voucher,
            "available_vouchers": available_vouchers,
            "delivery_lat": delivery_lat,
            "delivery_lng": delivery_lng,
            "selected_address_id": selected_address_id,
            "payment_method": payment_method,
            "transfer_code": transfer_code,
            "has_transfer_receipt": bool(transfer_receipt),
            "payment_method_choices": payment_method_choices,
            **pref,
        },
    )


def checkout_shipping_preview_api(request):
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return JsonResponse({"ok": False, "error": "unauthorized"}, status=403)

    items, total_quantity, total_amount = _cart_items(request)
    if not items:
        return JsonResponse({"ok": False, "error": "cart_empty"}, status=400)

    raw_lat = (request.GET.get("delivery_lat") or "").strip()
    raw_lng = (request.GET.get("delivery_lng") or "").strip()
    voucher_code = _normalize_voucher_code(request.GET.get("voucher_code"))

    try:
        lat_value = _parse_latitude(raw_lat) if raw_lat else None
        lng_value = _parse_longitude(raw_lng) if raw_lng else None
    except ValidationError as exc:
        return JsonResponse({"ok": False, "error": "; ".join(exc.messages)}, status=400)

    if (lat_value is None) ^ (lng_value is None):
        return JsonResponse(
            {
                "ok": False,
                "error": "Vui lòng nhập đủ cả vĩ độ và kinh độ giao hàng, hoặc để trống cả hai.",
            },
            status=400,
        )

    subtotal_amount = Decimal(total_amount or 0)
    discount_amount = Decimal("0")
    voucher_error = ""
    applied_voucher = None
    if voucher_code:
        try:
            applied_voucher, discount_amount = _resolve_checkout_voucher(voucher_code, items, subtotal_amount)
        except ValidationError as exc:
            voucher_error = "; ".join(exc.messages) or "Voucher không hợp lệ."

    store_groups = _allocate_discount_to_groups(
        _group_cart_items_by_store(items, lat_value, lng_value),
        discount_amount,
    )
    shipping_total = sum(((group["shipping_fee"] or Decimal("0")) for group in store_groups), Decimal("0"))
    shipping_pending = any(group.get("shipping_pending") for group in store_groups)
    final_amount = max(subtotal_amount - discount_amount, Decimal("0")) + shipping_total
    display_shipping_total = "Chưa tính" if shipping_pending else _format_currency(shipping_total)
    display_final_amount = (
        f"{_format_currency(max(subtotal_amount - discount_amount, Decimal('0')))} + ship"
        if shipping_pending
        else _format_currency(final_amount)
    )

    return JsonResponse(
        {
            "ok": True,
            "cart_total_quantity": total_quantity,
            "subtotal_amount": str(subtotal_amount),
            "display_subtotal_amount": _format_currency(subtotal_amount),
            "discount_amount": str(discount_amount),
            "display_discount_amount": _format_currency(discount_amount),
            "shipping_total": str(shipping_total),
            "display_shipping_total": display_shipping_total,
            "final_amount": str(final_amount),
            "display_final_amount": display_final_amount,
            "shipping_pending": shipping_pending,
            "applied_voucher_code": applied_voucher.ma_code if applied_voucher else "",
            "voucher_error": voucher_error,
            "store_groups": [
                {
                    "store_id": group["store"].pk,
                    "distance_label": group["distance_label"],
                    "display_shipping_fee": group["display_shipping_fee"],
                    "display_discount_amount": group["display_discount_amount"],
                    "display_final_amount": group["display_final_amount"],
                }
                for group in store_groups
            ],
        }
    )


def my_orders(request):
    unauthorized = _require_customer_account(request)
    if unauthorized:
        return unauthorized
    status_filter = (request.GET.get("status") or "all").strip()
    query = (request.GET.get("q") or "").strip()
    qs = DonHang.objects.filter(khach_hang=request.user).select_related("cua_hang_xu_ly").prefetch_related("items__san_pham")
    if status_filter != "all":
        order_status_map = {
            "pending": ["pending"],
            "unpaid": ["pending"],
            "shipping": ["confirmed", "shipping"],
            "delivering": ["shipping"],
            "done": ["done"],
            "cancelled": ["cancelled"],
            "refund": ["cancelled"],
        }
        statuses = order_status_map.get(status_filter, [])
        if statuses:
            qs = qs.filter(trang_thai__in=statuses)
    if query:
        search_filter = (
            Q(ho_ten_nguoi_nhan__icontains=query)
            | Q(items__san_pham__ten__icontains=query)
            | Q(cua_hang_xu_ly__ten__icontains=query)
        )
        if query.isdigit():
            search_filter |= Q(pk=int(query))
        qs = qs.filter(search_filter).distinct()
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get("page"))
    orders = list(page_obj.object_list)
    for order in orders:
        order.display_total_amount = _format_currency(order.tong_tien)
        order.display_payment_method = order.get_phuong_thuc_thanh_toan_display()
        order.display_payment_status = order.get_trang_thai_thanh_toan_display()
        order.display_store_name = order.cua_hang_xu_ly.ten if order.cua_hang_xu_ly_id else "-"
        first_item = order.items.all().first()
        order.primary_product = first_item.san_pham if first_item and first_item.san_pham_id else None
        order.primary_thumb = ""
        if order.primary_product:
            try:
                if order.primary_product.hinh_anh:
                    order.primary_thumb = order.primary_product.hinh_anh.url
            except Exception:
                order.primary_thumb = ""
        for item in order.items.all():
            item.display_unit_price = _format_currency(item.don_gia)
        order.status_ui = _order_status_ui_text(order)
    status_tabs = [
        {"key": "all", "label": u("T\u1ea5t c\u1ea3")},
        {"key": "unpaid", "label": u("Ch\u1edd thanh to\u00e1n")},
        {"key": "shipping", "label": u("V\u1eadn chuy\u1ec3n")},
        {"key": "delivering", "label": u("Ch\u1edd giao h\u00e0ng")},
        {"key": "done", "label": u("Ho\u00e0n th\u00e0nh")},
        {"key": "cancelled", "label": u("\u0110\u00e3 h\u1ee7y")},
        {"key": "refund", "label": u("Tr\u1ea3 h\u00e0ng/Ho\u00e0n ti\u1ec1n")},
    ]
    _, cart_total_quantity, _ = _cart_items(request)
    return render(
        request,
        "user/orders.html",
        {
            **_user_shell_context(
                request,
                section="orders",
                subsection="orders",
                page_title=u("\u0110\u01a1n mua"),
            ),
            "orders": orders,
            "page_obj": page_obj,
            "paginator": paginator,
            "status_filter": status_filter,
            "status_tabs": status_tabs,
            "search_query": query,
            **_admin_pref_context(request),
        },
    )


def momo_demo_payment(request, pk):
    unauthorized = _require_customer_account(request)
    if unauthorized:
        return unauthorized

    order = get_object_or_404(DonHang, pk=pk, khach_hang=request.user)
    if order.phuong_thuc_thanh_toan != "momo":
        return redirect("store:order_detail", pk=order.pk)

    pref = _admin_pref_context(request)
    if request.method == "POST":
        action = (request.POST.get("action") or "").strip()
        if action == "success":
            if order.trang_thai_thanh_toan != "paid":
                order.trang_thai_thanh_toan = "paid"
                order.save(update_fields=["trang_thai_thanh_toan"])
            messages.success(request, u("Thanh to\u00e1n MoMo demo th\u00e0nh c\u00f4ng."))
            return redirect("store:order_detail", pk=order.pk)
        if action == "fail":
            with transaction.atomic():
                if order.trang_thai_thanh_toan != "unpaid":
                    order.trang_thai_thanh_toan = "unpaid"
                    order.save(update_fields=["trang_thai_thanh_toan"])
                if order.trang_thai != "cancelled":
                    order.trang_thai = "cancelled"
                    order.save(update_fields=["trang_thai"])
                _release_order_inventory_if_needed(order, reason=u("thanh to\u00e1n MoMo demo th\u1ea5t b\u1ea1i"))
            messages.error(request, u("Thanh to\u00e1n MoMo demo th\u1ea5t b\u1ea1i ho\u1eb7c \u0111\u00e3 b\u1ecb h\u1ee7y."))
            return redirect("store:order_detail", pk=order.pk)

    _, cart_total_quantity, _ = _cart_items(request)
    return render(
        request,
        "store/momo_demo.html",
        {
            **_momo_demo_context(order),
            "cart_total_quantity": cart_total_quantity,
            "user_notifications": _user_header_notifications(request.user),
            **pref,
        },
    )


def user_notifications(request, category="order"):
    unauthorized = _require_customer_account(request)
    if unauthorized:
        return unauthorized

    active_category = (request.GET.get("category") or category or "order").strip()
    allowed_categories = {"order", "promotion", "wallet", "shopee"}
    if active_category not in allowed_categories:
        active_category = "order"

    all_notifications = _build_user_notification_feed(request.user)
    filtered_notifications = [item for item in all_notifications if item["category"] == active_category]
    paginator = Paginator(filtered_notifications, 8)
    page_obj = paginator.get_page(request.GET.get("page"))
    notifications = list(page_obj.object_list)
    notification_tabs = [
        {"key": "order", "label": u("C\u1eadp nh\u1eadt \u0111\u01a1n h\u00e0ng"), "count": sum(1 for item in all_notifications if item["category"] == "order")},
        {"key": "promotion", "label": u("Khuy\u1ebfn m\u00e3i"), "count": sum(1 for item in all_notifications if item["category"] == "promotion")},
        {"key": "wallet", "label": u("C\u1eadp nh\u1eadt v\u00ed"), "count": sum(1 for item in all_notifications if item["category"] == "wallet")},
        {"key": "shopee", "label": u("C\u1eadp nh\u1eadt h\u1ec7 th\u1ed1ng"), "count": sum(1 for item in all_notifications if item["category"] == "shopee")},
    ]

    return render(
        request,
        "user/notifications.html",
        {
            **_user_shell_context(
                request,
                section="notifications",
                subsection=active_category,
                notification_section=active_category,
                page_title=u("Th\u00f4ng b\u00e1o c\u1ee7a t\u00f4i"),
            ),
            "notifications": notifications,
            "page_obj": page_obj,
            "paginator": paginator,
            "active_category": active_category,
            "notification_tabs": notification_tabs,
            **_admin_pref_context(request),
        },
    )


@never_cache
def user_payment(request):
    unauthorized = _require_regular_user(request)
    if unauthorized:
        return unauthorized

    orders = list(
        DonHang.objects.filter(khach_hang=request.user)
        .order_by("-created_at")[:6]
    )
    linked_cards = []
    linked_banks = []
    for order in orders:
        method = order.get_phuong_thuc_thanh_toan_display()
        if order.phuong_thuc_thanh_toan in {"momo", "ewallet"}:
            linked_cards.append(
                {
                    "title": method,
                    "subtitle": u("\u0110\u01a1n #{order}").format(order=order.pk),
                    "amount": _format_currency(order.tong_tien),
                }
            )
        elif order.phuong_thuc_thanh_toan == "bank_transfer":
            linked_banks.append(
                {
                    "title": u("T\u00e0i kho\u1ea3n chuy\u1ec3n kho\u1ea3n \u0111\u01a1n #{order}").format(order=order.pk),
                    "subtitle": order.ma_giao_dich_thanh_toan or u("Ch\u01b0a c\u00f3 m\u00e3 giao d\u1ecbch"),
                    "amount": _format_currency(order.tong_tien),
                }
            )

    return render(
        request,
        "user/payment.html",
        {
            **_user_shell_context(
                request,
                section="account",
                subsection="payment",
                account_subsection="payment",
                page_title=u("Ng\u00e2n h\u00e0ng"),
            ),
            "linked_cards": linked_cards,
            "linked_banks": linked_banks,
            **_admin_pref_context(request),
        },
    )


@never_cache
def user_notification_settings(request):
    unauthorized = _require_regular_user(request)
    if unauthorized:
        return unauthorized

    settings_state = _user_notification_settings_state(request)
    if request.method == "POST":
        for key in settings_state.keys():
            settings_state[key] = request.POST.get(key) == "on"
        _save_user_notification_settings_state(request, settings_state)
        messages.success(request, u("\u0110\u00e3 c\u1eadp nh\u1eadt c\u00e0i \u0111\u1eb7t th\u00f4ng b\u00e1o."))
        return redirect("store:user_notification_settings")

    return render(
        request,
        "user/notification_settings.html",
        {
            **_user_shell_context(
                request,
                section="account",
                subsection="notification_settings",
                account_subsection="notification_settings",
                page_title=u("C\u00e0i \u0111\u1eb7t th\u00f4ng b\u00e1o"),
            ),
            "settings_state": settings_state,
            **_admin_pref_context(request),
        },
    )


@never_cache
def user_privacy_settings(request):
    unauthorized = _require_regular_user(request)
    if unauthorized:
        return unauthorized

    privacy_state = _user_privacy_state(request)
    if request.method == "POST":
        privacy_state["delete_requested"] = True
        _save_user_privacy_state(request, privacy_state)
        _create_admin_notification(
            f"Yêu cầu xóa tài khoản #{request.user.pk}",
            f"Người dùng {request.user.username} đã gửi yêu cầu xóa tài khoản. Email: {request.user.email or '-'}",
            level="warning",
            path=reverse("store:admin_user_management"),
            method="POST",
            status_code=202,
        )
        messages.success(request, u("Y\u00eau c\u1ea7u x\u00f3a t\u00e0i kho\u1ea3n \u0111\u00e3 \u0111\u01b0\u1ee3c ghi nh\u1eadn."))
        return redirect("store:user_privacy_settings")

    return render(
        request,
        "user/privacy.html",
        {
            **_user_shell_context(
                request,
                section="account",
                subsection="privacy",
                account_subsection="privacy",
                page_title=u("Nh\u1eefng thi\u1ebft l\u1eadp ri\u00eang t\u01b0"),
            ),
            "privacy_state": privacy_state,
            **_admin_pref_context(request),
        },
    )


@never_cache
def user_personal_info(request):
    unauthorized = _require_regular_user(request)
    if unauthorized:
        return unauthorized

    info_state = _user_personal_info_state(request, request.user)
    edit_mode = request.GET.get("edit") == "1"
    if request.method == "POST":
        info_state = {
            "full_name": (request.POST.get("full_name") or "").strip(),
            "national_id": (request.POST.get("national_id") or "").strip(),
            "address": (request.POST.get("address") or "").strip(),
        }
        _save_user_personal_info_state(request, info_state)
        messages.success(request, u("\u0110\u00e3 c\u1eadp nh\u1eadt th\u00f4ng tin c\u00e1 nh\u00e2n."))
        return redirect("store:user_personal_info")

    masked_info = {
        "full_name": _mask_middle(info_state["full_name"], prefix=1, suffix=1),
        "national_id": _mask_middle(info_state["national_id"], prefix=0, suffix=4),
        "address": _mask_middle(info_state["address"], prefix=0, suffix=min(8, len(info_state["address"]))),
    }
    return render(
        request,
        "user/personal_info.html",
        {
            **_user_shell_context(
                request,
                section="account",
                subsection="personal_info",
                account_subsection="personal_info",
                page_title=u("Th\u00f4ng tin c\u00e1 nh\u00e2n"),
            ),
            "info_state": info_state,
            "masked_info": masked_info,
            "edit_mode": edit_mode,
            **_admin_pref_context(request),
        },
    )


@never_cache
def user_voucher_wallet(request):
    unauthorized = _require_regular_user(request)
    if unauthorized:
        return unauthorized

    vouchers = list(KhuyenMai.objects.filter(dang_ap_dung=True).order_by("-ngay_bat_dau", "-id")[:24])
    voucher_groups = {
        "all": [],
        "circle-k": [],
        "gs25": [],
    }
    active_group = (request.GET.get("group") or "all").strip()
    if active_group not in voucher_groups:
        active_group = "all"
    for voucher in vouchers:
        store_names = list(voucher.cua_hang.values_list("ten", flat=True))
        chain_names = list(voucher.cua_hang.values_list("chuoi__ten", flat=True))
        chain_names_normalized = [str(name or "").lower() for name in chain_names]
        belongs_circle_k = any("circle" in name for name in chain_names_normalized)
        belongs_gs25 = any("gs25" in name for name in chain_names_normalized)
        if not belongs_circle_k and not belongs_gs25:
            belongs_circle_k = True
            belongs_gs25 = True

        voucher.display_amount = _format_currency(voucher.gia_tri_giam)
        voucher.display_min_order = _format_currency(voucher.gia_tri_don_hang_toi_thieu or 0)
        voucher.display_expiry = timezone.localtime(voucher.ngay_ket_thuc).strftime("%d.%m.%Y") if voucher.ngay_ket_thuc else u("Kh\u00f4ng gi\u1edbi h\u1ea1n")
        voucher.badge_label = "Circle K"
        if belongs_gs25 and not belongs_circle_k:
            voucher.badge_label = "GS25"
        elif belongs_circle_k and belongs_gs25:
            voucher.badge_label = "Circle K & GS25"
        voucher.detail_rows = [
            {"label": "Mã voucher", "value": voucher.ma_code or "Đang cập nhật"},
            {"label": "Ưu đãi", "value": f"Giảm {voucher.display_amount}"},
            {"label": "Đơn tối thiểu", "value": voucher.display_min_order},
            {"label": "Hạn dùng", "value": voucher.display_expiry},
        ]
        if voucher.mo_ta:
            voucher.detail_rows.append({"label": "Mô tả", "value": voucher.mo_ta})
        if store_names:
            voucher.detail_rows.append({"label": "Áp dụng tại", "value": ", ".join(store_names[:4])})

        voucher_groups["all"].append(voucher)
        if belongs_circle_k:
            voucher_groups["circle-k"].append(voucher)
        if belongs_gs25:
            voucher_groups["gs25"].append(voucher)

    voucher_tabs = [
        {"key": "all", "label": u("T\u1ea5t c\u1ea3 ({count})").format(count=len(voucher_groups["all"]))},
        {"key": "circle-k", "label": f"Circle K ({len(voucher_groups['circle-k'])})"},
        {"key": "gs25", "label": f"GS25 ({len(voucher_groups['gs25'])})"},
    ]
    return render(
        request,
        "user/voucher_wallet.html",
        {
            **_user_shell_context(
                request,
                section="vouchers",
                subsection="vouchers",
                page_title="Kho Voucher",
            ),
            "vouchers": voucher_groups[active_group],
            "voucher_tabs": voucher_tabs,
            "active_group": active_group,
            **_admin_pref_context(request),
        },
    )


def order_detail(request, pk):
    unauthorized = _require_customer_account(request)
    if unauthorized:
        return unauthorized

    order = get_object_or_404(
        DonHang.objects.filter(khach_hang=request.user)
        .select_related("cua_hang_xu_ly")
        .prefetch_related("items__san_pham", "lich_su_xac_nhan_thanh_toan__performed_by"),
        pk=pk,
    )
    for item in order.items.all():
        item.display_unit_price = _format_currency(item.don_gia)
        item.display_line_total = _format_currency((item.don_gia or Decimal("0")) * item.so_luong)

    timeline = _order_status_timeline(order)
    order.display_subtotal_amount = _format_currency(order.tong_tien_truoc_giam or order.tong_tien)
    order.display_discount_amount = _format_currency(order.giam_gia)
    order.display_total_amount = _format_currency(order.tong_tien)
    order.display_payment_method = order.get_phuong_thuc_thanh_toan_display()
    order.display_payment_status = order.get_trang_thai_thanh_toan_display()
    order.display_store_name = order.cua_hang_xu_ly.ten if order.cua_hang_xu_ly_id else "-"
    order.created_text = timezone.localtime(order.created_at).strftime("%d/%m/%Y %H:%M")
    payment_review_logs = list(order.lich_su_xac_nhan_thanh_toan.all())

    _, cart_total_quantity, _ = _cart_items(request)
    return render(
        request,
        "store/order_detail.html",
        {
            "order": order,
            "timeline": timeline,
            "payment_review_logs": payment_review_logs,
            "cart_total_quantity": cart_total_quantity,
            "user_notifications": _user_header_notifications(request.user),
            **_admin_pref_context(request),
        },
    )


def report_404_action(request, action):
    # log user intent from 404 page
    if action not in {"retry", "support"}:
        return redirect("store:home")
    title = "Retry Request" if action == "retry" else "Support Request"
    Notification.objects.create(
        level="info",
        title=title,
        message="User clicked from 404 page",
        path=(request.GET.get("path") or request.path)[:255],
        method=request.method[:10],
        status_code=404,
    )
    # redirect back or home
    return redirect(request.GET.get("back") or "store:home")


import pandas as pd
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.db import transaction
from django.shortcuts import render
from .models import GiaoDichKho, SanPham, CuaHang, NhanVien
from django.contrib import messages
from django.shortcuts import redirect

# =========================
# PAGE
# =========================
def kho_excel_page(request):
    return render(request, "admin/kho_excel.html")


# =========================
# IMPORT
# =========================

@require_POST
def import_kho_excel(request):
    file = request.FILES.get("file")

    if not file:
        messages.error(request, "Chưa chọn file")
        return redirect("/admin/giao-dich-kho/excel/")

    try:
        df = pd.read_excel(file)

        df.columns = [col.strip().lower() for col in df.columns]

        required = {"san_pham", "loai", "so_luong"}
        if not required.issubset(df.columns):
            messages.error(request, f"Thiếu cột bắt buộc: {required}")
            return redirect("/admin/giao-dich-kho/excel/")

        errors = []
        staged_movements = []

        for i, row in df.iterrows():
            try:
                if pd.isna(row["san_pham"]):
                    raise ValueError("Thiếu san_pham")

                san_pham_id = int(row["san_pham"])
                if not SanPham.objects.filter(id=san_pham_id).exists():
                    raise ValueError("Sản phẩm không tồn tại")

                loai_raw = str(row["loai"]).strip().lower()
                if loai_raw in ["import", "nhap"]:
                    loai = "import"
                elif loai_raw in ["export", "xuat"]:
                    loai = "export"
                else:
                    raise ValueError("loai phải là import/export")

                if pd.isna(row["so_luong"]):
                    raise ValueError("Thiếu so_luong")

                so_luong = int(row["so_luong"])
                if so_luong <= 0:
                    raise ValueError("so_luong phải > 0")

                nhan_vien_id = None
                if "nhan_vien_id" in df.columns and pd.notna(row.get("nhan_vien_id")):
                    nhan_vien_id = int(row["nhan_vien_id"])
                elif "nhan_vien" in df.columns and pd.notna(row.get("nhan_vien")):
                    nhan_vien_id = int(row["nhan_vien"])

                if nhan_vien_id and not NhanVien.objects.filter(id=nhan_vien_id).exists():
                    raise ValueError("Nhân viên không tồn tại")

                cua_hang_id = None
                if "cua_hang_id" in df.columns and pd.notna(row.get("cua_hang_id")):
                    cua_hang_id = int(row["cua_hang_id"])
                elif "cua_hang" in df.columns and pd.notna(row.get("cua_hang")):
                    cua_hang_id = int(row["cua_hang"])

                if cua_hang_id and not CuaHang.objects.filter(id=cua_hang_id).exists():
                    raise ValueError("Cửa hàng không tồn tại")

                ghi_chu = ""
                if "ghi_chu" in df.columns and pd.notna(row.get("ghi_chu")):
                    ghi_chu = str(row["ghi_chu"]).strip()

                staged_movements.append(
                    GiaoDichKho(
                        san_pham_id=san_pham_id,
                        loai=loai,
                        so_luong=so_luong,
                        nhan_vien_id=nhan_vien_id,
                        cua_hang_id=cua_hang_id,
                        ghi_chu=ghi_chu,
                    )
                )
            except Exception as e:
                errors.append(f"Dòng {i+2}: {str(e)}")

        if errors:
            messages.error(request, "Import lỗi:\n" + "\n".join(errors))
            return redirect("/admin/giao-dich-kho/excel/")

        with transaction.atomic():
            for obj in staged_movements:
                obj._skip_signature = True
                obj.save()

        messages.success(request, f"Import thành công {len(staged_movements)} dòng")
        return redirect("/admin/giao-dich-kho/")

    except Exception as e:
        messages.error(request, str(e))
        return redirect("/admin/giao-dich-kho/excel/")

# =========================
# EXPORT 
# =========================
def export_kho_excel(request):
    qs = GiaoDichKho.objects.select_related(
        "san_pham", "nhan_vien", "cua_hang"
    ).order_by("-id")

    data = []

    for obj in qs:
        data.append({
            "san_pham": obj.san_pham_id,
            "ten_san_pham": obj.san_pham.ten if obj.san_pham else "",

            "loai": obj.loai,
            "so_luong": obj.so_luong,

            "nhan_vien_id": obj.nhan_vien_id if obj.nhan_vien else "",
            "ten_nhan_vien": obj.nhan_vien.ho_ten if obj.nhan_vien else "",

            "cua_hang_id": obj.cua_hang_id if obj.cua_hang else "",
            "ten_cua_hang": obj.cua_hang.ten if obj.cua_hang else "",

            "ghi_chu": obj.ghi_chu or "",
            "created_at": obj.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        })

    df = pd.DataFrame(data)

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="kho.xlsx"'

    df.to_excel(response, index=False)

    return response


# =========================
# TEMPLATE 
# =========================
def export_template_excel(request):
    df = pd.DataFrame([{
        "san_pham": 1,
        "ten_san_pham": "Tên sản phẩm",

        "loai": "import",
        "so_luong": 100,

        "nhan_vien_id": 1,
        "ten_nhan_vien": "Nguyễn Văn A",

        "cua_hang_id": 1,
        "ten_cua_hang": "Circle K Quận 1",

        "ghi_chu": "Nhập kho",
        "created_at": ""
    }])

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="template.xlsx"'

    df.to_excel(response, index=False)

    return response
