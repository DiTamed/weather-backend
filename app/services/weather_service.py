import httpx

from app.config import OPEN_METEO_BASE_URL


# ==========================================
# CURRENT WEATHER
# ==========================================

async def get_current_weather(lat: float, lon: float):

    params = {
        "latitude": lat,
        "longitude": lon,

        "current": ",".join([
            "temperature_2m",
            "relative_humidity_2m",
            "apparent_temperature",
            "precipitation",
            "weather_code",
            "wind_speed_10m"
        ]),

        "timezone": "auto"
    }

    async with httpx.AsyncClient(timeout=10.0) as client:

        response = await client.get(
            OPEN_METEO_BASE_URL,
            params=params
        )

        response.raise_for_status()

        return response.json()


# ==========================================
# 7 DAYS BEFORE + TODAY + 7 DAYS AFTER
# ==========================================

async def get_weather_15_days(lat: float, lon: float):

    params = {
        "latitude": lat,
        "longitude": lon,

        # 7 ngày trước
        "past_days": 7,

        # Hôm nay + 7 ngày sau
        "forecast_days": 8,

        "daily": ",".join([

            # Weather
            "weather_code",

            # Temperature
            "temperature_2m_max",
            "temperature_2m_min",

            # Feels like
            "apparent_temperature_max",
            "apparent_temperature_min",

            # Humidity
            "relative_humidity_2m_mean",

            # Rain
            "precipitation_sum",
            "rain_sum",
            "precipitation_probability_max",

            # Wind
            "wind_speed_10m_max"
        ]),

        "timezone": "auto"
    }

    async with httpx.AsyncClient(timeout=15.0) as client:

        response = await client.get(
            OPEN_METEO_BASE_URL,
            params=params
        )

        response.raise_for_status()

        return response.json()