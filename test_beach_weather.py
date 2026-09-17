import json
from pathlib import Path

import requests

from config import BEACHES


# ============================================================
# OPEN-METEO
# ============================================================

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"


# ============================================================
# WEEROMSCHRIJVINGEN
# ============================================================

WEATHER_CODES = {
    0: "Helder",
    1: "Overwegend helder",
    2: "Half bewolkt",
    3: "Bewolkt",

    45: "Mist",
    48: "Aanzettende mist",

    51: "Lichte motregen",
    53: "Matige motregen",
    55: "Zware motregen",

    56: "Lichte ijzel",
    57: "Zware ijzel",

    61: "Lichte regen",
    63: "Matige regen",
    65: "Zware regen",

    66: "Lichte ijzelregen",
    67: "Zware ijzelregen",

    71: "Lichte sneeuw",
    73: "Matige sneeuw",
    75: "Zware sneeuw",
    77: "Sneeuwkorrels",

    80: "Lichte buien",
    81: "Matige buien",
    82: "Zware buien",

    85: "Lichte sneeuwbuien",
    86: "Zware sneeuwbuien",

    95: "Onweer",
    96: "Onweer met lichte hagel",
    99: "Onweer met zware hagel",
}


# ============================================================
# HULPFUNCTIES
# ============================================================

def wind_direction_to_text(degrees):
    """Zet windrichting in graden om naar N, NO, O, etc."""

    if degrees is None:
        return "Onbekend"

    directions = [
        "N", "NNO", "NO", "ONO",
        "O", "OZO", "ZO", "ZZO",
        "Z", "ZZW", "ZW", "WZW",
        "W", "WNW", "NW", "NNW",
    ]

    index = int((float(degrees) + 11.25) / 22.5) % 16

    return directions[index]


# ============================================================
# ALLE STRANDEN IN ÉÉN API-AANVRAAG
# ============================================================

def get_all_beach_weather():

    latitudes = ",".join(
        str(beach["lat"])
        for beach in BEACHES
    )

    longitudes = ",".join(
        str(beach["lon"])
        for beach in BEACHES
    )

    params = {
        "latitude": latitudes,
        "longitude": longitudes,

        "current": ",".join([
            "temperature_2m",
            "weather_code",
            "is_day",
            "wind_speed_10m",
            "wind_direction_10m",
            "wind_gusts_10m",
            "precipitation",
        ]),

        "daily": ",".join([
            "temperature_2m_min",
            "temperature_2m_max",
            "precipitation_probability_max",
            "precipitation_sum",
        ]),

        "forecast_days": 1,

        "timezone": "Europe/Lisbon",

        "wind_speed_unit": "kmh",
        "temperature_unit": "celsius",
        "precipitation_unit": "mm",
    }

    response = requests.get(
        OPEN_METEO_URL,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    # Bij meerdere locaties geeft Open-Meteo een lijst terug.
    if not isinstance(data, list):
        data = [data]

    return data


# ============================================================
# VERWERK DATA PER STRAND
# ============================================================

def process_beach_weather(beach, data):

    current = data.get("current", {})
    daily = data.get("daily", {})

    weather_code = current.get("weather_code")

    return {
        "coordinates": {
            "lat": beach["lat"],
            "lon": beach["lon"],
        },

        "current": {
            "temperature": current.get("temperature_2m"),

            "weather_code": weather_code,
            "is_day": current.get("is_day"),
            "weather": WEATHER_CODES.get(
                weather_code,
                f"Onbekend ({weather_code})"
            ),

            "wind_speed": current.get(
                "wind_speed_10m"
            ),

            "wind_direction_degrees": current.get(
                "wind_direction_10m"
            ),

            "wind_direction": wind_direction_to_text(
                current.get("wind_direction_10m")
            ),

            "wind_gusts": current.get(
                "wind_gusts_10m"
            ),

            "precipitation": current.get(
                "precipitation"
            ),
        },

        "today": {
            "temp_min": daily.get(
                "temperature_2m_min",
                [None]
            )[0],

            "temp_max": daily.get(
                "temperature_2m_max",
                [None]
            )[0],

            "rain_probability": daily.get(
                "precipitation_probability_max",
                [None]
            )[0],

            "rain_mm": daily.get(
                "precipitation_sum",
                [None]
            )[0],
        },

        "updated": current.get("time"),
    }


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 75)
    print("OPEN-METEO STRAND-WEERTEST")
    print("=" * 75)

    print()
    print(
        f"Alle {len(BEACHES)} stranden "
        f"in één API-aanvraag ophalen..."
    )

    try:
        all_data = get_all_beach_weather()

    except Exception as error:
        print()
        print(f"FOUT bij Open-Meteo: {error}")
        return

    print("Data succesvol ontvangen.")

    # Hier verzamelen we alle resultaten voor de JSON.
    results = {}

    # De volgorde van de API-resultaten komt overeen
    # met de volgorde van de verstuurde coördinaten.
    for beach, data in zip(BEACHES, all_data):

        result = process_beach_weather(
            beach,
            data
        )

        # Opslaan onder de naam van het strand.
        results[beach["name"]] = result

        current = result["current"]
        today = result["today"]

        print()
        print(f"Strand: {beach['name']}")
        print("-" * 75)

        print(
            f"Coördinaten: "
            f"{beach['lat']}, "
            f"{beach['lon']}"
        )

        print()
        print("ACTUEEL")

        print(
            f"  Temperatuur: "
            f"{current['temperature']} °C"
        )

        print(
            f"  Weer: "
            f"{current['weather']}"
        )

        print(
            f"  Wind: "
            f"{current['wind_speed']} km/u "
            f"uit {current['wind_direction']}"
        )

        print(
            f"  Windvlagen: "
            f"{current['wind_gusts']} km/u"
        )

        print(
            f"  Neerslag nu: "
            f"{current['precipitation']} mm"
        )

        print()
        print("VANDAAG")

        print(
            f"  Temperatuur: "
            f"{today['temp_min']}° / "
            f"{today['temp_max']}°"
        )

        print(
            f"  Regenkans: "
            f"{today['rain_probability']}%"
        )

        print(
            f"  Verwachte regen: "
            f"{today['rain_mm']} mm"
        )

    # ========================================================
    # OPSLAAN ALS JSON
    # ========================================================

    data_folder = Path("data")
    data_folder.mkdir(exist_ok=True)

    output_file = data_folder / "beach_weather.json"

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            results,
            f,
            ensure_ascii=False,
            indent=4
        )

    # ========================================================
    # KLAAR
    # ========================================================

    print()
    print("=" * 75)
    print(
        f"KLAAR: {len(results)} van "
        f"{len(BEACHES)} stranden opgehaald."
    )
    print(f"JSON opgeslagen: {output_file}")
    print("=" * 75)


if __name__ == "__main__":
    main()
