import httpx

from app.config import (
    OPENWEATHER_API_KEY,
    OPENWEATHER_BASE_URL
)


async def get_current_weather(lat: float, lon: float):

    url = f"{OPENWEATHER_BASE_URL}/weather"

    params = {
        "lat": lat,
        "lon": lon,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric",
        "lang": "vi"
    }

    async with httpx.AsyncClient() as client:

        response = await client.get(
            url,
            params=params
        )

        response.raise_for_status()

        data = response.json()

        return data