import re


def parse_latlon(text: str):
    if not text:
        return None
    m = re.match(r"^\s*(-?\d+(?:\.\d+)?)\s*[,; ]\s*(-?\d+(?:\.\d+)?)\s*$", text.strip())
    if not m:
        return None
    lat = float(m.group(1))
    lon = float(m.group(2))
    if -90 <= lat <= 90 and -180 <= lon <= 180:
        return lat, lon
    return None
