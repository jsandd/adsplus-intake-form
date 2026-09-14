"""Projection helpers. Everything spatial is stored in EPSG:5070 (CONUS Albers, metres)."""
import math
from pyproj import Transformer

_to5070 = Transformer.from_crs("EPSG:4326", "EPSG:5070", always_xy=True)
_to4326 = Transformer.from_crs("EPSG:5070", "EPSG:4326", always_xy=True)
FT = 3.280839895
MI = 1609.344


def to_m(lon, lat):
    return _to5070.transform(lon, lat)


def to_ll(x, y):
    return _to4326.transform(x, y)


def haversine_mi(a, b):
    la1, lo1, la2, lo2 = map(math.radians, [a[0], a[1], b[0], b[1]])
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 3958.8 * 2 * math.asin(math.sqrt(h))


def point_in_poly(lon, lat, poly):
    inside = False
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]; x2, y2 = poly[(i + 1) % n]
        if (y1 > lat) != (y2 > lat):
            xi = x1 + (lat - y1) * (x2 - x1) / (y2 - y1)
            if lon < xi:
                inside = not inside
    return inside
