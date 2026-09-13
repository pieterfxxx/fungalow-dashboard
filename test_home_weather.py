import json
import requests
from datetime import datetime
from config import HOME


def weather_description(code):
    descriptions = {
        0: "Helder",
        1: "Overwegend helder",
        2: "Licht bewolkt",
        3: "Bewolkt",
        45: "Mist",
        48: "Aanzettende mist",
        51: "Lichte motregen",
        53: "Motregen",
        55: "Zware motregen",
        56: "Lichte ijzel",
        57: "Zware ijzel",
        61: "Lichte regen",
        63: "Regen",
        65: "Zware regen",
        66: "Lichte ijzelregen",
        67: "Zware ijzelregen",
        71: "Lichte sneeuw",
        73: "Sneeuw",
        75: "Zware sneeuw",
        77: "Sneeuwkorrels",
        80: "Lichte buien",
        81: "Buien",
        82: "Zware buien",
        85: "Lichte sneeuwbuien",
        86: "Zware sneeuwbuien",
        95: "Onweer",
        96: "Onweer met lichte hagel",
        99: "Onweer met zware hagel",
    }

    return descriptions.get(code, "Onbekend")


def wind_direction(degrees):
    directions = [
        "N", "NNO", "NO", "ONO",
        "O", "OZO", "ZO", "ZZO",
        "Z", "ZZW", "ZW", "WZW",
        "W", "WNW", "NW", "NNW"
    ]

    index = round(degrees / 22.5) % 16

    return directions[index]


def format_date(date_string):
    days = [
        "Maandag",
        "Dinsdag",
        "Woensdag",
        "Donderdag",
        "Vrijdag",
        "Zaterdag",
        "Zondag"
    ]

    months = [
        "januari",
        "februari",
        "maart",
        "april",
        "mei",
        "juni",
        "juli",
        "augustus",
        "september",
        "oktober",
        "november",
        "december"
    ]

    date = datetime.fromisoformat(date_string)

    return (
        f"{days[date.weekday()]} "
        f"{date.day} "
        f"{months[date.month - 1]}"
    )


def format_time(datetime_string):
    date = datetime.fromisoformat(datetime_string)

    return date.strftime("%H:%M")


def daytime_weather_code(date_string, hourly, fallback_code):
    """
    Kies voor de dagvoorspelling de weersituatie die het dichtst
    bij 14:00 lokale tijd ligt. Daardoor wordt ochtendmist niet
    automatisch het label voor de hele dag.
    """

    times = hourly.get("time", [])
    codes = hourly.get("weather_code", [])

    target = datetime.fromisoformat(f"{date_string}T14:00")

    candidates = []

    for time_string, code in zip(times, codes):
        if time_string.startswith(date_string):
            time_value = datetime.fromisoformat(time_string)
            difference = abs(
                (time_value - target).total_seconds()
            )
            candidates.append((difference, code))

    if candidates:
        return min(candidates, key=lambda item: item[0])[1]

    return fallback_code


def forecast_weather_description(code):
    """
    Dagvriendelijke omschrijving voor de voorspelling.
    Overdag klinkt 'Zonnig' natuurlijker dan 'Helder'.
    """

    daytime_descriptions = {
        0: "Zonnig",
        1: "Overwegend zonnig",
    }

    return daytime_descriptions.get(
        code,
        weather_description(code)
    )


def beaufort(wind_kmh):
    if wind_kmh < 2:
        return 0
    if wind_kmh < 6:
        return 1
    if wind_kmh < 12:
        return 2
    if wind_kmh < 20:
        return 3
    if wind_kmh < 29:
        return 4
    if wind_kmh < 39:
        return 5
    if wind_kmh < 50:
        return 6
    if wind_kmh < 62:
        return 7
    if wind_kmh < 75:
        return 8
    if wind_kmh < 89:
        return 9
    if wind_kmh < 103:
        return 10
    if wind_kmh < 118:
        return 11
    return 12


# --------------------------------------------------
# LOCATIE
# --------------------------------------------------

lat = HOME["lat"]
lon = HOME["lon"]


# --------------------------------------------------
# OPEN-METEO API
# --------------------------------------------------

url = (
    "https://api.open-meteo.com/v1/forecast"
    f"?latitude={lat}"
    f"&longitude={lon}"

    "&current="
    "temperature_2m,"
    "apparent_temperature,"
    "relative_humidity_2m,"
    "precipitation,"
    "precipitation_probability,"
    "wind_speed_10m,"
    "wind_direction_10m,"
    "wind_gusts_10m,"
    "weather_code,"
    "visibility,"
    "surface_pressure,"
    "uv_index"

    "&hourly="
    "weather_code"

    "&daily="
    "weather_code,"
    "temperature_2m_max,"
    "temperature_2m_min,"
    "precipitation_probability_max,"
    "wind_speed_10m_max,"
    "wind_direction_10m_dominant,"
    "sunrise,"
    "sunset"

    "&timezone=Europe%2FLisbon"
    "&forecast_days=4"
)


# --------------------------------------------------
# DATA OPHALEN
# --------------------------------------------------

response = requests.get(url, timeout=20)
response.raise_for_status()

data = response.json()

current = data["current"]
hourly = data["hourly"]
daily = data["daily"]


# --------------------------------------------------
# ACTUEEL WEER
# --------------------------------------------------

current_weather = {
    "temperature": f"{current['temperature_2m']:.1f}°C",

    "condition": weather_description(
        current["weather_code"]
    ),

    "feels_like": f"{current['apparent_temperature']:.1f}°C",

    "humidity": f"{current['relative_humidity_2m']:.0f}%",

    "wind": (
        f"{current['wind_speed_10m']:.1f} km/u "
        f"{wind_direction(current['wind_direction_10m'])}"
    ),

    "wind_force": f"{beaufort(current['wind_speed_10m'])} Bft",

    "wind_gusts": f"{current['wind_gusts_10m']:.1f} km/u",

    "rain_probability": f"{current['precipitation_probability']:.0f}%",

    "rain_amount": f"{current['precipitation']:.1f} mm",

    "visibility": f"{current['visibility'] / 1000:.1f} km",

    "pressure": f"{current['surface_pressure']:.0f} hPa",

    "uv_index": f"{current['uv_index']:.0f}",

    "sunrise": format_time(
        daily["sunrise"][0]
    ),

    "sunset": format_time(
        daily["sunset"][0]
    ),
}


# --------------------------------------------------
# KOMENDE 3 DAGEN
# --------------------------------------------------

forecast = []

for i in range(1, 4):

    forecast.append({
        "day": format_date(
            daily["time"][i]
        ),

        "weather": forecast_weather_description(
            daytime_weather_code(
                daily["time"][i],
                hourly,
                daily["weather_code"][i]
            )
        ),

        "temp": (
            f"{daily['temperature_2m_min'][i]:.1f}° / "
            f"{daily['temperature_2m_max'][i]:.1f}°"
        ),

        "wind": (
            f"{daily['wind_speed_10m_max'][i]:.1f} km/u "
            f"{wind_direction(daily['wind_direction_10m_dominant'][i])}"
        ),

        "precipitation_probability": (
            f"{daily['precipitation_probability_max'][i]:.0f}%"
        )
    })


# --------------------------------------------------
# RESULTAAT VOOR DASHBOARD
# --------------------------------------------------

result = {
    **current_weather,
    "forecast": forecast
}


# --------------------------------------------------
# JSON UITVOER
# --------------------------------------------------

print(
    json.dumps(
        result,
        ensure_ascii=False
    )
)