#weather.py
import requests
from datetime import datetime
from typing import Dict, Optional


# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------

def c_to_warmth(temp: float) -> str:
    if temp >= 24:
        return "caluroso"
    elif temp >= 15:
        return "medio"
    return "frio"


def weather_code_to_rain(main_weather: str) -> bool:
    if not main_weather:
        return False
    return main_weather.lower() in ["rain", "drizzle", "thunderstorm"]


def safe_day_name(dt_txt: str) -> str:
    """
    Convierte una fecha tipo '2026-03-17 12:00:00' a nombre del día en español.
    """
    dt = datetime.strptime(dt_txt, "%Y-%m-%d %H:%M:%S")
    days_map = {
        "Monday": "Lunes",
        "Tuesday": "Martes",
        "Wednesday": "Miércoles",
        "Thursday": "Jueves",
        "Friday": "Viernes",
        "Saturday": "Sábado",
        "Sunday": "Domingo",
    }
    return days_map[dt.strftime("%A")]


def weather_icon(weather_info: Optional[dict]) -> str:
    if not weather_info:
        return "❔"

    if weather_info.get("rain"):
        return "🌧️"

    desc = str(weather_info.get("description", "")).lower()

    if "nube" in desc or "cloud" in desc:
        return "☁️"
    if "sol" in desc or "clear" in desc or "despejado" in desc:
        return "☀️"

    return "⛅"


# ---------------------------------------------------------
# CLIMA ACTUAL
# ---------------------------------------------------------

def get_current_weather(city: str, api_key: str) -> Optional[dict]:
    """
    Devuelve clima actual para una ciudad.
    """
    if not city or not api_key or api_key == "TU_API_KEY_AQUI":
        return None

    try:
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": city,
            "appid": api_key,
            "units": "metric",
            "lang": "es"
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        temp = data["main"]["temp"]
        weather_main = data["weather"][0]["main"]
        description = data["weather"][0].get("description", "sin datos")

        return {
            "temp": round(temp),
            "rain": weather_code_to_rain(weather_main),
            "description": description,
            "warmth": c_to_warmth(temp),
            "raw": data
        }

    except Exception as e:
        print(f"Error obteniendo clima actual: {e}")
        return None


# ---------------------------------------------------------
# PRONÓSTICO SEMANAL
# ---------------------------------------------------------

def get_week_forecast(city: str, api_key: str) -> Dict[str, dict]:
    """
    Obtiene pronóstico de 5 días / 3 horas de OpenWeather
    y devuelve un dict por nombre de día en español.

    Ejemplo:
    {
        "Lunes": {"temp": 12, "rain": True, "description": "lluvia ligera", "warmth": "frio"},
        "Martes": {...}
    }
    """
    if not city or not api_key or api_key == "TU_API_KEY_AQUI":
        return {}

    try:
        url = "https://api.openweathermap.org/data/2.5/forecast"
        params = {
            "q": city,
            "appid": api_key,
            "units": "metric",
            "lang": "es"
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        forecast_list = data.get("list", [])
        if not forecast_list:
            return {}

        grouped = {}

        for item in forecast_list:
            dt_txt = item["dt_txt"]
            day_name = safe_day_name(dt_txt)

            hour = int(dt_txt.split(" ")[1].split(":")[0])
            temp = item["main"]["temp"]
            weather_main = item["weather"][0]["main"]
            description = item["weather"][0].get("description", "sin datos")

            entry = {
                "hour": hour,
                "temp": round(temp),
                "rain": weather_code_to_rain(weather_main),
                "description": description,
                "warmth": c_to_warmth(temp),
            }

            grouped.setdefault(day_name, []).append(entry)

        result = {}

        for day_name, entries in grouped.items():
            chosen = min(entries, key=lambda x: abs(x["hour"] - 12))
            result[day_name] = {
                "temp": chosen["temp"],
                "rain": chosen["rain"],
                "description": chosen["description"],
                "warmth": chosen["warmth"],
            }

        return result

    except Exception as e:
        print(f"Error obteniendo pronóstico semanal: {e}")
        return {}


# ---------------------------------------------------------
# FORMATEO PARA UI
# ---------------------------------------------------------

def format_weather_label(weather_info: Optional[dict]) -> str:
    if not weather_info:
        return "Sin pronóstico"

    icon = weather_icon(weather_info)
    temp = weather_info.get("temp", "?")
    desc = weather_info.get("description", "sin datos")

    return f"{icon} {temp}°C · {desc}"