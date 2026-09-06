"""Geometry helpers: distances, bearings, projections, state lookup.

State outlines are simplified polygons (the same low-poly shapes the map uses).
They are good enough to say which state a point is in; they are not survey lines.
"""
import math

R_MI = 3958.8


def haversine(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * R_MI * math.asin(math.sqrt(h))


def bearing(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    y = math.sin(lo2 - lo1) * math.cos(la2)
    x = math.cos(la1) * math.sin(la2) - math.sin(la1) * math.cos(la2) * math.cos(lo2 - lo1)
    return (math.degrees(math.atan2(y, x)) + 360) % 360


def destination(a, brg, mi):
    d = mi / R_MI
    la1, lo1, t = math.radians(a[0]), math.radians(a[1]), math.radians(brg)
    la2 = math.asin(math.sin(la1) * math.cos(d) + math.cos(la1) * math.sin(d) * math.cos(t))
    lo2 = lo1 + math.atan2(math.sin(t) * math.sin(d) * math.cos(la1), math.cos(d) - math.sin(la1) * math.sin(la2))
    return [round(math.degrees(la2), 5), round(math.degrees(lo2), 5)]


def back_bearing(b):
    return (b + 180) % 360


# Simplified state polygons as (lat, lon) rings.
STATES = {
    "WA": [(49, -123.3), (48.4, -124.7), (46.25, -124.05), (45.7, -120.7), (46, -119), (46, -117.03), (49, -117.03)],
    "OR": [(46.25, -124.05), (45.7, -120.7), (46, -119), (46, -116.9), (45.5, -116.5), (44, -117.0), (42, -117.03), (42, -124.2)],
    "CA": [(42, -124.2), (42, -120), (39, -120), (35, -114.6), (32.7, -114.72), (32.53, -117.12), (33.5, -117.8), (34.4, -120.5), (35.6, -121.2), (36.9, -122.0), (38, -123.0), (39.5, -123.8), (40.4, -124.4)],
    "NV": [(42, -120), (42, -114.05), (36.2, -114.05), (35, -114.6), (39, -120)],
    "ID": [(49, -117.03), (49, -116.05), (47.9, -116.05), (46.6, -114.4), (45.6, -114.5), (44.5, -112.9), (44.5, -111.05), (42, -111.05), (42, -117.03), (44, -117.0), (45.5, -116.5), (46, -116.9), (46, -117.03)],
    "MT": [(49, -116.05), (49, -104.05), (45, -104.05), (45, -111.05), (44.5, -111.05), (44.5, -112.9), (45.6, -114.5), (46.6, -114.4), (47.9, -116.05)],
    "WY": [(45, -111.05), (45, -104.05), (41, -104.05), (41, -111.05)],
    "UT": [(42, -114.05), (42, -111.05), (41, -111.05), (41, -109.05), (37, -109.05), (37, -114.05)],
    "CO": [(41, -109.05), (41, -102.05), (37, -102.05), (37, -109.05)],
    "AZ": [(37, -114.05), (37, -109.05), (31.33, -109.05), (31.33, -111.07), (32.5, -114.8), (32.7, -114.72), (35, -114.6), (36.2, -114.05)],
    "NM": [(37, -109.05), (37, -103), (32, -103), (32, -106.6), (31.78, -106.5), (31.78, -108.2), (31.33, -108.2), (31.33, -109.05)],
    "SD": [(46, -104.05), (46, -96.6), (43, -96.5), (43, -104.05)],
    "ND": [(49, -104.05), (49, -97.2), (46, -96.6), (46, -104.05)],
    "NE": [(43, -104.05), (43, -96.5), (40, -95.3), (40, -102.05), (41, -102.05), (41, -104.05)],
}
STATE_NAMES = {"WA": "Washington", "OR": "Oregon", "CA": "California", "NV": "Nevada", "ID": "Idaho", "MT": "Montana", "WY": "Wyoming", "UT": "Utah", "CO": "Colorado", "AZ": "Arizona", "NM": "New Mexico", "SD": "South Dakota", "ND": "North Dakota", "NE": "Nebraska", "AK": "Alaska"}


def point_in_poly(pt, poly):
    x, y = pt[1], pt[0]
    inside = False
    n = len(poly)
    for i in range(n):
        y1, x1 = poly[i]
        y2, x2 = poly[(i + 1) % n]
        if (y1 > y) != (y2 > y):
            xi = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
            if x < xi:
                inside = not inside
    return inside


def state_of(lat, lon):
    if lat is None or lon is None:
        return None
    if lat > 51:
        return "AK"
    for k, poly in STATES.items():
        if point_in_poly((lat, lon), poly):
            return k
    return None


def bbox_of(points):
    lats = [p[0] for p in points]
    lons = [p[1] for p in points]
    return [min(lats), min(lons), max(lats), max(lons)]


def in_bbox(lat, lon, bbox):
    return bbox[0] <= lat <= bbox[2] and bbox[1] <= lon <= bbox[3]


def bbox_center(bbox):
    return [(bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2]
