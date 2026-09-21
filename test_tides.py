import requests
import json
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from config import TIDECHECK_API_KEY


# ==============================
# INSTELLINGEN
# ==============================

STATION_ID = "fes2022-lourinhã"
STATION_NAME = "Lourinhã"

LOCAL_TZ = ZoneInfo("Europe/Lisbon")


def parse_time(time_string):
    """Zet een TideCheck tijd om naar lokale Portugal-tijd."""
    dt = datetime.fromisoformat(
        time_string.replace("Z", "+00:00")
    )
    return dt.astimezone(LOCAL_TZ)


def format_time(dt):
    return dt.strftime("%H:%M")


# ==============================
# GETIJDENDATA OPHALEN
# ==============================

headers = {
    "X-API-Key": TIDECHECK_API_KEY
}

tides_url = f"https://tidecheck.com/api/station/{STATION_ID}/tides"

print("Getijdendata ophalen...")
print("Station:", STATION_NAME)
print("Station ID:", STATION_ID)

response = requests.get(
    tides_url,
    params={
        "days": 2
    },
    headers=headers,
    timeout=20
)

response.raise_for_status()

data = response.json()


# ==============================
# GRAFIEKDATA VERWERKEN
# ==============================

points = []

for point in data.get("timeSeries", []):
    points.append({
        "time": parse_time(point["time"]),
        "height": float(point["height"])
    })

points.sort(key=lambda x: x["time"])

now = datetime.now(LOCAL_TZ)

start_time = now - timedelta(hours=12)
end_time = now + timedelta(hours=12)

window = [
    point
    for point in points
    if start_time <= point["time"] <= end_time
]

if not window:
    raise ValueError("Geen grafiekpunten gevonden voor dit tijdvenster.")


# ==============================
# HUIDIGE HOOGTE
# ==============================

current_point = min(
    points,
    key=lambda point: abs(point["time"] - now)
)

current_height = current_point["height"]


# ==============================
# STATUS
# ==============================

current_index = points.index(current_point)

if current_index < len(points) - 1:
    next_point = points[current_index + 1]

    if next_point["height"] > current_height:
        tide_direction = "Opkomend"
    elif next_point["height"] < current_height:
        tide_direction = "Aflopend"
    else:
        tide_direction = "Stabiel"
else:
    tide_direction = "Onbekend"


# ==============================
# HOOG- EN LAAGWATER
# ==============================

extremes = []

for event in data.get("extremes", []):
    extremes.append({
        "time": parse_time(event["localTime"]),
        "type": event["type"].upper(),
        "height": float(event["height"])
    })

extremes.sort(key=lambda x: x["time"])

previous_extreme = None
next_extreme = None

for event in extremes:
    if event["time"] <= now:
        previous_extreme = event
    elif event["time"] > now and next_extreme is None:
        next_extreme = event


# ==============================
# VOLGENDE VLOED EN EB
# ==============================

next_high = next(
    (
        event
        for event in extremes
        if event["time"] > now and event["type"] == "HIGH"
    ),
    None
)

next_low = next(
    (
        event
        for event in extremes
        if event["time"] > now and event["type"] == "LOW"
    ),
    None
)


# ==============================
# RESULTAAT VOOR DASHBOARD
# ==============================

result = {
    "station": STATION_NAME,
    "current_height": f"{current_height:.2f} m",
    "direction": tide_direction,
    "next_high": (
        {
            "time": format_time(next_high["time"]),
            "height": f"{next_high['height']:.2f} m"
        }
        if next_high
        else None
    ),
    "next_low": (
        {
            "time": format_time(next_low["time"]),
            "height": f"{next_low['height']:.2f} m"
        }
        if next_low
        else None
    )
}

print(json.dumps(result, ensure_ascii=False))
