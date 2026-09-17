#!/usr/bin/env python3
"""Fungalow web dashboard generator.

This is deliberately separate from dashboard.py. It uses the same
config.py and data scripts, then generates dashboard.html.
"""

import ast
import html
import json
import os
import re
import subprocess
import sys
from datetime import datetime

from config import BEACHES as CONFIG_BEACHES, BEACH_PAIRS

OUTPUT = "dashboard.html"
BEACH_DIR = "static/beaches"
WEATHER_DIR = "static/weather"

META = {
    "Santa Cruz Centro": ("12,9 km", "19 min rijden", "santa_cruz_centro.jpg"),
    "Praia do Peralta": ("5,4 km", "8 min rijden", "peralta.jpg"),
    "Lisboa": ("", "", "lisboa.jpeg"),
    "Nazaré": ("", "", "nazare.jpg"),
    "São Martinho do Porto": ("", "", "saomartinhodoporto.jpg"),
    "Foz do Arelho": ("", "", "fozdoarelho.jpg"),
    "Praia do Areal Sul": ("", "", "areal_sul.jpg"),
}

def esc(value):
    return html.escape(str(value))

def run_script(filename):
    try:
        result = subprocess.run(
            [sys.executable, filename],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode != 0:
            print(f"FOUT bij {filename}: {result.stderr.strip()}")
            return None
        output = result.stdout.strip()
        try:
            return json.loads(output)
        except Exception:
            pass
        for line in reversed(output.splitlines()):
            try:
                return json.loads(line.strip())
            except Exception:
                pass
        try:
            return ast.literal_eval(output)
        except Exception:
            return None
    except Exception as e:
        print(f"FOUT bij {filename}: {e}")
        return None

def normalise(name):
    value = str(name).lower()
    for old, new in {
        "ã":"a","á":"a","à":"a","â":"a","é":"e","ê":"e","í":"i",
        "ó":"o","ô":"o","õ":"o","ú":"u","ü":"u","ç":"c"
    }.items():
        value = value.replace(old, new)
    return re.sub(r"[^a-z0-9]+", "_", value).strip("_")

def beach_image(name):
    if name in META and META[name][2]:
        return META[name][2]
    base = normalise(name)
    for ext in (".jpg", ".jpeg", ".png"):
        if os.path.exists(os.path.join(BEACH_DIR, base + ext)):
            return base + ext
    return base + ".jpg"

def weather_icon(condition, is_day=1):
    c = str(condition).lower()
    night = str(is_day) == "0"

    rules = [
        (["onweer","trovoada","thunder"], "thunderstorms-day-rain.svg"),
        (["zware regen","extreme rain"], "extreme-rain.svg"),
        (["motregen","chuvisco","drizzle"], "drizzle.svg"),
        (["buien","aguaceiros","regen","chuva","rain"],
         "partly-cloudy-night-rain.svg" if night else "partly-cloudy-day-rain.svg"),
        (["natte sneeuw","sleet"], "sleet.svg"),
        (["sneeuw","snow"], "snow.svg"),
        (["mist","fog"], "mist.svg"),
        (["nevel","haze"], "haze.svg"),
        (["zwaar bewolkt","zeer bewolkt","overcast","muito nublado"],
         "overcast.svg"),
        (["licht bewolkt","gedeeltelijk bewolkt","partly cloudy","pouco nublado"],
         "partly-cloudy-night.svg" if night else "partly-cloudy-day.svg"),
        (["bewolkt","cloudy","nublado"], "cloudy.svg"),
        (["helder","zonnig","clear","limpo"],
         "clear-night.svg" if night else "clear-day.svg"),
    ]

    for words, filename in rules:
        if any(word in c for word in words):
            return filename

    return "not-available.svg"

def fmt_temp(value):
    try:
        return f"{float(value):.1f}°C"
    except Exception:
        return str(value) + "°C" if value else None

def main():
    # Exact dezelfde data-bronnen als de werkende laptopversie.
    home = run_script("test_home_weather.py") or {}
    info = run_script("test_infoagua.py") or {}
    tides = run_script("test_tides.py") or {}

    print("Open-Meteo strandweer vernieuwen...")
    run_script("test_beach_weather.py")

    try:
        with open("data/beach_weather.json", encoding="utf-8") as f:
            beach_weather = json.load(f)
    except Exception:
        beach_weather = {}

    weather = {
        "temperature":"Niet beschikbaar", "condition":"Niet beschikbaar",
        "is_day": 1,
        "feels_like":"Niet beschikbaar", "humidity":"Niet beschikbaar",
        "wind_force":"Niet beschikbaar", "wind":"Niet beschikbaar",
        "wind_gusts":"Niet beschikbaar", "rain_probability":"Niet beschikbaar",
        "rain_amount":"Niet beschikbaar", "visibility":"Niet beschikbaar",
        "pressure":"Niet beschikbaar", "uv_index":"Niet beschikbaar",
        "sunrise":"Niet beschikbaar", "sunset":"Niet beschikbaar",
    }
    if isinstance(home, dict):
        for key in weather:
            if key in home:
                weather[key] = str(home[key])

    forecast = home.get("forecast", []) if isinstance(home, dict) else []
    if not isinstance(forecast, list) or len(forecast) != 3:
        forecast = [
            {"day":"Niet beschikbaar","weather":"Niet beschikbaar",
             "temp":"Niet beschikbaar","wind":"Niet beschikbaar",
             "precipitation_probability":"Niet beschikbaar"}
        ] * 3

    tide = {"direction":"Niet beschikbaar","next_high":"Niet beschikbaar","next_low":"Niet beschikbaar"}
    if isinstance(tides, dict):
        tide["direction"] = tides.get("direction", tide["direction"])
        for key in ("next_high", "next_low"):
            item = tides.get(key)
            if isinstance(item, dict):
                parts = [str(item.get(k, "")).strip() for k in ("time", "height")]
                tide[key] = " • ".join(x for x in parts if x)

    beaches = []
    for config_beach in CONFIG_BEACHES:
        name = str(config_beach.get("name", "")).strip()
        default_distance, default_drive, _ = META.get(
            name, ("Afstand niet ingesteld", "Rijtijd niet ingesteld", "")
        )
        beach = {
            "name": name.upper(),
            "distance": config_beach.get("distance", default_distance),
            "drive": config_beach.get("drive", default_drive),
            "weather":"Niet beschikbaar", "wind":"Niet beschikbaar",
            "wind_gusts":"Niet beschikbaar", "precipitation":"Niet beschikbaar",
            "rain_probability":"Niet beschikbaar", "rain_mm":"Niet beschikbaar",
            "water":"Niet beschikbaar", "waves":"Niet beschikbaar",
            "status":"Niet beschikbaar", "warning":"Geen actieve waarschuwingen",
            "image": beach_image(name),
            "weather_icon": "not-available.svg",
        }

        live = None
        if isinstance(info, dict):
            for key, value in info.items():
                if key.upper() == beach["name"]:
                    live = value
                    break
        if isinstance(live, dict):
            for key in ("weather","water","waves","status","warning"):
                if key in live:
                    beach[key] = str(live[key])

        om = None
        if isinstance(beach_weather, dict):
            for key, value in beach_weather.items():
                if key.upper() == beach["name"]:
                    om = value
                    break
        if isinstance(om, dict):
            current = om.get("current", {})
            today = om.get("today", {})
            parts = [
                str(current.get("weather", "")).strip(),
                fmt_temp(current.get("temperature"))
            ]
            parts = [x for x in parts if x]
            if today.get("temp_min") is not None and today.get("temp_max") is not None:
                parts += [
                    f"min {fmt_temp(today['temp_min'])}",
                    f"max {fmt_temp(today['temp_max'])}"
                ]
            if parts:
                beach["weather"] = " | ".join(parts)
                beach["weather_icon"] = weather_icon(
                    current.get("weather", ""),
                    current.get("is_day", 1)
                )

            def number(value, suffix=""):
                if value is None or value == "":
                    return "Niet beschikbaar"
                try:
                    n = float(value)
                    text = str(int(n)) if n.is_integer() else f"{n:.1f}"
                    return text + suffix
                except Exception:
                    return str(value) + suffix

            if current.get("wind_speed") is not None:
                beach["wind"] = number(current["wind_speed"], " km/u")
                if current.get("wind_direction"):
                    beach["wind"] += " uit " + str(current["wind_direction"])
            if current.get("wind_gusts") is not None:
                beach["wind_gusts"] = number(current["wind_gusts"], " km/u")
            if current.get("precipitation") is not None:
                beach["precipitation"] = number(current["precipitation"], " mm")
            if today.get("rain_probability") is not None:
                beach["rain_probability"] = number(today["rain_probability"], "%")
            if today.get("rain_mm") is not None:
                beach["rain_mm"] = number(today["rain_mm"], " mm")

        beaches.append(beach)

    lookup = {b["name"]: b for b in beaches}

    slides = []
    for pair in BEACH_PAIRS:
        selected = [lookup[str(name).upper()] for name in pair]
        cards = []
        for beach in selected:
            rows = [
                ("Weer:", beach["weather"]), ("Wind:", beach["wind"]),
                ("Windvlagen:", beach["wind_gusts"]),
                ("Neerslag nu:", beach["precipitation"]),
                ("Regenkans:", beach["rain_probability"]),
                ("Regen vandaag:", beach["rain_mm"]),
                ("Water:", beach["water"]), ("Golven:", beach["waves"]),
                ("Golfstatus:", beach["status"]),
                ("Waarschuwingen:", beach["warning"]),
            ]
            row_html = "".join(
                f'<div class="row"><b>{esc(label)}</b><span>{esc(value)}</span></div>'
                for label, value in rows
            )
            cards.append(
                f"<section class=\"beach\" style=\"background-image:url('static/beaches/{esc(beach['image'])}')\">"
                f'<div class="wash"></div><div class="card">'
                f'<img class="beach-weather-icon" src="static/weather/{esc(beach["weather_icon"])}" alt="">'
                f'<h2>{esc(beach["name"])}</h2>'
                f'<p>{esc(beach["distance"])} &nbsp;•&nbsp; {esc(beach["drive"])}</p>'
                f'{row_html}</div></section>'
            )

        forecast_html = "".join(
            f'<div class="forecast"><b>{esc(item.get("day",""))}</b>'
            f'<img src="static/weather/{esc(weather_icon(weather["condition"], weather.get("is_day", 1)))}">'
            f'<div>{esc(item.get("weather",""))}<small>Wind: {esc(item.get("wind",""))}</small></div>'
            f'<strong>{esc(item.get("temp",""))}<small>Regen: {esc(item.get("precipitation_probability",""))}</small></strong></div>'
            for item in forecast
        )

        groups = [
            ("WIND & REGEN", [
                ("Windkracht", weather["wind_force"]), ("Windsnelheid", weather["wind"]),
                ("Windvlagen", weather["wind_gusts"]), ("Regenkans", weather["rain_probability"]),
                ("Regen", weather["rain_amount"])]),
            ("GETIJ", [
                ("Getij", tide["direction"]), ("Volgende vloed", tide["next_high"]),
                ("Volgende eb", tide["next_low"])]),
            ("ATMOSFEER", [
                ("Luchtvochtigheid", weather["humidity"]), ("Zicht", weather["visibility"]),
                ("Luchtdruk", weather["pressure"])]),
            ("ZON & UV", [
                ("UV-kracht", weather["uv_index"]), ("Zon op", weather["sunrise"]),
                ("Zon onder", weather["sunset"])])
        ]
        group_html = "".join(
            f'<div class="group"><h3>{esc(title)}</h3>' +
            "".join(f'<div class="weather-row"><b>{esc(label)}</b><span>{esc(value)}</span></div>' for label, value in rows) +
            '</div>'
            for title, rows in groups
        )

        slides.append(
            f'<main class="slide"><div class="left">'
            f'<section class="current"><div class="panel"><h2>HUIDIG WEER</h2>'
            f'<div class="summary"><strong>{esc(weather["temperature"])}</strong>'
            f'<div>{esc(weather["condition"])}<small>Gevoel: {esc(weather["feels_like"])}</small></div>'
            f'<img src="static/weather/{esc(weather_icon(weather["condition"], weather.get("is_day", 1)))}"></div>'
            f'<div class="groups">{group_html}</div></div></section>'
            f'<section class="forecastbox"><div class="panel"><h2>WEERSVOORSPELLING</h2>'
            f'{forecast_html}</div></section></div>'
            f'<div class="right">{"".join(cards)}</div></main>'
        )

    date_text = datetime.now().strftime("%A %d %B").lower()
    translations = {
        "monday":"maandag","tuesday":"dinsdag","wednesday":"woensdag",
        "thursday":"donderdag","friday":"vrijdag","saturday":"zaterdag",
        "sunday":"zondag","january":"januari","february":"februari",
        "march":"maart","april":"april","may":"mei","june":"juni",
        "july":"juli","august":"augustus","september":"september",
        "october":"oktober","november":"november","december":"december"
    }
    for english, dutch in translations.items():
        date_text = date_text.replace(english, dutch)

    page = """<!doctype html>
<html lang="nl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>The Fungalow</title>
<style>
*{box-sizing:border-box}html,body{margin:0;background:#eee;color:#232323;font-family:Arial,Calibri,sans-serif}
body{overflow:hidden}.slide{display:none;width:100vw;height:100vh;padding-top:78px;grid-template-columns:1fr 1fr}
.slide.active{display:grid}.left{display:grid;grid-template-rows:60% 40%;min-width:0;background:linear-gradient(#f5f5f588,#f5f5f588),url("static/beaches/fungalow.jpg") center/cover}
.current,.forecastbox{min-width:0;min-height:0}.current{padding:30px 35px;background:transparent;border-bottom:2px solid}
.forecastbox{padding:30px 35px}.panel{height:100%;padding:24px 35px;background:#fafafaB0}
h2{margin:0 0 28px;font-size:clamp(22px,2vw,36px)}.summary{display:flex;gap:30px;position:relative;min-height:205px}
.summary>strong{font-size:clamp(45px,4vw,70px);line-height:1}.summary small,.forecast small{display:block;margin-top:9px;font-size:.8em}
.summary img{position:absolute;right:0;top:-25px;width:clamp(100px,15vw,250px);height:clamp(100px,15vw,250px)}
.groups{display:grid;grid-template-columns:1fr 1fr;gap:25px 40px}.group h3{font-size:clamp(15px,1.3vw,22px);margin:0 0 10px}
.group div{font-size:clamp(13px,1.2vw,22px);line-height:1.55}.group span{margin-left:25px}
.forecast{display:grid;grid-template-columns:100px 65px 1fr auto;gap:14px;align-items:center;min-height:78px}.forecast img{width:60px;height:60px}.forecast strong{text-align:right}
.right{display:grid;grid-template-rows:1fr 1fr;border-left:3px solid}.beach{position:relative;min-width:0;min-height:0;padding:30px;background-size:cover;background-position:center;border-bottom:3px solid}
.beach:last-child{border:0}.wash{position:absolute;inset:0;background:#f5f5f566}.card{position:relative;width:min(800px,100%);height:100%;padding:20px 25px;background:#fafafabe}.beach-weather-icon{position:absolute;right:18px;top:12px;width:90px;height:90px;object-fit:contain;z-index:2}.card h2,.card p,.card .row{position:relative;z-index:1}.beach-weather-icon{position:absolute;right:20px;top:15px;width:clamp(65px,7vw,105px);height:clamp(65px,7vw,105px)}
.card h2{margin:0 0 14px}.card p{font-size:clamp(14px,1.2vw,24px);margin:0 0 25px}.weather-row{display:grid;grid-template-columns:115px 1fr;gap:0;font-size:clamp(13px,1.15vw,22px);line-height:1.55}.weather-row b{font-weight:400}.weather-row span{display:block}.row{display:grid;grid-template-columns:255px 1fr;gap:10px;font-size:clamp(13px,1.15vw,22px);line-height:1.55}
.nav{position:fixed;z-index:5;bottom:12px;left:50%;transform:translateX(-50%);background:#fff;padding:7px 14px;border-radius:20px}button{border:0;background:transparent;font-size:20px}
@media(max-width:800px){
html,body{width:100%;min-width:0;overflow-x:hidden}
body{overflow-y:auto;-webkit-text-size-adjust:100%}
header{height:60px!important;padding:10px 14px!important}
header b{font-size:clamp(17px,5vw,25px)!important;white-space:nowrap}
.slide,.slide.active{display:block;width:100%;height:auto;min-height:0;padding-top:60px}
.slide:not(:first-child) .left{display:none}
.left{display:block;background-position:center top}
.current{min-height:0;padding:16px 12px}
.forecastbox{min-height:0;padding:12px}
.panel{height:auto;padding:16px 14px}
h2{margin-bottom:15px;font-size:clamp(18px,5.2vw,25px)}
.summary{min-height:115px;gap:8px;align-items:flex-start}
.summary>strong{font-size:clamp(40px,12vw,54px)}
.summary img{right:0;top:-7px;width:clamp(82px,22vw,108px);height:clamp(82px,22vw,108px)}
.groups{grid-template-columns:1fr 1fr;gap:12px 14px}
.group h3{font-size:13px;margin-bottom:6px}
.group div{font-size:12px;line-height:1.4}
.group span{margin-left:6px}
.forecast{grid-template-columns:56px 44px minmax(0,1fr) auto;gap:6px;min-height:56px}
.forecast img{width:40px;height:40px}
.forecast>b{font-size:11px;line-height:1.25}
.forecast strong{font-size:12px}
.forecast small{font-size:9px}
.right{display:block;border:0}
.beach{min-height:400px;height:auto;padding:12px;border-bottom:2px solid}
.card{width:100%;height:auto;min-height:370px;padding:14px 12px}
.card h2{padding-right:75px;margin-bottom:9px;font-size:20px}
.card p{padding-right:65px;margin-bottom:16px;font-size:13px}
.beach-weather-icon{right:10px;top:9px;width:66px;height:66px}
.row{grid-template-columns:minmax(100px,42%) minmax(0,1fr);gap:6px;font-size:12px;line-height:1.45}
.nav{display:none}
}
</style>
</head>
<body>
<header style="position:fixed;z-index:10;top:0;left:0;width:100%;height:78px;padding:15px 28px;background:#f2f2f2;border-bottom:3px solid;display:flex;justify-content:space-between;align-items:center">
<b style="font-size:clamp(22px,2.4vw,44px)">The Fungalow <i style="font-weight:400;font-size:.7em">"Never not stop genieting"</i></b>
<span style="font-size:clamp(14px,1.5vw,28px)">DATE_PLACEHOLDER</span>
</header>
<div id="slides">SLIDES_PLACEHOLDER</div>
<div class="nav"><button onclick="go(-1)">‹</button><span id="n">1 / COUNT</span><button onclick="go(1)">›</button></div>
<script>
const slides=[...document.querySelectorAll(".slide")];
let i=0;
function show(){slides.forEach((x,n)=>x.classList.toggle("active",n===i));document.getElementById("n").textContent=(i+1)+" / "+slides.length}
function go(d){i=(i+d+slides.length)%slides.length;show()}
show();
if (!window.matchMedia("(max-width:800px)").matches) {
  setInterval(()=>go(1),5000);
}
</script>
</body></html>"""

    page = page.replace("DATE_PLACEHOLDER", esc(date_text))
    page = page.replace("SLIDES_PLACEHOLDER", "".join(slides))
    page = page.replace("COUNT", str(len(slides)))

    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write(page)

    print("HTML dashboard succesvol gemaakt:")
    print(os.path.abspath(OUTPUT))
    print(f"{len(slides)} slides, automatisch wisselen iedere 5 seconden.")

if __name__ == "__main__":
    main()
