import os

HOME = {
    "name": "De Fungalow",
    "tagline": "Never not stop genieting",
    "lat": 39.2072543,
    "lon": -9.3159164,
}

BEACHES = [
    {
        "name": "Baleal Noord",
        "lat": 39.3740652,
        "lon": -9.3363481,
        "infoagua_id": "8979630740",
            "distance": "22,5 km",
        "drive": "26 min rijden",
},
    {
        "name": "Baleal Zuid",
        "lat": 39.3649046,
        "lon": -9.3434251,
        "infoagua_id": "8979629988",
            "distance": "22,3 km",
        "drive": "27 min rijden",
},
    {
        "name": "Supertubos",
        "lat": 39.3446740,
        "lon": -9.3628866,
        "infoagua_id": "8979629916",
            "distance": "20,8 km",
        "drive": "23 min rijden",
},
    {
        "name": "São Bernardino",
        "lat": 39.3111807,
        "lon": -9.3467045,
        "infoagua_id": "8979629982",
            "distance": "13,5 km",
        "drive": "18 min rijden",
},
    {
        "name": "Valmitão",
        "lat": 39.2010972,
        "lon": -9.3468292,
        "infoagua_id": "8979630202",
            "distance": "4,0 km",
        "drive": "6 min rijden",
},
    {
        "name": "Santa Rita Noord",
        "lat": 39.1723694,
        "lon": -9.3581049,
        "infoagua_id": "8979630346",
            "distance": "7,7 km",
        "drive": "11 min rijden",
},
    {
        "name": "Santa Cruz Centro",
        "lat": 39.1389198,
        "lon": -9.3800249,
        "infoagua_id": "8979630094",
            "distance": "12,9 km",
        "drive": "19 min rijden",
},
    {
    "name": "Praia do Peralta",
    "lat": 39.24520757260981,
    "lon": -9.340824603944416,
    "infoagua_id": "8979630090",
            "distance": "5,4 km",
        "drive": "8 min rijden",
},
    {
        "name": "Praia do Areal Sul",
        "lat": 39.2597241,
        "lon": -9.3372809,
        "infoagua_id": "8979630176",
            "distance": "8,4 km",
        "drive": "12 min rijden",
},
    {
        "name": "Porto Dinheiro",
        "lat": 39.2139722,
        "lon": -9.3444491,
        "infoagua_id": "8979630808",
            "distance": "3,3 km",
        "drive": "7 min rijden",
},
    {
        "name": "Lisboa",
        "lat": 38.7070278,
        "lon": -9.1348611,
        "infoagua_id": "8979630354",
            "distance": "70,7 km",
        "drive": "57 min rijden",
},
    {
        "name": "Nazaré",
        "lat": 39.6063056,
        "lon": -9.0848889,
        "infoagua_id": "8979630860",
            "distance": "75,9 km",
        "drive": "57 min rijden",
},
    {
        "name": "São Martinho do Porto",
        "lat": 39.5043056,
        "lon": -9.1381667,
        "infoagua_id": "9662972230",
            "distance": "59,9 km",
        "drive": "48 min rijden",
},
    {
        "name": "Foz do Arelho",
        "lat": 39.4301111,
        "lon": -9.2261111,
        "infoagua_id": "8979629866",
            "distance": "51,9 km",
        "drive": "42 min rijden",
},
]

BEACH_PAIRS = [
    ("Baleal Noord", "Baleal Zuid"),
    ("Supertubos", "São Bernardino"),
    ("Praia do Areal Sul", "Praia do Peralta"),
    ("Porto Dinheiro", "Valmitão"),
    ("Santa Rita Noord", "Santa Cruz Centro"),

    ("Lisboa", "Nazaré"),
    ("São Martinho do Porto", "Foz do Arelho"),
]

FALLBACK_INFOAGUA_ID = "8979629982"

TIDECHECK_API_KEY = os.environ.get("TIDECHECK_API_KEY", "")

# ============================================================
# DASHBOARD LAYOUT / FINETUNING
# Pas hier zelf eenvoudig het uiterlijk aan
# ============================================================

DASHBOARD_LAYOUT = {

    # --------------------------------------------------------
    # ALGEMEEN
    # --------------------------------------------------------

    "width": 1872,
    "height": 1404,
    "header_height": 110,

    "background": (238, 238, 238),
    "header_background": (244, 244, 244),

    "margin_left": 35,
    "margin_right": 35,

    "line_width": 2,


    # --------------------------------------------------------
    # KOLOMMEN
    # --------------------------------------------------------

    # Exact even breed
    "left_column_ratio": 0.50,
    "right_column_ratio": 0.50,


    # --------------------------------------------------------
    # LINKER KOLOM
    # --------------------------------------------------------

    # Hoogteverdeling
    "weather_ratio": 0.40,
    "forecast_ratio": 0.40,
    "tide_ratio": 0.20,

    # Kopjes
    "section_title_size": 48,
    "section_title_top": 20,

    # Huidig weer
    "temperature_size": 58,
    "weather_condition_size": 28,
    "weather_text_size": 24,

    "temperature_top": 100,
    "condition_x": 250,
    "condition_top": 115,

    "weather_info_top": 230,
    "weather_label_x": 35,
    "weather_value_x": 300,
    "weather_line_gap": 55,


    # --------------------------------------------------------
    # 3 DAGEN VOORUIT
    # --------------------------------------------------------

    "forecast_text_size": 24,

    "forecast_top": 105,
    "forecast_day_x": 35,
    "forecast_weather_x": 210,
    "forecast_right_margin": 45,
    "forecast_line_gap": 70,
    "forecast_detail_gap": 28,


    # --------------------------------------------------------
    # GETIJDEN
    # --------------------------------------------------------

    "tide_title_top": 20,
    "tide_graph_top": 85,

    # Hoeveel ruimte de grafiek maximaal mag gebruiken
    "tide_graph_margin_x": 90,
    "tide_graph_bottom_margin": 20,


    # --------------------------------------------------------
    # STRANDFOTO'S
    # --------------------------------------------------------

    # Hoger = lichtere foto
    "beach_brightness": 2.35,

    # Lager = rustiger / minder contrast
    "beach_contrast": 0.58,

    # Extra witte laag over de foto
    # 0 = geen, 255 = volledig wit
    "beach_white_overlay": 45,


    # --------------------------------------------------------
    # STRANDTEKST
    # --------------------------------------------------------

    "beach_title_size": 48,
    "beach_distance_size": 30,
    "beach_label_size": 29,
    "beach_value_size": 29,

    "beach_text_left": 55,

    "beach_title_top": 35,
    "beach_distance_top": 110,

    "beach_info_top": 180,

    "beach_value_x": 300,
    "beach_info_gap": 65,

    # Dikke witte rand rond zwarte tekst
    "beach_text_stroke": 5,


    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    "title_size": 44,
    "tagline_size": 24,
    "date_size": 28,

    "title_x": 35,
    "title_y": 25,

    "tagline_gap": 30,

    "date_y": 39,
}