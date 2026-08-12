import asyncio
import httpx

from app.config import OPEN_METEO_BASE_URL


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

    async with httpx.AsyncClient(
        timeout=15.0
    ) as client:

        for attempt in range(3):

            response = await client.get(
                OPEN_METEO_BASE_URL,
                params=params
            )

            print(
                "OPEN-METEO CURRENT STATUS:",
                response.status_code
            )

            # =========================
            # RATE LIMIT
            # =========================

            if response.status_code == 429:

                if attempt < 2:

                    print(
                        "Open-Meteo rate limit. "
                        "Retry after 10 seconds..."
                    )

                    await asyncio.sleep(10)

                    continue

                raise Exception(
                    "Open-Meteo đang giới hạn request (429). "
                    "Vui lòng thử lại sau."
                )

            response.raise_for_status()

            return response.json()

        raise Exception(
            "Không thể lấy dữ liệu Open-Meteo."
        )


async def get_weather_15_days(
    lat: float,
    lon: float
):

    params = {
        "latitude": lat,
        "longitude": lon,

        "past_days": 7,

        "forecast_days": 8,

        "daily": ",".join([
            "weather_code",

            "temperature_2m_max",
            "temperature_2m_min",

            "apparent_temperature_max",
            "apparent_temperature_min",

            "relative_humidity_2m_mean",

            "precipitation_sum",
            "rain_sum",
            "precipitation_probability_max",

            "wind_speed_10m_max"
        ]),

        "timezone": "auto"
    }

    async with httpx.AsyncClient(
        timeout=15.0
    ) as client:

        for attempt in range(3):

            response = await client.get(
                OPEN_METEO_BASE_URL,
                params=params
            )

            print(
                "OPEN-METEO 15 DAYS STATUS:",
                response.status_code
            )

            if response.status_code == 429:

                if attempt < 2:

                    print(
                        "Open-Meteo rate limit. "
                        "Retry after 10 seconds..."
                    )

                    await asyncio.sleep(10)

                    continue

                raise Exception(
                    "Open-Meteo đang giới hạn request (429). "
                    "Vui lòng thử lại sau."
                )

            response.raise_for_status()

            return response.json()

        raise Exception(
            "Không thể lấy dữ liệu Open-Meteo."
        )