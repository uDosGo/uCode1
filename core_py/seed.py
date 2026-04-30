#!/usr/bin/env python3
"""
Seed Pod — Default data initialization for uCode1.
Creates a binder 'city-index' with cities of the world organized by timezone.
Provides location lookup based on system clock detection.

Location string format: <city>, <country> [<tz>] @<lat>,<lon>
Example: London, United Kingdom [Europe/London] @51.5,-0.1
"""

import json
import os
import zoneinfo
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ── City Index by Timezone ──────────────────────────────────────────────────
# Key cities per timezone region with uCode location strings

CITIES_BY_TZ: Dict[str, List[Dict[str, Any]]] = {
    # UTC-11 to UTC-9 — Pacific
    "Pacific/Midway": [
        {"city": "Midway", "country": "US Minor Outlying Islands", "lat": 28.2, "lon": -177.4, "tz": "Pacific/Midway"},
        {"city": "Pago Pago", "country": "American Samoa", "lat": -14.3, "lon": -170.7, "tz": "Pacific/Pago_Pago"},
    ],
    "Pacific/Honolulu": [
        {"city": "Honolulu", "country": "United States", "lat": 21.3, "lon": -157.8, "tz": "Pacific/Honolulu"},
    ],
    # UTC-8 — Pacific Time
    "America/Los_Angeles": [
        {"city": "Los Angeles", "country": "United States", "lat": 34.1, "lon": -118.2, "tz": "America/Los_Angeles"},
        {"city": "San Francisco", "country": "United States", "lat": 37.8, "lon": -122.4, "tz": "America/Los_Angeles"},
        {"city": "Vancouver", "country": "Canada", "lat": 49.3, "lon": -123.1, "tz": "America/Vancouver"},
        {"city": "Seattle", "country": "United States", "lat": 47.6, "lon": -122.3, "tz": "America/Los_Angeles"},
    ],
    # UTC-7 — Mountain Time
    "America/Denver": [
        {"city": "Denver", "country": "United States", "lat": 39.7, "lon": -104.9, "tz": "America/Denver"},
        {"city": "Phoenix", "country": "United States", "lat": 33.4, "lon": -112.0, "tz": "America/Phoenix"},
        {"city": "Salt Lake City", "country": "United States", "lat": 40.8, "lon": -111.9, "tz": "America/Denver"},
    ],
    # UTC-6 — Central Time
    "America/Chicago": [
        {"city": "Chicago", "country": "United States", "lat": 41.9, "lon": -87.6, "tz": "America/Chicago"},
        {"city": "Dallas", "country": "United States", "lat": 32.8, "lon": -96.8, "tz": "America/Chicago"},
        {"city": "Houston", "country": "United States", "lat": 29.8, "lon": -95.4, "tz": "America/Chicago"},
        {"city": "Mexico City", "country": "Mexico", "lat": 19.4, "lon": -99.1, "tz": "America/Mexico_City"},
    ],
    # UTC-5 — Eastern Time
    "America/New_York": [
        {"city": "New York", "country": "United States", "lat": 40.7, "lon": -74.0, "tz": "America/New_York"},
        {"city": "Toronto", "country": "Canada", "lat": 43.7, "lon": -79.4, "tz": "America/Toronto"},
        {"city": "Miami", "country": "United States", "lat": 25.8, "lon": -80.2, "tz": "America/New_York"},
        {"city": "Washington DC", "country": "United States", "lat": 38.9, "lon": -77.0, "tz": "America/New_York"},
        {"city": "Bogota", "country": "Colombia", "lat": 4.6, "lon": -74.1, "tz": "America/Bogota"},
        {"city": "Lima", "country": "Peru", "lat": -12.0, "lon": -77.0, "tz": "America/Lima"},
    ],
    # UTC-4 — Atlantic / Caracas
    "America/Halifax": [
        {"city": "Halifax", "country": "Canada", "lat": 44.6, "lon": -63.6, "tz": "America/Halifax"},
        {"city": "Caracas", "country": "Venezuela", "lat": 10.5, "lon": -66.9, "tz": "America/Caracas"},
        {"city": "Santiago", "country": "Chile", "lat": -33.5, "lon": -70.7, "tz": "America/Santiago"},
    ],
    # UTC-3 — Brasilia / Buenos Aires
    "America/Sao_Paulo": [
        {"city": "Sao Paulo", "country": "Brazil", "lat": -23.5, "lon": -46.6, "tz": "America/Sao_Paulo"},
        {"city": "Buenos Aires", "country": "Argentina", "lat": -34.6, "lon": -58.4, "tz": "America/Argentina/Buenos_Aires"},
        {"city": "Rio de Janeiro", "country": "Brazil", "lat": -22.9, "lon": -43.2, "tz": "America/Sao_Paulo"},
        {"city": "Montevideo", "country": "Uruguay", "lat": -34.9, "lon": -56.2, "tz": "America/Montevideo"},
    ],
    # UTC+0 — UTC / London
    "Europe/London": [
        {"city": "London", "country": "United Kingdom", "lat": 51.5, "lon": -0.1, "tz": "Europe/London"},
        {"city": "Dublin", "country": "Ireland", "lat": 53.3, "lon": -6.2, "tz": "Europe/Dublin"},
        {"city": "Lisbon", "country": "Portugal", "lat": 38.7, "lon": -9.1, "tz": "Europe/Lisbon"},
        {"city": "Reykjavik", "country": "Iceland", "lat": 64.1, "lon": -21.9, "tz": "Atlantic/Reykjavik"},
        {"city": "Accra", "country": "Ghana", "lat": 5.6, "lon": -0.2, "tz": "Africa/Accra"},
    ],
    # UTC+1 — CET
    "Europe/Paris": [
        {"city": "Paris", "country": "France", "lat": 48.9, "lon": 2.3, "tz": "Europe/Paris"},
        {"city": "Berlin", "country": "Germany", "lat": 52.5, "lon": 13.4, "tz": "Europe/Berlin"},
        {"city": "Rome", "country": "Italy", "lat": 41.9, "lon": 12.5, "tz": "Europe/Rome"},
        {"city": "Madrid", "country": "Spain", "lat": 40.4, "lon": -3.7, "tz": "Europe/Madrid"},
        {"city": "Amsterdam", "country": "Netherlands", "lat": 52.4, "lon": 4.9, "tz": "Europe/Amsterdam"},
        {"city": "Brussels", "country": "Belgium", "lat": 50.8, "lon": 4.4, "tz": "Europe/Brussels"},
        {"city": "Zurich", "country": "Switzerland", "lat": 47.4, "lon": 8.5, "tz": "Europe/Zurich"},
        {"city": "Stockholm", "country": "Sweden", "lat": 59.3, "lon": 18.1, "tz": "Europe/Stockholm"},
        {"city": "Oslo", "country": "Norway", "lat": 59.9, "lon": 10.8, "tz": "Europe/Oslo"},
        {"city": "Copenhagen", "country": "Denmark", "lat": 55.7, "lon": 12.6, "tz": "Europe/Copenhagen"},
        {"city": "Vienna", "country": "Austria", "lat": 48.2, "lon": 16.4, "tz": "Europe/Vienna"},
        {"city": "Warsaw", "country": "Poland", "lat": 52.2, "lon": 21.0, "tz": "Europe/Warsaw"},
        {"city": "Prague", "country": "Czech Republic", "lat": 50.1, "lon": 14.4, "tz": "Europe/Prague"},
    ],
    # UTC+2 — EET
    "Europe/Helsinki": [
        {"city": "Helsinki", "country": "Finland", "lat": 60.2, "lon": 24.9, "tz": "Europe/Helsinki"},
        {"city": "Athens", "country": "Greece", "lat": 38.0, "lon": 23.7, "tz": "Europe/Athens"},
        {"city": "Istanbul", "country": "Turkey", "lat": 41.0, "lon": 29.0, "tz": "Europe/Istanbul"},
        {"city": "Cairo", "country": "Egypt", "lat": 30.0, "lon": 31.2, "tz": "Africa/Cairo"},
        {"city": "Kyiv", "country": "Ukraine", "lat": 50.5, "lon": 30.5, "tz": "Europe/Kyiv"},
        {"city": "Bucharest", "country": "Romania", "lat": 44.4, "lon": 26.1, "tz": "Europe/Bucharest"},
        {"city": "Jerusalem", "country": "Israel", "lat": 31.8, "lon": 35.2, "tz": "Asia/Jerusalem"},
        {"city": "Johannesburg", "country": "South Africa", "lat": -26.2, "lon": 28.0, "tz": "Africa/Johannesburg"},
    ],
    # UTC+3 — Moscow / East Africa
    "Europe/Moscow": [
        {"city": "Moscow", "country": "Russia", "lat": 55.8, "lon": 37.6, "tz": "Europe/Moscow"},
        {"city": "Nairobi", "country": "Kenya", "lat": -1.3, "lon": 36.8, "tz": "Africa/Nairobi"},
        {"city": "Addis Ababa", "country": "Ethiopia", "lat": 9.0, "lon": 38.7, "tz": "Africa/Addis_Ababa"},
        {"city": "Riyadh", "country": "Saudi Arabia", "lat": 24.7, "lon": 46.7, "tz": "Asia/Riyadh"},
        {"city": "Dubai", "country": "UAE", "lat": 25.2, "lon": 55.3, "tz": "Asia/Dubai"},
    ],
    # UTC+4 to UTC+5 — South Asia
    "Asia/Karachi": [
        {"city": "Karachi", "country": "Pakistan", "lat": 24.9, "lon": 67.0, "tz": "Asia/Karachi"},
        {"city": "Mumbai", "country": "India", "lat": 19.1, "lon": 72.9, "tz": "Asia/Kolkata"},
        {"city": "Delhi", "country": "India", "lat": 28.6, "lon": 77.2, "tz": "Asia/Kolkata"},
        {"city": "Colombo", "country": "Sri Lanka", "lat": 6.9, "lon": 79.9, "tz": "Asia/Colombo"},
        {"city": "Dhaka", "country": "Bangladesh", "lat": 23.7, "lon": 90.4, "tz": "Asia/Dhaka"},
    ],
    # UTC+6 to UTC+7 — Southeast Asia
    "Asia/Bangkok": [
        {"city": "Bangkok", "country": "Thailand", "lat": 13.8, "lon": 100.5, "tz": "Asia/Bangkok"},
        {"city": "Ho Chi Minh City", "country": "Vietnam", "lat": 10.8, "lon": 106.7, "tz": "Asia/Ho_Chi_Minh"},
        {"city": "Jakarta", "country": "Indonesia", "lat": -6.2, "lon": 106.8, "tz": "Asia/Jakarta"},
        {"city": "Singapore", "country": "Singapore", "lat": 1.3, "lon": 103.8, "tz": "Asia/Singapore"},
    ],
    # UTC+8 — China / Western Australia
    "Asia/Shanghai": [
        {"city": "Shanghai", "country": "China", "lat": 31.2, "lon": 121.5, "tz": "Asia/Shanghai"},
        {"city": "Beijing", "country": "China", "lat": 39.9, "lon": 116.4, "tz": "Asia/Shanghai"},
        {"city": "Hong Kong", "country": "China", "lat": 22.3, "lon": 114.2, "tz": "Asia/Hong_Kong"},
        {"city": "Taipei", "country": "Taiwan", "lat": 25.0, "lon": 121.5, "tz": "Asia/Taipei"},
        {"city": "Perth", "country": "Australia", "lat": -31.9, "lon": 115.9, "tz": "Australia/Perth"},
        {"city": "Kuala Lumpur", "country": "Malaysia", "lat": 3.1, "lon": 101.7, "tz": "Asia/Kuala_Lumpur"},
        {"city": "Manila", "country": "Philippines", "lat": 14.6, "lon": 121.0, "tz": "Asia/Manila"},
    ],
    # UTC+9 — Japan / Korea
    "Asia/Tokyo": [
        {"city": "Tokyo", "country": "Japan", "lat": 35.7, "lon": 139.7, "tz": "Asia/Tokyo"},
        {"city": "Osaka", "country": "Japan", "lat": 34.7, "lon": 135.5, "tz": "Asia/Tokyo"},
        {"city": "Seoul", "country": "South Korea", "lat": 37.6, "lon": 127.0, "tz": "Asia/Seoul"},
        {"city": "Pyongyang", "country": "North Korea", "lat": 39.0, "lon": 125.7, "tz": "Asia/Pyongyang"},
    ],
    # UTC+10 to UTC+12 — Australia / Pacific
    "Australia/Sydney": [
        {"city": "Sydney", "country": "Australia", "lat": -33.9, "lon": 151.2, "tz": "Australia/Sydney"},
        {"city": "Melbourne", "country": "Australia", "lat": -37.8, "lon": 145.0, "tz": "Australia/Melbourne"},
        {"city": "Brisbane", "country": "Australia", "lat": -27.5, "lon": 153.0, "tz": "Australia/Brisbane"},
        {"city": "Auckland", "country": "New Zealand", "lat": -36.8, "lon": 174.8, "tz": "Pacific/Auckland"},
        {"city": "Suva", "country": "Fiji", "lat": -18.1, "lon": 178.4, "tz": "Pacific/Fiji"},
    ],
}

# ── All cities flat list for binder storage ────────────────────────────────

ALL_CITIES: List[Dict[str, Any]] = []
for tz_name, cities in CITIES_BY_TZ.items():
    for c in cities:
        c["location_string"] = f'{c["city"]}, {c["country"]} [{c["tz"]}] @{c["lat"]},{c["lon"]}'
        ALL_CITIES.append(c)


def location_string(city: Dict[str, Any]) -> str:
    """Format a city entry as a uCode location string."""
    return f'{city["city"]}, {city["country"]} [{city["tz"]}] @{city["lat"]},{city["lon"]}'


# ── Timezone Detection ──────────────────────────────────────────────────────

def detect_timezone() -> str:
    """Detect current timezone from system clock.

    Uses Python's zoneinfo to get the local timezone.
    Falls back to UTC offset matching if IANA name not available.

    Returns:
        IANA timezone string, e.g. 'America/New_York'.
    """
    # Mapping of common abbreviations to IANA keys
    ABBR_MAP = {
        "AEST": "Australia/Sydney",
        "AEDT": "Australia/Sydney",
        "EST": "America/New_York",
        "EDT": "America/New_York",
        "CST": "America/Chicago",
        "CDT": "America/Chicago",
        "MST": "America/Denver",
        "MDT": "America/Denver",
        "PST": "America/Los_Angeles",
        "PDT": "America/Los_Angeles",
        "BST": "Europe/London",
        "CET": "Europe/Paris",
        "CEST": "Europe/Paris",
        "EET": "Europe/Helsinki",
        "EEST": "Europe/Helsinki",
        "MSK": "Europe/Moscow",
        "IST": "Asia/Kolkata",
        "JST": "Asia/Tokyo",
        "KST": "Asia/Seoul",
        "CST_CHINA": "Asia/Shanghai",
        "HKT": "Asia/Hong_Kong",
        "SGT": "Asia/Singapore",
        "WIB": "Asia/Jakarta",
        "ICT": "Asia/Bangkok",
    }

    # Offset-based fallback: offset hours → preferred IANA key
    OFFSET_MAP: Dict[int, str] = {
        -11: "Pacific/Midway",
        -10: "Pacific/Honolulu",
        -8: "America/Los_Angeles",
        -7: "America/Denver",
        -6: "America/Chicago",
        -5: "America/New_York",
        -4: "America/Halifax",
        -3: "America/Sao_Paulo",
        0: "Europe/London",
        1: "Europe/Paris",
        2: "Europe/Helsinki",
        3: "Europe/Moscow",
        5: "Asia/Karachi",
        6: "Asia/Bangkok",
        7: "Asia/Bangkok",
        8: "Asia/Shanghai",
        9: "Asia/Tokyo",
        10: "Australia/Sydney",
        11: "Australia/Sydney",
        12: "Pacific/Auckland",
    }

    try:
        tz = datetime.now().astimezone().tzinfo
        if tz is not None:
            key = str(tz)
            # Direct match
            if key in CITIES_BY_TZ:
                return key
            # Abbreviation match
            if key in ABBR_MAP:
                return ABBR_MAP[key]
            # Fuzzy: check if any known tz ends with same name
            for known_tz in CITIES_BY_TZ:
                if known_tz.endswith(key) or key.endswith(known_tz.split("/")[-1]):
                    return known_tz

        # Fallback: match by UTC offset
        offset = datetime.now().astimezone().utcoffset()
        if offset is not None:
            h = round(offset.total_seconds() / 3600)
            if h in OFFSET_MAP:
                return OFFSET_MAP[h]
        return "UTC"
    except Exception:
        return "UTC"


def local_cities() -> List[Dict[str, Any]]:
    """Get cities matching the detected local timezone.

    Returns:
        List of city dicts in the detected timezone.
    """
    tz = detect_timezone()
    cities = CITIES_BY_TZ.get(tz, [])
    if not cities and tz != "UTC":
        # Fallback: check all known tz keys
        for known_tz, known_cities in CITIES_BY_TZ.items():
            if tz in known_tz or known_tz in tz:
                cities = known_cities
                break
    if not cities:
        cities = CITIES_BY_TZ.get("Europe/London", [])
    return cities


def offset_hours() -> float:
    """Get current UTC offset in hours from system clock."""
    try:
        offset = datetime.now().astimezone().utcoffset()
        if offset is not None:
            return offset.total_seconds() / 3600
    except Exception:
        pass
    return 0.0


# ── Seed Pod Generation ────────────────────────────────────────────────────

def generate_seed_binder() -> dict:
    """Generate the default seed binder 'city-index' with all cities.

    The binder is stored in the Binder JSON format with cities organized
    by timezone as hierarchical entries.

    Returns:
        Binder dict ready for serialization.
    """
    from .binder.models import Binder, BinderEntry, BinderMetadata, BinderResource

    root_children = []
    for tz_name, cities in sorted(CITIES_BY_TZ.items()):
        tz_short = tz_name.split("/")[-1].replace("_", " ")
        city_resources = []
        for c in cities:
            city_resources.append(BinderResource(
                id=f"city-{c['city'].lower().replace(' ', '-')}",
                name=c["city"],
                resource_type="data",
                data={
                    "city": c["city"],
                    "country": c["country"],
                    "lat": c["lat"],
                    "lon": c["lon"],
                    "tz": c["tz"],
                    "location": location_string(c),
                },
            ))
        tz_entry = BinderEntry(
            id=f"tz-{tz_name.replace('/', '-').lower()}",
            name=tz_short,
            entry_type="collection",
            resources=city_resources,
        )
        root_children.append(tz_entry)

    binder = Binder(
        metadata=BinderMetadata(
            id="CITY-INDEX-001",
            name="City Index",
            version="1.0.0",
            description="World cities indexed by timezone — seed pod for uCode1 location handling",
            author="uCode1 Seed Pod",
            tags=["seed", "location", "cities", "timezone"],
        ),
        root=BinderEntry(
            id="root",
            name="Cities of the World",
            entry_type="collection",
            children=root_children,
        ),
    )
    return binder.to_dict()


def save_seed_binder(output_dir: str = ".binders") -> str:
    """Generate and save the seed binder to disk.

    Args:
        output_dir: Directory to save the binder file.

    Returns:
        Path to the saved binder file.
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    binder_dict = generate_seed_binder()
    path = os.path.join(output_dir, "CITY-INDEX-001.binder.json")
    with open(path, "w") as f:
        json.dump(binder_dict, f, indent=2)
    return path


def boot_report() -> dict:
    """Generate a boot report showing seed pod status and local location.

    Called by the BBC BASIC terminal on startup to display seed pod info
    alongside the '64k ram 38911 bytes free' message.

    Returns:
        Dict with boot statistics.
    """
    tz = detect_timezone()
    local = local_cities()
    offset = offset_hours()
    total_cities = len(ALL_CITIES)
    total_tz = len(CITIES_BY_TZ)

    return {
        "timezone": tz,
        "utc_offset": f"UTC{offset:+g}h" if offset != 0 else "UTC",
        "local_cities": [c["city"] for c in local[:5]],
        "local_city_count": len(local),
        "total_cities": total_cities,
        "total_timezones": total_tz,
        "seed_pod": "CITY-INDEX-001",
    }
