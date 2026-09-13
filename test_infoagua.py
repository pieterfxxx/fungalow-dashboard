import requests
import re
import json
from config import BEACHES, FALLBACK_INFOAGUA_ID


def clean(text):
    text = re.sub(r"<.*?>", "", text)
    return " ".join(text.split()).strip()


def translate(text):
    # Officiële IPMA-weertypen die InfoÁgua gebruikt voor de dagelijkse
    # weersverwachting. Eerst de volledige uitdrukkingen, daarna eventuele
    # kortere losse varianten.
    translations = {
        # Algemene / ontbrekende informatie
        "---": "Niet beschikbaar",
        "Sem informação": "Geen informatie",

        # Bewolking
        "Céu limpo": "Helder",
        "Céu pouco nublado": "Licht bewolkt",
        "Céu parcialmente nublado": "Half bewolkt",
        "Céu muito nublado ou encoberto": "Zwaar bewolkt of betrokken",
        "Céu muito nublado": "Zwaar bewolkt",
        "Céu nublado por nuvens altas": "Bewolkt met hoge bewolking",
        "Céu com períodos de muito nublado": "Afwisselend bewolkt en zwaar bewolkt",
        "Céu nublado": "Bewolkt",
        "Períodos de céu muito nublado": "Perioden met zware bewolking",

        # Regen en buien
        "Aguaceiros/chuva fortes": "Zware buien en regen",
        "Aguaceiros/chuva fracos": "Lichte buien en regen",
        "Aguaceiros/chuva": "Buien en regen",
        "Chuva/aguaceiros forte": "Zware regen en buien",
        "Chuva/aguaceiros": "Regen en buien",
        "Períodos de chuva forte": "Perioden met zware regen",
        "Períodos de chuva fraca": "Perioden met lichte regen",
        "Períodos de chuva": "Perioden met regen",
        "Chuva fraca ou chuvisco": "Lichte regen of motregen",
        "Chuva fraca": "Lichte regen",
        "Chuva moderada": "Matige regen",
        "Chuva forte": "Zware regen",
        "Aguaceiros fracos": "Lichte buien",
        "Aguaceiros fortes": "Zware buien",
        "Aguaceiros": "Buien",
        "Chuva": "Regen",
        "Chuvisco": "Motregen",

        # Onweer
        "Aguaceiros e possibilidade de trovoada": "Buien met mogelijk onweer",
        "Chuva e possibilidade de trovoada": "Regen met mogelijk onweer",
        "Possibilidade de trovoada": "Mogelijk onweer",
        "Trovoada": "Onweer",

        # Overige officiële IPMA-weertypen
        "Neblina": "Nevel",
        "Nevoeiro ou nuvens baixas": "Mist of lage bewolking",
        "Nevoeiro": "Mist",
        "Neve": "Sneeuw",
        "Granizo": "Hagel",
        "Geada": "Vorst",
        "Nebulosidade convectiva": "Convectieve bewolking",
        "Aguaceiros de neve": "Sneeuwbuien",
        "Chuva e Neve": "Regen en sneeuw",

        # Golfstatus
        "fraco": "Rustig",
        "moderado": "Matig",
        "forte": "Sterk",

        # Waarschuwingen
        "Não existem Alertas ativos": "Geen actieve waarschuwingen",
        "Não existem alertas ativos": "Geen actieve waarschuwingen",
    }

    for portuguese, dutch in sorted(
        translations.items(),
        key=lambda item: len(item[0]),
        reverse=True
    ):
        text = re.sub(
            re.escape(portuguese),
            dutch,
            text,
            flags=re.IGNORECASE
        )

    # Netjes opruimen.
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\s*,\s*", ", ", text)
    return text.strip(" ,")


def get_value(html, class_name):
    pattern = (
        rf'<div class="item {re.escape(class_name)}.*?">'
        rf'.*?<div class="value">(.*?)</div>'
    )

    match = re.search(pattern, html, re.DOTALL)

    if match:
        return clean(match.group(1))

    return "Niet beschikbaar"


def get_data_from_id(infoagua_id):
    url = (
        "https://infoagua.apambiente.pt/pt/praias/praia-detalhe/"
        f"{infoagua_id}"
    )

    response = requests.get(
        url,
        timeout=20,
        headers={"User-Agent": "Mozilla/5.0"}
    )
    response.raise_for_status()

    html = response.text

    # Weer + minimum/maximum temperatuur
    weather_match = re.search(
        r'<div class="info simple-weather">(.*?)</div>\s*'
        r'<div class="info advanced-weather">',
        html,
        re.DOTALL
    )

    if weather_match:
        weather_text = clean(weather_match.group(1))
    else:
        weather_text = "Niet beschikbaar"

    water_temperature = get_value(html, "weather")
    wave_status = get_value(html, "waves-status")
    wave_height = get_value(html, "waves-height")

    alerts_match = re.search(
        r'<div class="alerts-list">\s*<div class="message">(.*?)</div>',
        html,
        re.DOTALL
    )

    if alerts_match:
        alerts = clean(alerts_match.group(1))
    else:
        alerts = "Niet beschikbaar"

    # Vertalen
    weather_text = translate(weather_text)

    # Alleen het weer-veld opschonen: een golfstatus hoort hier niet thuis.
    weather_text = re.sub(
        r"\b(?:fraco|moderado|forte|rustig\w*|matig\w*|sterk\w*)\b",
        "",
        weather_text,
        flags=re.IGNORECASE
    )
    weather_text = re.sub(r"\s+", " ", weather_text)
    weather_text = re.sub(r"\s*,\s*", ", ", weather_text).strip(" ,")

    # Deze velden mogen de statusvertaling juist behouden.
    wave_status = translate(wave_status)
    alerts = translate(alerts)

    # Temperaturen netjes formatteren
    weather_text = re.sub(
        r"(\d+(?:[.,]\d+)?)\s*[°º](?!C)",
        r"\1°C",
        weather_text
    )

    if water_temperature != "Niet beschikbaar":
        water_temperature = re.sub(
            r"\s*[°º]\s*(?:C)?",
            "",
            water_temperature,
            flags=re.IGNORECASE
        ).strip()
        water_temperature = f"{water_temperature}°C"

    return {
        "weather": weather_text,
        "water": water_temperature,
        "status": wave_status,
        "waves": wave_height,
        "warning": alerts,
    }


def get_beach_data(beach):
    try:
        return get_data_from_id(beach["infoagua_id"])

    except Exception as error:
        return {
            "weather": "Niet beschikbaar",
            "water": "Niet beschikbaar",
            "status": "Niet beschikbaar",
            "waves": "Niet beschikbaar",
            "warning": "Niet beschikbaar",
            "error": str(error),
        }


# Eerst de fallback-data van São Bernardino ophalen
try:
    fallback_data = get_data_from_id(FALLBACK_INFOAGUA_ID)
except Exception as error:
    fallback_data = {
        "weather": "Niet beschikbaar",
        "water": "Niet beschikbaar",
        "status": "Niet beschikbaar",
        "waves": "Niet beschikbaar",
        "warning": "Niet beschikbaar",
    }


# Daarna alle stranden ophalen
result = {}

for beach in BEACHES:
    beach_data = get_beach_data(beach)

    # Alleen ontbrekende waarden vervangen door de fallback van São Bernardino
    for key in ["weather", "water", "status", "waves", "warning"]:
        if beach_data.get(key) == "Niet beschikbaar":
            fallback_value = fallback_data.get(key, "Niet beschikbaar")

            if fallback_value != "Niet beschikbaar":
                beach_data[key] = f"~{fallback_value}"
            else:
                beach_data[key] = "Niet beschikbaar"

    result[beach["name"]] = beach_data


# Geldige JSON-output met alle 10 stranden
print(json.dumps(result, ensure_ascii=False, indent=2))