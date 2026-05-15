import math
import re
import time
import json
import unicodedata
import hashlib
import requests
from functools import wraps

from django.http import JsonResponse
from django.db.models import Q
from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from modules.store.models import CuaHang


# =========================
# CONFIG
# =========================
ALIASES = {
    "CIRCLEK": ["CIRCLEK", "CIRCLE K", "CIRCLE_K", "CIRCLE-K", "Circle K"],
    "GS25": ["GS25", "GS 25", "Gs25", "GS-25"],
}

DEFAULT_CENTER = (10.7769, 106.7009)  # TP.HCM
VN_COUNTRY_CODE = "vn"

CACHE_TTL = 60 * 60 * 6
CACHE_TTL_SHORT = 60 * 10

CONTACT_EMAIL = "student@example.com"
NOMINATIM_TIMEOUT = 12
OSRM_TIMEOUT = 12

_LAST_NOMINATIM_TS_KEY = "nominatim:last_ts"
_NOMINATIM_MIN_INTERVAL_SEC = 0.35

MAX_STORES_RETURN = 2000


# =========================
# CORS
# =========================
def _add_cors_headers(resp, request):
    origin = request.META.get("HTTP_ORIGIN")
    resp["Access-Control-Allow-Origin"] = origin if origin else "*"
    resp["Vary"] = "Origin"
    resp["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    resp["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    resp["Access-Control-Max-Age"] = "86400"
    return resp


def _options_ok(request):
    resp = JsonResponse({"ok": True, "message": "OPTIONS OK"})
    return _add_cors_headers(resp, request)


def cors_view(fn):
    @wraps(fn)
    def _wrapped(request, *args, **kwargs):
        if request.method == "OPTIONS":
            return _options_ok(request)
        resp = fn(request, *args, **kwargs)
        return _add_cors_headers(resp, request)

    return _wrapped


# =========================
# RESPONSE HELPERS
# =========================
def ok(data=None, message="OK"):
    payload = {"ok": True, "message": message}
    if data:
        payload.update(data)
    return JsonResponse(payload)


def bad(message="Bad request", status=400, **extra):
    payload = {"ok": False, "error": message}
    payload.update(extra)
    return JsonResponse(payload, status=status)


def _safe_int(v, default=0, min_v=None, max_v=None):
    try:
        x = int(v)
    except Exception:
        x = default
    if min_v is not None:
        x = max(min_v, x)
    if max_v is not None:
        x = min(max_v, x)
    return x


def _safe_float(v, default=None):
    try:
        return float(v)
    except Exception:
        return default


def _cache_key(prefix: str, obj: dict):
    s = json.dumps(obj, sort_keys=True, ensure_ascii=False)
    h = hashlib.md5(s.encode("utf-8")).hexdigest()
    return f"{prefix}:{h}"


# =========================
# HELPERS
# =========================
def _headers():
    return {
        "User-Agent": f"webgis_project/1.0 (student project; contact: {CONTACT_EMAIL})",
        "Accept-Language": "vi,en;q=0.8",
    }


def _strip_accents(s: str) -> str:
    if not s:
        return ""
    s = unicodedata.normalize("NFD", s)
    s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn")
    return unicodedata.normalize("NFC", s)


def _normalize_brand(raw: str) -> str:
    if not raw:
        return ""
    up = (raw or "").strip().upper()
    if up in ALIASES:
        return up
    # Match alias xuất hiện ở bất kỳ vị trí nào (vd: "GS25 Nguyễn Trãi" vẫn nhận ra GS25).
    for key, arr in ALIASES.items():
        for a in arr:
            if a.upper() in up:
                return key
    return ""


def _brand_q(brand_key: str):
    """
    DB của bạn: CuaHang.chuoi (FK) -> ChuoiCuaHang.ten
    Bạn đã chuẩn hóa: 'CIRCLEK', 'GS25'
    """
    if not brand_key:
        return Q()
    q = Q()
    for b in ALIASES.get(brand_key, []):
        q |= Q(chuoi__ten__iexact=b)
    return q


def _parse_latlon(text: str):
    if not text:
        return None
    t = text.strip()
    m = re.match(r"^\s*(-?\d+(?:\.\d+)?)\s*[,; ]\s*(-?\d+(?:\.\d+)?)\s*$", t)
    if not m:
        return None
    lat = float(m.group(1))
    lon = float(m.group(2))
    if -90 <= lat <= 90 and -180 <= lon <= 180:
        return lat, lon
    return None


def _haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = (math.sin(dphi / 2) ** 2) + math.cos(phi1) * math.cos(phi2) * (math.sin(dlambda / 2) ** 2)
    return 2 * R * math.asin(math.sqrt(a))


def _bbox_filter(qs, lat, lon, radius_km):
    dlat = radius_km / 111.0
    dlon = radius_km / (111.0 * max(math.cos(math.radians(lat)), 1e-6))
    return qs.filter(
        vi_do__gte=lat - dlat, vi_do__lte=lat + dlat,
        kinh_do__gte=lon - dlon, kinh_do__lte=lon + dlon
    )


def _store_dict(s: CuaHang, extra=None):
    def _is_open_now(store: CuaHang, now_t=None):
        if getattr(store, "hoat_dong_24h", False):
            return True
        open_t = getattr(store, "mo_cua", None)
        close_t = getattr(store, "dong_cua", None)
        if not open_t or not close_t:
            return None
        now_t = now_t or timezone.localtime().time()
        if open_t <= close_t:
            return open_t <= now_t <= close_t
        # Overnight shift, e.g. 22:00 -> 06:00.
        return now_t >= open_t or now_t <= close_t

    def _business_hours(store: CuaHang):
        if getattr(store, "hoat_dong_24h", False):
            return "24/7"
        open_t = getattr(store, "mo_cua", None)
        close_t = getattr(store, "dong_cua", None)
        if open_t and close_t:
            return f"{open_t.strftime('%H:%M')}-{close_t.strftime('%H:%M')}"
        if open_t:
            return f"Mo {open_t.strftime('%H:%M')}"
        if close_t:
            return f"Dong {close_t.strftime('%H:%M')}"
        return ""

    d = {
        "id": s.id,
        "name": s.ten,
        "brand": s.chuoi.ten if getattr(s, "chuoi", None) else "",
        "address_db": s.dia_chi,
        "district": getattr(s, "quan_huyen", "") or "",
        "lat": float(s.vi_do),
        "lon": float(s.kinh_do),
        "open_time": s.mo_cua.strftime("%H:%M") if getattr(s, "mo_cua", None) else None,
        "close_time": s.dong_cua.strftime("%H:%M") if getattr(s, "dong_cua", None) else None,
        "is_24h": bool(getattr(s, "hoat_dong_24h", False)),
        "is_open_now": _is_open_now(s),
        "business_hours": _business_hours(s),
        "coord_source": "db",
    }
    if extra:
        d.update(extra)
    return d


def _normalize_raw_query(raw: str) -> str:
    if not raw:
        return ""
    parts = [x.strip() for x in raw.splitlines() if x.strip()]
    q = ", ".join(parts) if parts else raw.strip()
    q = re.sub(r"\s+", " ", q).strip()
    q = re.sub(r"(?i)^\s*(circle\s*k|circlek|gs25)\s+", "", q).strip()
    q = re.sub(r"(?i)\bQ\s*(\d+)\b", r"Quan \1", q)
    q = re.sub(r"(?i)\bP\s*(\d+)\b", r"Phuong \1", q)
    q = re.sub(r"\s*,\s*", ", ", q)
    q = re.sub(r"(, )+", ", ", q).strip(" ,")
    return q


def _ensure_hcm_vn(q: str) -> str:
    if not q:
        return ""
    low_plain = _strip_accents(q).lower()
    has_vn = ("viet nam" in low_plain) or ("vietnam" in low_plain)
    has_hcm = ("ho chi minh" in low_plain) or ("tp hcm" in low_plain) or bool(re.search(r"\bhcm\b", low_plain))
    has_district = bool(re.search(r"\bquan\s*\d+\b", low_plain))
    comma_parts = [part.strip() for part in q.split(",") if part.strip()]

    q = re.sub(r"(?i)\bTP\s*HCM\b", "Thanh pho Ho Chi Minh", q)
    q = re.sub(r"(?i)\bHCM\b", "Thanh pho Ho Chi Minh", q)
    q = re.sub(r"(?i)\bSai\s*Gon\b", "Thanh pho Ho Chi Minh", q)

    if (has_district or len(comma_parts) >= 2) and not has_hcm:
        q = f"{q}, Thanh pho Ho Chi Minh"
    if not has_vn:
        q = f"{q}, Viet Nam"
    return q.strip()


def _make_geocode_variants(raw_q: str):
    base = _normalize_raw_query(raw_q)
    if not base:
        return []
    v1 = _ensure_hcm_vn(base)
    v2 = _strip_accents(v1)
    v3 = base
    if not re.search(r"\bviet nam\b|\bvietnam\b", _strip_accents(v3).lower()):
        v3 = f"{v3}, Viet Nam"

    out, seen = [], set()
    for v in [v1, v2, v3]:
        vv = re.sub(r"\s+", " ", v).strip()
        if vv and vv not in seen:
            seen.add(vv)
            out.append(vv)
    return out


def _make_geocode_fallback_queries(raw_q: str):
    variants = _make_geocode_variants(raw_q)
    out, seen = [], set()

    def _add(v: str):
        vv = re.sub(r"\s+", " ", (v or "")).strip(" ,")
        if vv and vv not in seen:
            seen.add(vv)
            out.append(vv)

    for v in variants:
        _add(v)
        parts = [p.strip() for p in v.split(",") if p.strip()]
        if len(parts) >= 2:
            # Drop business/building prefix, keep street+district+city.
            _add(", ".join(parts[1:]))
        if len(parts) >= 3:
            # Keep only street/district/city/country tail.
            _add(", ".join(parts[-4:]))
            _add(", ".join(parts[-3:]))

        # Remove common building prefixes.
        _add(re.sub(
            r"(?i)\b(cao oc|cao ốc|toa nha|tòa nhà|building|chung cu|chung cư|apartment|can ho|căn hộ)\b",
            " ",
            v,
        ))

    return out


def _norm_text(s: str) -> str:
    s = _strip_accents((s or "").lower())
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _tokens(s: str):
    stop = {
        "viet", "nam", "vietnam", "thanh", "pho", "tp", "ho", "chi", "minh",
        "duong", "street", "road", "hem", "ngo", "so", "ap", "xa", "phuong",
        "quan", "huyen", "city", "ward", "district",
    }
    t = []
    for w in _norm_text(s).split():
        if len(w) <= 1:
            continue
        if w in stop:
            continue
        t.append(w)
    return t


def _score_geocode_candidate(query: str, display: str):
    q_tokens = set(_tokens(query))
    d_tokens = set(_tokens(display))
    if not q_tokens or not d_tokens:
        return 0.0
    inter = len(q_tokens & d_tokens)
    score = inter / max(len(q_tokens), 1)

    q_nums = set(re.findall(r"\d+", query or ""))
    d_nums = set(re.findall(r"\d+", display or ""))
    if q_nums and d_nums:
        score += 0.15 * (len(q_nums & d_nums) / len(q_nums))
    return score


def _cache_get(key):
    return cache.get(key)


def _cache_set(key, value, seconds=CACHE_TTL):
    cache.set(key, value, seconds)


def _nominatim_throttle():
    last = _cache_get(_LAST_NOMINATIM_TS_KEY)
    now = time.time()
    if last:
        try:
            last = float(last)
            if (now - last) < _NOMINATIM_MIN_INTERVAL_SEC:
                time.sleep(_NOMINATIM_MIN_INTERVAL_SEC - (now - last))
        except Exception:
            pass
    _cache_set(_LAST_NOMINATIM_TS_KEY, str(time.time()), seconds=60)


def _call_nominatim_search_safe(query: str, use_countrycodes=True):
    _nominatim_throttle()
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": query, "format": "jsonv2", "limit": 8, "addressdetails": 1}
    if use_countrycodes:
        params["countrycodes"] = VN_COUNTRY_CODE
    try:
        r = requests.get(url, params=params, headers=_headers(), timeout=NOMINATIM_TIMEOUT)
        if r.status_code != 200:
            return None, {"status": r.status_code, "body": r.text[:200], "query": query}
        return (r.json() or []), None
    except Exception as e:
        return None, {"exception": str(e), "query": query}


def _call_photon_search_safe(query: str):
    _nominatim_throttle()
    url = "https://photon.komoot.io/api/"
    params = {"q": query, "limit": 8, "lang": "en"}
    try:
        r = requests.get(url, params=params, headers=_headers(), timeout=NOMINATIM_TIMEOUT)
        if r.status_code != 200:
            return None, {"status": r.status_code, "body": r.text[:200], "query": query, "provider": "photon"}

        data = r.json() or {}
        feats = data.get("features") or []
        items = []
        for f in feats:
            geom = f.get("geometry") or {}
            coords = geom.get("coordinates") or []
            if len(coords) >= 2:
                lon = coords[0]
                lat = coords[1]
                props = f.get("properties") or {}
                parts = [
                    props.get("name"),
                    props.get("street"),
                    props.get("city"),
                    props.get("district"),
                    props.get("state"),
                    props.get("country"),
                ]
                display = ", ".join([p for p in parts if p])
                items.append({
                    "display_name": display,
                    "lat": str(lat),
                    "lon": str(lon),
                    "place_id": props.get("osm_id"),
                })
        return items, None
    except Exception as e:
        return None, {"exception": str(e), "query": query, "provider": "photon"}


def _call_nominatim_reverse_safe(lat: float, lon: float):
    _nominatim_throttle()
    url = "https://nominatim.openstreetmap.org/reverse"
    params = {"format": "jsonv2", "lat": lat, "lon": lon, "zoom": 18, "addressdetails": 1}
    try:
        r = requests.get(url, params=params, headers=_headers(), timeout=NOMINATIM_TIMEOUT)
        if r.status_code != 200:
            return None, {"status": r.status_code, "body": r.text[:200]}
        return r.json(), None
    except Exception as e:
        return None, {"exception": str(e)}


def _reverse_geocode(lat: float, lon: float):
    key = _cache_key("geo_rev", {"lat": round(lat, 6), "lon": round(lon, 6)})
    cached = _cache_get(key)
    if isinstance(cached, dict):
        return cached, None
    res, err = _call_nominatim_reverse_safe(lat, lon)
    if res:
        _cache_set(key, res, seconds=60 * 60)
        return res, None
    return None, err


def _resolve_geocode_payload(q: str):
    variants = _make_geocode_fallback_queries(q)
    if not variants:
        return {"q": q, "location": None, "provider": None, "error": "NO_VARIANTS"}

    last_err = None
    candidates = []

    for v in variants[:5]:
        arr, err = _call_nominatim_search_safe(v, use_countrycodes=True)
        if arr:
            for it in arr[:8]:
                candidates.append({
                    "provider": "nominatim",
                    "lat": _safe_float(it.get("lat")),
                    "lon": _safe_float(it.get("lon")),
                    "display": it.get("display_name", ""),
                })
        else:
            last_err = err

    for v in variants[:5]:
        arr, err = _call_photon_search_safe(v)
        if arr:
            for it in arr[:8]:
                candidates.append({
                    "provider": "photon",
                    "lat": _safe_float(it.get("lat")),
                    "lon": _safe_float(it.get("lon")),
                    "display": it.get("display_name", ""),
                })
        else:
            last_err = err

    uniq = []
    seen = set()
    for c in candidates:
        if c["lat"] is None or c["lon"] is None:
            continue
        k = (round(float(c["lat"]), 6), round(float(c["lon"]), 6), (c["display"] or "").strip().lower())
        if k in seen:
            continue
        seen.add(k)
        c["score"] = _score_geocode_candidate(q, c.get("display", ""))
        uniq.append(c)

    uniq.sort(key=lambda x: x.get("score", 0.0), reverse=True)
    best = uniq[0] if uniq else None

    if best and best.get("score", 0.0) >= 0.18:
        return {
            "q": q,
            "provider": best.get("provider"),
            "location": {
                "lat": best.get("lat"),
                "lon": best.get("lon"),
                "display": best.get("display", ""),
            },
            "score": round(best.get("score", 0.0), 4),
            "variants": variants[:6],
            "candidates_count": len(uniq),
        }

    return {
        "q": q,
        "provider": None,
        "location": None,
        "score": round(best.get("score", 0.0), 4) if best else 0.0,
        "variants": variants[:6],
        "candidates_count": len(uniq),
        "error": last_err,
    }


# =========================
# ENDPOINTS
# =========================
@cors_view
def ping(request):
    return ok({"pong": True}, message="pong")


@cors_view
def suggest(request):
    q = (request.GET.get("q") or "").strip()
    if len(q) < 3:
        return ok({"q": q, "items": [], "variants": []}, message="Type more")

    key = _cache_key("suggest", {"q": q.lower()})
    cached = _cache_get(key)
    if isinstance(cached, dict):
        return ok(cached, message="OK (cache)")

    variants = _make_geocode_variants(q)
    items = []
    last_err = None

    for v in variants[:4]:
        arr, err = _call_nominatim_search_safe(v, use_countrycodes=True)
        if arr:
            for x in arr[:8]:
                items.append({
                    "display": x.get("display_name", ""),
                    "lat": x.get("lat"),
                    "lon": x.get("lon"),
                    "place_id": x.get("place_id"),
                })
            break
        last_err = err

        arr, err = _call_nominatim_search_safe(v, use_countrycodes=False)
        if arr:
            for x in arr[:8]:
                items.append({
                    "display": x.get("display_name", ""),
                    "lat": x.get("lat"),
                    "lon": x.get("lon"),
                    "place_id": x.get("place_id"),
                })
            break
        last_err = err

    seen, uniq = set(), []
    for it in items:
        k = (it.get("display") or "").strip().lower()
        if k and k not in seen:
            seen.add(k)
            uniq.append(it)

    payload = {"q": q, "items": uniq, "variants": variants[:6], "error": last_err}
    _cache_set(key, payload, seconds=60 * 30)
    return ok(payload, message="OK")


@cors_view
def reverse(request):
    lat = _safe_float(request.GET.get("lat"))
    lon = _safe_float(request.GET.get("lon"))
    if lat is None or lon is None:
        return bad("Required: lat, lon", status=400)

    res, err = _reverse_geocode(lat, lon)
    if res:
        display = res.get("display_name", "")
        return ok(
            {"lat": lat, "lon": lon, "display": display, "display_address": display, "raw": res},
            message="OK",
        )
    return ok({"lat": lat, "lon": lon, "display": "", "display_address": "", "error": err}, message="NO_RESULT")


@cors_view
def geocode(request):
    q = (request.GET.get("q") or "").strip()
    if len(q) < 3:
        return bad("Required: q (at least 3 chars)", status=400)

    key = _cache_key("geocode", {"q": q.lower()})
    cached = _cache_get(key)
    if isinstance(cached, dict):
        return ok(cached, message="OK (cache)")

    payload = _resolve_geocode_payload(q)
    _cache_set(key, payload, seconds=60 * 30)
    return ok(payload, message="OK" if payload.get("location") else "NO_RESULT")


@cors_view
def route_osrm(request):
    profile = (request.GET.get("profile") or "driving").strip().lower()
    if profile not in ("driving", "walking", "cycling"):
        profile = "driving"

    frm = (request.GET.get("from") or "").strip()
    to = (request.GET.get("to") or "").strip()
    alternatives = _safe_int(request.GET.get("alternatives", 1), default=1, min_v=0, max_v=3)

    f = _parse_latlon(frm.replace(",", " "))
    t = _parse_latlon(to.replace(",", " "))
    if not f or not t:
        return bad("Required: from=lat,lon and to=lat,lon", status=400)

    flt, fln = f
    tlt, tln = t

    key = _cache_key("osrm_route", {
        "profile": profile,
        "from": [round(flt, 6), round(fln, 6)],
        "to": [round(tlt, 6), round(tln, 6)],
        "alternatives": alternatives
    })
    cached = _cache_get(key)
    if isinstance(cached, dict):
        return ok(cached, message="OK (cache)")

    url = f"https://router.project-osrm.org/route/v1/{profile}/{fln},{flt};{tln},{tlt}"
    params = {
        "overview": "full",
        "geometries": "geojson",
        "steps": "true",
        "alternatives": "true" if alternatives else "false"
    }

    try:
        r = requests.get(url, params=params, headers=_headers(), timeout=OSRM_TIMEOUT)
        if r.status_code != 200:
            return bad("OSRM error", status=502, status_code=r.status_code, body=r.text[:250])

        data = r.json()
        if data.get("code") != "Ok":
            return bad("OSRM not OK", status=502, raw=data)

        routes = data.get("routes") or []
        out = {"profile": profile, "from": {"lat": flt, "lon": fln}, "to": {"lat": tlt, "lon": tln}, "routes": routes}
        _cache_set(key, out, seconds=60 * 30)
        return ok(out, message="OK")
    except Exception as e:
        return bad("OSRM exception", status=502, exception=str(e))


@cors_view
def districts(request):
    brand = _normalize_brand(request.GET.get("brand", ""))
    key = _cache_key("districts", {"brand": brand or "ALL"})
    cached = _cache_get(key)
    if isinstance(cached, list):
        return ok({"brand": brand or "ALL", "districts": cached}, message="OK (cache)")

    qs = CuaHang.objects.select_related("chuoi").all()
    if brand:
        qs = qs.filter(_brand_q(brand))

    items = sorted({
        (getattr(s, "quan_huyen", "") or "").strip()
        for s in qs
        if (getattr(s, "quan_huyen", "") or "").strip()
    })
    _cache_set(key, items, seconds=CACHE_TTL)
    return ok({"brand": brand or "ALL", "districts": items}, message="OK")


@cors_view
def stores_in_radius(request):
    lat = _safe_float(request.GET.get("lat"))
    lon = _safe_float(request.GET.get("lon"))
    radius_km = _safe_float(request.GET.get("radius_km"), 1.0)
    if lat is None or lon is None:
        return bad("Required: lat, lon", status=400)
    if radius_km <= 0:
        return bad("radius_km must be > 0", status=400)

    brand = _normalize_brand(request.GET.get("brand", ""))
    district = (request.GET.get("district") or "").strip()

    limit = _safe_int(request.GET.get("limit", 300), default=300, min_v=1, max_v=1000)
    offset = _safe_int(request.GET.get("offset", 0), default=0, min_v=0, max_v=100000)

    key = _cache_key("stores_in_radius", {
        "lat": round(lat, 6), "lon": round(lon, 6),
        "radius_km": round(radius_km, 3),
        "brand": brand or "ALL",
        "district": district.lower(),
    })
    cached = _cache_get(key)
    if isinstance(cached, list):
        sliced = cached[offset: offset + limit]
        return ok({
            "brand": brand or "ALL",
            "center": {"lat": lat, "lon": lon},
            "radius_km": radius_km,
            "total": len(cached),
            "count": len(sliced),
            "offset": offset,
            "limit": limit,
            "stores": sliced,
        }, message="OK (cache)")

    qs = CuaHang.objects.select_related("chuoi").all()
    if brand:
        qs = qs.filter(_brand_q(brand))
    if district:
        qs = qs.filter(quan_huyen__iexact=district)

    qs = _bbox_filter(qs, lat, lon, radius_km)

    result = []
    for s in qs:
        d = _haversine_km(lat, lon, float(s.vi_do), float(s.kinh_do))
        if d <= radius_km:
            result.append(_store_dict(s, {"distance_km": round(d, 3)}))

    result.sort(key=lambda x: x.get("distance_km", 1e9))
    if len(result) > MAX_STORES_RETURN:
        result = result[:MAX_STORES_RETURN]

    _cache_set(key, result, seconds=CACHE_TTL_SHORT)

    sliced = result[offset: offset + limit]
    return ok({
        "brand": brand or "ALL",
        "center": {"lat": lat, "lon": lon},
        "radius_km": radius_km,
        "total": len(result),
        "count": len(sliced),
        "offset": offset,
        "limit": limit,
        "stores": sliced,
    }, message="OK")


@cors_view
def stores_in_bounds(request):
    south = _safe_float(request.GET.get("south"))
    west = _safe_float(request.GET.get("west"))
    north = _safe_float(request.GET.get("north"))
    east = _safe_float(request.GET.get("east"))
    if None in (south, west, north, east):
        return bad("Required: south, west, north, east", status=400)

    brand = _normalize_brand(request.GET.get("brand", ""))
    district = (request.GET.get("district") or "").strip()
    limit = _safe_int(request.GET.get("limit", 500), default=500, min_v=1, max_v=2000)

    qs = CuaHang.objects.select_related("chuoi").all()
    if brand:
        qs = qs.filter(_brand_q(brand))
    if district:
        qs = qs.filter(quan_huyen__iexact=district)

    qs = qs.filter(
        vi_do__gte=min(south, north),
        vi_do__lte=max(south, north),
        kinh_do__gte=min(west, east),
        kinh_do__lte=max(west, east),
    )[:limit]

    stores = [_store_dict(s) for s in qs]
    return ok({
        "brand": brand or "ALL",
        "bounds": {"south": south, "west": west, "north": north, "east": east},
        "count": len(stores),
        "stores": stores,
    }, message="OK")


@cors_view
def search_stores(request):
    q = (request.GET.get("q") or "").strip()
    brand = _normalize_brand(request.GET.get("brand", ""))
    district = (request.GET.get("district") or "").strip()
    limit = _safe_int(request.GET.get("limit", 200), default=200, min_v=1, max_v=1000)

    qs = CuaHang.objects.select_related("chuoi").all()
    if brand:
        qs = qs.filter(_brand_q(brand))
    if district:
        qs = qs.filter(quan_huyen__iexact=district)

    if q:
        qs = qs.filter(Q(ten__icontains=q) | Q(dia_chi__icontains=q))

    qs = qs[:limit]
    stores = [_store_dict(s) for s in qs]
    return ok({"q": q, "brand": brand or "ALL", "district": district, "count": len(stores), "stores": stores}, message="OK")


@csrf_exempt
@cors_view
def smart_search(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))
        except Exception:
            data = {}
    elif request.method == "GET":
        data = {
            "ten": request.GET.get("ten") or request.GET.get("brand"),
            "brand": request.GET.get("brand"),
            "dia_chi": request.GET.get("q") or request.GET.get("dia_chi"),
            "lat": request.GET.get("lat"),
            "lng": request.GET.get("lng") or request.GET.get("lon"),
            "max_km": request.GET.get("max_km"),
        }
    else:
        return bad("Method not allowed", status=405)

    ten = (data.get("ten") or "").strip()
    dia_chi = (data.get("dia_chi") or "").strip()
    lat_in = data.get("lat")
    lng_in = data.get("lng")

    brand = _normalize_brand(ten) or _normalize_brand(data.get("brand", ""))
    max_km = _safe_float(data.get("max_km"), 0.5) or 0.5
    if max_km <= 0:
        max_km = 0.5

    client_latlng = None
    if lat_in not in (None, "") and lng_in not in (None, ""):
        try:
            client_latlng = (float(lat_in), float(lng_in))
        except Exception:
            client_latlng = None

    geocode_info = None

    # pick center
    if dia_chi:
        latlon = _parse_latlon(dia_chi)
        if latlon:
            lat, lng = latlon
            mode = "latlon_from_text"
        else:
            geo = _resolve_geocode_payload(dia_chi)
            geocode_info = {
                "provider": geo.get("provider"),
                "score": geo.get("score"),
                "candidates_count": geo.get("candidates_count"),
            }
            loc = geo.get("location")
            if loc and loc.get("lat") is not None and loc.get("lon") is not None:
                lat = float(loc["lat"])
                lng = float(loc["lon"])
                mode = "geocode_address"
            elif client_latlng:
                lat, lng = client_latlng
                mode = "client_latlon_after_geocode_fail"
            else:
                lat, lng = DEFAULT_CENTER
                mode = "fallback_default_no_geocode"
    else:
        if client_latlng:
            lat, lng = client_latlng
            mode = "client_latlon"
        else:
            lat, lng = DEFAULT_CENTER
            mode = "default"

    candidates = CuaHang.objects.select_related("chuoi").all()
    if brand:
        candidates = candidates.filter(_brand_q(brand))
    candidates = _bbox_filter(candidates, lat, lng, max_km)

    stores_list = []
    for s in candidates:
        d = _haversine_km(lat, lng, float(s.vi_do), float(s.kinh_do))
        if d <= max_km:
            stores_list.append(_store_dict(s, {"distance_km": round(d, 3)}))

    stores_list.sort(key=lambda x: x.get("distance_km", 1e9))
    store_data = stores_list[0] if stores_list else None

    return JsonResponse({
        "ok": bool(stores_list),
        "tool": "smart_search",
        "mode": mode,
        "geocode": geocode_info,
        "input": {"ten": ten, "dia_chi": dia_chi, "lat": lat, "lng": lng, "brand": brand, "max_km": max_km},
        "location": {"lat": lat, "lon": lng, "display_address": dia_chi or "TP.HCM"},
        "store": store_data,
        "count": len(stores_list),
        "stores": stores_list[:300],
        "message": f"Tim thay {len(stores_list)} cua hang trong {max_km} km.",
    })
